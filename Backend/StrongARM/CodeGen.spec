// CodeGen.spec, created Tue Jul 6 12:12:41 1999 by pnkfelix
// Copyright (C) 1999 Felix S. Klock II <pnkfelix@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Backend.StrongARM;

import harpoon.ClassFile.HClass;
import harpoon.ClassFile.HCodeElement;
import harpoon.ClassFile.HMethod;
import harpoon.IR.Assem.Instr;
import harpoon.IR.Assem.InstrEdge;
import harpoon.IR.Assem.InstrMEM;
import harpoon.IR.Assem.InstrJUMP;
import harpoon.IR.Assem.InstrMOVE;
import harpoon.IR.Assem.InstrCALL;
import harpoon.IR.Assem.InstrLABEL;
import harpoon.IR.Assem.InstrDIRECTIVE;
import harpoon.IR.Assem.InstrFactory;
import harpoon.IR.Tree.TreeDerivation;
import harpoon.IR.Tree.Bop;
import harpoon.IR.Tree.Uop;
import harpoon.IR.Tree.Type;
import harpoon.IR.Tree.TEMP;
import harpoon.IR.Tree.Typed;
import harpoon.IR.Tree.PreciselyTyped;
import harpoon.IR.Tree.ExpList;
import harpoon.Util.Util;
import harpoon.Temp.TempList;
import harpoon.Temp.Temp;
import harpoon.Temp.LabelList;
import harpoon.Temp.Label;

import harpoon.IR.Tree.BINOP;
import harpoon.IR.Tree.CALL;
import harpoon.IR.Tree.INVOCATION;
import harpoon.IR.Tree.CJUMP;
import harpoon.IR.Tree.CONST;
import harpoon.IR.Tree.EXP;
import harpoon.IR.Tree.JUMP;
import harpoon.IR.Tree.LABEL;
import harpoon.IR.Tree.MEM;
import harpoon.IR.Tree.MOVE;
import harpoon.IR.Tree.NAME;
import harpoon.IR.Tree.NATIVECALL;
import harpoon.IR.Tree.OPER;
import harpoon.IR.Tree.RETURN;
import harpoon.IR.Tree.TEMP;
import harpoon.IR.Tree.UNOP;
import harpoon.IR.Tree.SEQ;

import harpoon.Util.Collections.MultiMap;
import harpoon.Util.Collections.GenericMultiMap;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Set;
import java.util.HashSet;
import java.util.Map;
import java.util.HashMap;
import java.util.Iterator;

/**
 * <code>StrongARM.CodeGen</code> is a code-generator for the ARM architecture.
 * 
 * @see Jaggar, <U>ARM Architecture Reference Manual</U>
 * @author  Felix S. Klock II <pnkfelix@mit.edu>
 * @version $Id: CodeGen.spec,v 1.1.2.137 2000-02-18 07:33:49 pnkfelix Exp $
 */
// NOTE THAT the StrongARM actually manipulates the DOUBLE type in quasi-
// big-endian (45670123) order.  To keep things simple, the 'low' temp in
// a two-word temp representing a double represents the MSB, and the 'high'
// temp the LSB.  This makes sure that the parameter-passing order is
// correct, even if we don't know whether a given two-word-temp is LONG or
// double.  See the CONST rules for some more oddity related to this quirk.
%%


    // InstrFactory to generate Instrs from
    private InstrFactory instrFactory;
    

    /*final*/ RegFileInfo regfile;
    private Temp r0, r1, r2, r3, r4, r5, r6, FP, IP, SP, LR, PC;
    Comparator regComp;

    // whether to generate stabs debugging information in output (-g flag)
    private static final boolean stabsDebugging=true;

    public CodeGen(Frame frame) {
	super(frame);
	last = null;
	this.regfile = (RegFileInfo) frame.getRegFileInfo();
	r0 = regfile.reg[0];
	r1 = regfile.reg[1];
	r2 = regfile.reg[2];
	r3 = regfile.reg[3];
	r4 = regfile.reg[4];
	r5 = regfile.reg[5];
	r6 = regfile.reg[6];
	FP = regfile.FP; // reg 11
	IP = regfile.reg[12];
	SP = regfile.SP; // reg 13
	LR = regfile.LR; // reg 14
	PC = regfile.PC; // reg 15
	// allow sorting of registers so that stm and ldm work correctly.
	final Map regToNum = new HashMap();
	for (int i=0; i<regfile.reg.length; i++)
	    regToNum.put(regfile.reg[i], new Integer(i));
	regComp = new Comparator() {
	    public int compare(Object o1, Object o2) {
		Util.assert(regToNum.keySet().contains(o1),
			    o1+" not in regToNum's keys");
		Util.assert(regToNum.keySet().contains(o2),
			    o2+" not in regToNum's keys");
		return ((Integer)regToNum.get(o1)).intValue() -
		       ((Integer)regToNum.get(o2)).intValue();
	    }
	};
    }


    /** The main Instr layer; nothing below this line should call
	emit(Instr) directly, unless they are constructing extensions
	of Instr.
    */
    private Instr emit(HCodeElement root, String assem,
		      Temp[] dst, Temp[] src,
		      boolean canFallThrough, List targets) {
	return emit(new Instr( instrFactory, root, assem,
			dst, src, canFallThrough, targets));
    }		      

    /** Secondary emit layer; for primary usage by the other emit
	methods. 
    */
    private Instr emit2(HCodeElement root, String assem,
		      Temp[] dst, Temp[] src) {
	return emit(root, assem, dst, src, true, null);
    }

    /** Single dest Single source Emit Helper. */
    private Instr emit( HCodeElement root, String assem, 
		       Temp dst, Temp src) {
	return emit2(root, assem, new Temp[]{ dst }, new Temp[]{ src });
    }
    

    /** Single dest Two source Emit Helper. */
    private Instr emit( HCodeElement root, String assem, 
		       Temp dst, Temp src1, Temp src2) {
	return emit2(root, assem, new Temp[]{ dst },
			new Temp[]{ src1, src2 });
    }

    /** Null dest Null source Emit Helper. */
    private Instr emit( HCodeElement root, String assem ) {
	return emit2(root, assem, null, null);
    }

    /** Single dest Single source emit InstrMOVE helper */
    private Instr emitMOVE( HCodeElement root, String assem,
			   Temp dst, Temp src) {
	return emit(new InstrMOVE( instrFactory, root, assem+" @move",
			    new Temp[]{ dst },
			    new Temp[]{ src }));
    }			         

    /* Branching instruction emit helper. 
       Instructions emitted using this *can* fall through.
    */
    private Instr emit( HCodeElement root, String assem,
		       Temp[] dst, Temp[] src, Label[] targets ) {
        return emit(new Instr( instrFactory, root, assem,
			dst, src, true, Arrays.asList(targets)));
    }
    
    /* Branching instruction emit helper. 
       Instructions emitted using this *cannot* fall through.
    */
    private Instr emitNoFall( HCodeElement root, String assem,
		       Temp[] dst, Temp[] src, Label[] targets ) {
        return emit(new Instr( instrFactory, root, assem,
			dst, src, false, Arrays.asList(targets)));
    }

    /* Call instruction emit helper. 
       Instructions emitted using this *cannot* fall through.
    */
    private Instr emitCallNoFall( HCodeElement root, String assem,
		       Temp[] dst, Temp[] src, Label[] targets ) {
	List tlist = (targets==null?null:Arrays.asList(targets));
        return emit(new InstrCALL( instrFactory, root, assem,
				   dst, src, false, tlist));
    }

    private Instr emitNativeCall( HCodeElement root, String assem,
				  Temp[] dst, Temp[] src, 
				  boolean canFall, Label[] targets) {
	List tlist = (targets==null?null:Arrays.asList(targets));
	return emit(new InstrCALL( instrFactory, root, assem,
				   dst, src, canFall, tlist));
    }

    /* InstrJUMP emit helper; automatically adds entry to
       label->branches map. */ 
    private Instr emitJUMP( HCodeElement root, String assem, Label l ) {
	Instr j = emit( new InstrJUMP( instrFactory, root, assem, l ));
	return j;
    }

    /* InstrLABEL emit helper. */
    private Instr emitLABEL( HCodeElement root, String assem, Label l ) {
	return emit( new InstrLABEL( instrFactory, root, assem, l ));
    }	
    /* InstrLABEL emit helper. */
    private Instr emitNoFallLABEL( HCodeElement root, String assem, Label l ) {
	return emit( InstrLABEL.makeNoFall( instrFactory, root, assem, l ));
    }	

    /* InstrDIRECTIVE emit helper. */
    private Instr emitDIRECTIVE( HCodeElement root, String assem ) {
	return emit( new InstrDIRECTIVE( instrFactory, root, assem ));
    }
    /* InstrDIRECTIVE emit helper. */
    private Instr emitNoFallDIRECTIVE( HCodeElement root, String assem ) {
	return emit( InstrDIRECTIVE.makeNoFall( instrFactory, root, assem ));
    }

    private Temp makeTemp() {
	    return new Temp(instrFactory.tempFactory());
    }

    private TwoWordTemp makeTwoWordTemp() {
	    return new TwoWordTemp(instrFactory.tempFactory());
    }

    Map origTempToNewTemp;

    private Temp makeTemp( Temp orig ) {
	    Temp newT = (Temp) origTempToNewTemp.get(orig);
	    if (newT == null) {
	    	newT = makeTemp();
		origTempToNewTemp.put(orig, newT);
	    }	
	    return newT;
    }

    private TwoWordTemp makeTwoWordTemp( Temp orig ) {
	    TwoWordTemp newT = (TwoWordTemp) origTempToNewTemp.get(orig);
	    if (newT == null) {
	    	newT = makeTwoWordTemp();
		origTempToNewTemp.put(orig, newT);
	    }	
	    return newT;
    }

    // helper for predicate clauses
    private boolean is12BitOffset(long val) {
	// addressing mode two takes a 12 bit unsigned offset, with
	// an additional bit in the instruction word indicating whether
	// to add or subtract this offset.  This means that there
	// are two representations for zero offset: +0 and -0.
	long absval = (val<0)?-val:val;
	return (absval&(~0xFFF))==0;
    }
    private boolean is12BitOffset(Number n) {
	if (n instanceof Double || n instanceof Float) return false;
	else return is12BitOffset(n.longValue());
    }
    // helper for operand2 shifts
    private boolean is5BitShift(long val) {
	return (val>=0) && (val<=31);
    }
    private boolean is5BitShift(Number n) {
	if (n instanceof Double || n instanceof Float) return false;
	else return is5BitShift(n.longValue());
    }
    private boolean isShiftOp(int op) {
	switch (op) {
	case Bop.SHL: case Bop.SHR: case Bop.USHR: return true;
	default: return false;
	}
    }
    private String shiftOp2Str(int op) {
	switch (op) {
	case Bop.SHL: return "lsl";
	case Bop.SHR: return "asr";
	case Bop.USHR: return "lsr";
	default: throw new Error("Illegal shift operation");
	}
    }
    // helper for comparison operations
    private boolean isCmpOp(int op) {
	switch (op) {
	case Bop.CMPEQ:
	case Bop.CMPGT: case Bop.CMPGE:
	case Bop.CMPLT: case Bop.CMPLE: return true;
	default: return false;
	}
    }
    private String cmpOp2Str(int op) {
	switch (op) {
	case Bop.CMPEQ: return "eq";
	case Bop.CMPGT: return "gt";
	case Bop.CMPGE: return "ge";
	case Bop.CMPLE: return "le";
	case Bop.CMPLT: return "lt";
	default: throw new Error("Illegal compare operation");
	}
    }
    // helper for operand2 immediates
    private boolean isOpd2Imm(Number n) {
	if (!(n instanceof Integer)) return false;
	else return isOpd2Imm(n.intValue());
    }
    private boolean isOpd2Imm(int val) {
	return (steps(val)<=1);
    }
    private int negate(Number n) {
	return -((Integer)n).intValue();
    }
    // helper for outputting constants
    private String loadConst32(String reg, int val, String humanReadable) {
	StringBuffer sb=new StringBuffer();
	String MOV="mov ", ADD="add ";
	// sometimes it is easier to load the complement of the number.
	boolean invert = (steps(~val) < steps(val));
	if (invert) { val=~val; MOV="mvn "; ADD="sub "; }
	// continue until there are no more bits to load...
	boolean first=true;
	while (val!=0) {
	  // get next eight-bit chunk (shift amount has to be even)
	  int eight = val & (0xFF << ((Util.ffs(val)-1) & ~1));
	  if (first) {
	    first=false;
	    sb.append(MOV+reg+", #"+eight+
		      " @ loading constant "+humanReadable);
	  } else
	    sb.append("\n"+ADD+reg+", "+reg+", #"+eight);
	  // zero out the eight bit chunk we just loaded, and continue.
	  val ^= eight;
	}
	if (first) return MOV+reg+", #0 @ loading constant "+humanReadable;
	else return sb.toString();
    }
    /* returns the number of instructions it will take to load the
     * specified constant. */
    private int steps(int v) {
	int r=0;
	for ( ; v!=0; r++)
	   v &= ~(0xFF << ((Util.ffs(v)-1) & ~1));
	return r;
    }

    /** simple tuple class to wrap some bits of info about the call prologue */
    private class CallState {
      /** number of parameter bytes pushed on to the stack. */
      final int stackOffset;
      /** set of registers used by parameters to the call. */
      final List callUses;
      CallState(int stackOffset, List callUses) {
	this.stackOffset=stackOffset; this.callUses=callUses;
      }
      /** Append a stack-offset instruction to the actual call.
       *  We delay the stack-offset to the point where it is
       *  atomic with the call, so that the register allocator
       *  can't insert spill code between the stack adjustment
       *  and the call. (the spill code would fail horribly in
       *  that case, because the stack pointer won't be where it
       *  expects it to be.) */
      String prependSPOffset(String asmString) {
	// optimize for common case.
	if (stackOffset==0) return asmString;
	return "sub sp, sp, #"+stackOffset+"\n\t"+asmString;
      }
    }

    private List buildTypeHCs(INVOCATION ROOT, TreeDerivation td) {
	Iterator iter = ExpList.iterator(ROOT.getArgs());
	List l = new ArrayList();
	while(iter.hasNext()) {
	    l.add(td.typeMap( (harpoon.IR.Tree.Exp) iter.next() ));
	}
	return l;
    } 
    /** Helper for setting up registers/memory with the strongARM standard
     *  calling convention.  Returns the stack offset necessary,
     *  along with a set of registers used by the parameters. */
    private CallState emitCallPrologue(INVOCATION ROOT, 
				       TempList list,
				       List typeHCs) {
	/** OUTPUT ARGUMENT ASSIGNMENTS IN REVERSE ORDER **/
      List callUses = new ArrayList(6);
      int stackOffset = 0;
      // reverse list and count # of words required
      TempList reverse=null;
      int index=0;
      int tind = 0;
      for(TempList tl=list; tl!=null; tl=tl.tail) {
	  reverse=new TempList(tl.head, reverse);
	  index+=(tl.head instanceof TwoWordTemp) ? 2 : 1;
	  tind++;
      }
      // add all registers up to and including r3 to callUses list.
      for (int i=0; i<index && i<4; i++)
	callUses.add(frame.getRegFileInfo().getRegister(i));
      index--; // so index points to 'register #' of last argument.

      declare( SP, HClass.Void ); // don't screw with the stack
      for (TempList tl = reverse; tl != null; tl = tl.tail) { 
	Temp temp = tl.head; tind--;
	if (temp instanceof TwoWordTemp) {
	  // arg takes up two words
	  switch(index) {
	  case 0: throw new Error("Not enough space!");
	  case 1: case 2: case 3: // put in registers 
	    // not certain an emitMOVE is legal with the l/h modifiers
	    Temp rfirst = frame.getRegFileInfo().getRegister(index--);
	    declare(rfirst, HClass.Void);
	    Temp rsecnd = frame.getRegFileInfo().getRegister(index--);
	    declare(rsecnd, HClass.Void);
	    emit( ROOT, "mov `d0, `s0h", rfirst, temp );
	    emit( ROOT, "mov `d0, `s0l", rsecnd, temp );
	    break;			     
	  case 4: // spread between regs and stack
	    stackOffset += 4; index--;
	    emit(new InstrMEM( instrFactory, ROOT,
			       "str `s0h, [`s1, #-"+stackOffset+"]",
			       new Temp[]{ SP }, // SP *implicitly* modified
			       new Temp[]{ temp, SP })); 
	    // not certain an emitMOVE is legal with the l/h modifiers
	    Temp rthird = frame.getRegFileInfo().getRegister(index--);
	    declare( rthird, HClass.Void );
	    emit( ROOT, "mov `d0, `s0l", rthird, temp );
	    break;
	  default: // start putting args in memory
	    stackOffset += 4; index--;
	    emit(new InstrMEM( instrFactory, ROOT,
			       "str `s0h, [`s1, #-"+stackOffset+"]",
			       new Temp[]{ SP }, // SP *implicitly* modified
			       new Temp[]{ temp, SP })); 
	    stackOffset += 4; index--;
	    emit(new InstrMEM( instrFactory, ROOT,
			       "str `s0l, [`s1, #-"+stackOffset+"]", 
			       new Temp[] { SP }, // SP *implicitly* modified 
			       new Temp[]{ temp, SP }));
	    break;
	  }
	} else {
	  // arg is one word
	  if (index < 4) {
	    Temp reg = frame.getRegFileInfo().getRegister(index--); 
	    declare( reg, (HClass) typeHCs.get(tind));
	    emitMOVE( ROOT, "mov `d0, `s0", reg, temp);
	  } else {
	    stackOffset += 4; index--;
	    emit(new InstrMEM(
			      instrFactory, ROOT,
			      "str `s0, [`s1, #-"+stackOffset+"]",
			      new Temp[]{ SP }, // SP *implicitly* modified
			      new Temp[]{ temp, SP }));
	  }
	}
      }
      Util.assert(index==-1);
      return new CallState(stackOffset, callUses);
    }
    /** Make a handler stub. */
    private void emitHandlerStub(INVOCATION ROOT, Temp retex, Label handler) {
	declare( retex, frame.getLinker().forName("java.lang.Throwable"));
	emitMOVE ( ROOT, "mov `d0, `s0", retex, r0 );
	emitJUMP ( ROOT, "b "+handler, handler);
    }
    /** Emit a fixup table entry */
    private void emitCallFixup(INVOCATION ROOT, Label retaddr, Label handler) {
      // this '1f' and '1:' business is taking advantage of a GNU
      // Assembly feature to avoid polluting the global name space with
      // local labels
      // these may need to be included in the previous instr to preserve
      // ordering semantics, but for now this way they indent properly
      emitDIRECTIVE( ROOT, ".text 10\t@.section fixup");
      emitDIRECTIVE( ROOT, "\t.word "+retaddr+", "+handler+" @ (retaddr, handler)");
      emitDIRECTIVE( ROOT, ".text 0 \t@.section code");
    }
    /** Finish up a CALL or NATIVECALL. */
    private void emitCallEpilogue(INVOCATION ROOT,
				  Temp retval, HClass type, 
				  CallState cs) {
      // this will break if stackOffset > 255 (ie >63 args)
      Util.assert( cs.stackOffset < 256, 
		   "Update the spec file to handle large SP offsets");
      if (cs.stackOffset!=0) // optimize for common case.
	  emit( ROOT, "add `d0, `s0, #" + cs.stackOffset, SP , SP );
      if (ROOT.getRetval()==null) {
	  // this is a void method.  don't bother to emit move.
      } else if (ROOT.getRetval().isDoubleWord()) {
	retval = makeTwoWordTemp(retval);
	// not certain an emitMOVE is legal with the l/h modifiers

	declare(retval, type);
	emit( ROOT, "mov `d0l, `s0", retval, r0 );
	emit( ROOT, "mov `d0h, `s0", retval, r1 );
      } else {
	retval = makeTemp(retval);
	declare(retval, type);
	emitMOVE( ROOT, "mov `d0, `s0", retval, r0 );
      }  
    }

    // Mandated by CodeGen generic class: perform entry/exit
    public Instr procFixup(HMethod hm, Instr instr,
			   int stackspace, Set usedRegisters) {
	InstrFactory inf = instrFactory; // convenient abbreviation.
	Label methodlabel = frame.getRuntime().nameMap.label(hm);
	// make list of callee-save registers we gotta save.
	StringBuffer reglist = new StringBuffer();

	Temp[] usedRegArray =
	    (Temp[]) usedRegisters.toArray(new Temp[usedRegisters.size()]);
	Collections.sort(Arrays.asList(usedRegArray), regComp);
	int nregs=0;
	for (int i=0; i<usedRegArray.length; i++) {
	    Temp rX = usedRegArray[i];
	    Util.assert(regfile.isRegister(rX));
	    if (rX.equals(r0)||rX.equals(r1)||rX.equals(r2)||rX.equals(r3))
		continue; // caller save registers.
	    if (rX.equals(LR)||rX.equals(PC)||rX.equals(FP)||rX.equals(SP)||
		rX.equals(IP)) continue; // always saved.
	    reglist.append(rX.toString());
	    reglist.append(", "); 
	    nregs++;
	}
	// find method entry/exit stubs
	Instr last=instr;
	for (Instr il = instr; il!=null; il=il.getNext()) {
	    if (il instanceof InstrENTRY) { // entry stub.
		Instr in1 = new InstrDIRECTIVE(inf, il, ".balign 4");
		Instr in2 = new InstrDIRECTIVE(inf, il, ".global " +
					       methodlabel.name);
		Instr in2a= new InstrDIRECTIVE(inf, il, ".type " +
					       methodlabel.name+",#function");
		Instr in3 = new InstrLABEL(inf, il, methodlabel.name+":",
					   methodlabel);
		Instr in4 = new Instr(inf, il, "mov ip, sp", null, null);
		Instr in5 = new Instr(inf, il,
				      "stmfd sp!, {"+reglist+"fp,ip,lr,pc}",
				      null, null);
		Instr in6 = new Instr(inf, il, "sub fp, ip, #4", null, null);
		
		String assem;
		if (harpoon.Backend.StrongARM.
		    Code.isValidConst(stackspace*4)) {
		    assem = "sub sp, sp, #"+(stackspace*4);
		} else {
		    assem="";
		    int op2 = stackspace *4;
		    while(op2 != 0) {
			// FSK: trusting CSA's code from CodeGen here...
			int eight = op2 & (0xFF << ((Util.ffs(op2)-1) & ~1));
			assem += "sub sp, sp, #"+eight;
			op2 ^= eight;
			if (op2!=0) assem += "\n";		
		    }
		}
		Instr in7 = new Instr(inf, il, assem, null, null);
		in7.layout(il, il.getNext());
		in6.layout(il, in7);
		in5.layout(il, in6);
		in4.layout(il, in5);
		in3.layout(il, in4);
		in2a.layout(il,in3);
		in2.layout(il, in2a);
		in1.layout(il, in2);
		if (il==instr) instr=in1; // fixup root if necessary.
		if (stackspace==0) in7.remove(); // optimize
		il.remove(); il=in1;
	    }
	    if (il instanceof InstrEXIT) { // exit stub
		Instr in1 = new Instr(inf, il,
				"ldmea fp, {"+reglist+"fp, sp, pc}",
				 null, null);
		in1.layout(il.getPrev(), il);
		il.remove(); il=in1;
	    }
	    last=il;
	}
	// add a size directive to the end of the function to let gdb
	// know how long it is.
	if (last!=null) { // best be safe.
	    Instr in1 = new InstrDIRECTIVE(inf, last, "\t.size " +
					   methodlabel.name + ", . - " +
					   methodlabel.name);
	    in1.layout(last, last.getNext());
	    last=in1;
	}
	// stabs debugging information:
	if (stabsDebugging && !hm.getDeclaringClass().isArray()) {
	    int lineno=-1;
	    for (Instr il = instr; il!=null; il=il.getNext())
		if (il.getLineNumber()!=lineno) {
		    lineno = il.getLineNumber();
		    Instr in1 = new InstrDIRECTIVE(inf, il, // line number
						   "\t.stabd 68,0,"+lineno);
		    in1.layout(il.getPrev(), il);
		    if (il==instr) instr=in1;
		}
	    Instr in1 = new InstrDIRECTIVE(inf, instr, // source path
					   "\t.stabs \""+
					   hm.getDeclaringClass().getPackage()
					   .replace('.','/')+"/"+
					   "\",100,0,0,"+methodlabel.name);
	    Instr in2 = new InstrDIRECTIVE(inf, instr, // source file name
					   "\t.stabs \""+instr.getSourceFile()+
					   "\",100,0,0,"+methodlabel.name);
	    Instr in3 = new InstrDIRECTIVE(inf, instr, // define void type
					   "\t.stabs \"void:t19=19\",128,0,0,0"
					   );
	    Instr in4 = new InstrDIRECTIVE(inf, instr, // mark as function
					   "\t.stabs \""+
					   methodlabel.name.substring(1)+":F19"
					   +"\",36,0,"+(nregs*4)+","+
					   methodlabel.name);
	    in1.layout(instr.getPrev(), instr);
	    in2.layout(in1, instr);
	    in3.layout(in2, instr);
	    instr = in1;
	    in4.layout(last, last.getNext());
	    last = in4;
	}
	return instr;
    }

    // now define our little InstrENTRY and InstrEXIT sub-types.
    private static class InstrENTRY extends InstrDIRECTIVE {
	public InstrENTRY(InstrFactory inf, HCodeElement src) {
	    super(inf, src, "@ --method entry point--");
	}
    }
    private class InstrEXIT extends Instr {
	public InstrEXIT(InstrFactory inf, HCodeElement hce) {
	    // uses SP and PC making them live in whole
	    // procedure (so register allocator doesn't stomp
	    // on them!)
	    super(inf, hce, "@ --method exit point--", null, 
		  new Temp[]{ SP, PC }, false, null);
	}
    }
%%
%start with %{
       // initialize state variables each time gen() is called
       first = null; last = null;
       origTempToNewTemp = new HashMap();
       this.instrFactory = inf;

}%
%end with %{
       // *** METHOD EPILOGUE *** 

}%
    /* this comment will be eaten by the .spec processor (unlike comments above) */
	
/* EXPRESSIONS */ 
BINOP<p,i>(ADD, j, k) = i
%{
    emit( ROOT, "add `d0, `s0, `s1", i, j, k);
}%
BINOP<p,i>(ADD, j, CONST<p,i>(c)) = i
%pred %( isOpd2Imm(c) )%
%{
    emit( ROOT, "add `d0, `s0, #"+c, i, j);
}%
BINOP<p,i>(ADD, j, BINOP<p,i>(shiftop, k, CONST<p,i>(c))) = i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    emit( ROOT, "add `d0, `s0, `s1, "+shiftOp2Str(shiftop)+" #"+c, i, j, k);
}%

BINOP<l>(ADD, j, k) = i %{

    emit( ROOT, "adds `d0l, `s0l, `s1l\n"+
		"adc  `d0h, `s0h, `s1h", i, j, k );
    // make sure d0l isn't assigned same reg as `s0h or `s1h
    emit2( ROOT, "@ dummy use of `s0l `s0h `s1l `s1h", null, new Temp[]{j,k});
}%

BINOP<f>(ADD, j, k) = i %{
    /* call auxillary fp routines */
    declare(r1, HClass.Float);
    declare(r0, HClass.Float);
    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2( ROOT, "bl ___addsf3",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<d>(ADD, j, k) = i %{
    /* call auxillary fp routines */
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );
        // not certain an emitMOVE is legal with the l/h modifiers
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___adddf3", // uses & stomps on these registers
	 new Temp[]{r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

    /*-------- SUBTRACT (which, in tree form, is (x + (-y) ) -------- */
BINOP<p,i>(ADD, j, UNOP<p,i>(NEG, k)) = i
%{
    emit( ROOT, "sub `d0, `s0, `s1", i, j, k);
}%
BINOP<p,i>(ADD, j, CONST<i>(c)) = i
%pred %( isOpd2Imm(negate(c)) )%
%{
    emit( ROOT, "sub `d0, `s0, #"+negate(c), i, j);
}%
BINOP<p,i>(ADD, j, UNOP<p,i>(NEG, BINOP<p,i>(shiftop, k, CONST<p,i>(c)))) = i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    emit( ROOT, "sub `d0, `s0, `s1, "+shiftOp2Str(shiftop)+" #"+c, i, j, k);
}%
    // bless its CISCy heart, StrongARM lets us reverse-subtract...
BINOP<p,i>(ADD, UNOP<p,i>(NEG, j), CONST<p,i>(c)) = i
%pred %( isOpd2Imm(c) )%
%{
    emit( ROOT, "rsb `d0, `s0, #"+c, i, j);
}%
BINOP<p,i>(ADD, UNOP<p,i>(NEG, j), BINOP<p,i>(shiftop, k, CONST<p,i>(c))) = i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    emit( ROOT, "rsb `d0, `s0, `s1, "+shiftOp2Str(shiftop)+" #"+c, i, j, k);
}%
    // okay, back to regular subtractions.
BINOP<l>(ADD, j, UNOP<l>(NEG, k)) = i %{

    emit( ROOT, "subs `d0l, `s0l, `s1l\n"+
		"sbc  `d0h, `s0h, `s1h", i, j, k );
    // make sure d0l isn't assigned same reg as `s0h or `s1h
    emit2( ROOT, "@ dummy use of `s0l `s0h `s1l `s1h", null, new Temp[]{j,k});
}%
BINOP<f>(ADD, j, UNOP<l>(NEG, k)) = i %{
    /* call auxillary fp routines */
    declare( r1, HClass.Float );
    declare( r0, HClass.Float );

    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2( ROOT, "bl ___subsf3",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
BINOP<d>(ADD, j, UNOP<l>(NEG, k)) = i %{
    /* call auxillary fp routines */
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

        // not certain an emitMOVE is legal with the l/h modifiers
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___subdf3", // uses & stomps on these registers
	 new Temp[]{r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<p,i>(AND, j, k) = i
%{
    emit( ROOT, "and `d0, `s0, `s1", i, j, k );
}%
BINOP<p,i>(AND, j, CONST<p,i>(c)) = i
%pred %( isOpd2Imm(c) )%
%{
    emit( ROOT, "and `d0, `s0, #"+c, i, j );
}%
BINOP<p,i>(AND, j, BINOP<p,i>(shiftop, k, CONST<p,i>(c))) = i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    emit( ROOT, "and `d0, `s0, `s1, "+shiftOp2Str(shiftop)+" #"+c, i, j, k );
}%

BINOP<l>(AND, j, k) = i %{

    emit( ROOT, "and `d0l, `s0l, `s1l", i, j, k );
    emit( ROOT, "and `d0h, `s0h, `s1h", i, j, k );
}%

    /* Auxilliary comparison functions on StrongARM are... interesting.
     * ___ne, ___gt, and ___lt return the result you would expect:
     * non-zero if the test is true, zero if it is false.
     * HOWEVER, ___eq, ___ge, and ___le return an *inverted* result:
     * non-zero if the test is *false*, zero if it is true.
     * Fun, fun, fun. [CSA]
     */

BINOP(CMPEQ, j, CONST<i,p>(c)) = i
%pred %( (ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT)
	 && (c==null || isOpd2Imm(c)) )%
%{
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #"+(c==null?"0 @ null":c.toString())+"\n"+
		"moveq `d0, #1\n"+
		"movne `d0, #0", i, j );
}%

BINOP(CMPEQ, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"moveq `d0, #1\n"+
		"movne `d0, #0", i, j, k );
}%

BINOP(CMPEQ, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0l, `s1l\n"+
		"cmpeq `s0h, `s1h\n"+
		"moveq `d0, #1\n"+
		"movne `d0, #0", i, j, k );
}%
  
BINOP(CMPEQ, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    declare( r1, HClass.Float );
    declare( r0, HClass.Float );
    /* NOTE: the ___eqsf2 routine seems to be broken, as it returns
     * the exact same values as ___nesf2.  The return value makes sense
     * for ___nesf2, but are reversed from what you'd expect for
     * ___eqsf2.  So we use the ___nesf2 routine here. */
    emitMOVE( ROOT, "mov `d0, `s0", r0, j);
    emitMOVE( ROOT, "mov `d0, `s0", r1, k);
    emit2( ROOT, "bl ___nesf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #1\n"+
		"movne `d0, #0", i, r0 );
}%

BINOP(CMPEQ, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    /* NOTE: the ___eqdf2 routine seems to be broken, as it returns
     * the exact same values as ___nedf2.  The return value makes sense
     * for ___nedf2, but are reversed from what you'd expect for
     * ___eqdf2.  So we use the ___nedf2 routine here. */
    emit ( ROOT, "mov `d0, `s0l", r0, j);
    emit ( ROOT, "mov `d0, `s0h", r1, j);
    emit ( ROOT, "mov `d0, `s0l", r2, k);
    emit ( ROOT, "mov `d0, `s0h", r3, k);
    emit2( ROOT, "bl ___nedf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1, r2, r3} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #1\n"+
		"movne `d0, #0", i, r0 );
}%

BINOP<p,i>(CMPGT, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(ROOT, "cmp `s0, `s1\n"+	
	       "movgt `d0, #1\n"+	
	       "movle `d0, #0", i, j, k );
}%

BINOP(CMPGT, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movgt `d0, #1\n"+
		"movle `d0, #0", i, j, k );
}%

BINOP(CMPGT, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    declare( r1, HClass.Float );
    declare( r0, HClass.Float );

    emitMOVE( ROOT, "mov `d0, `s0", r0, j);
    emitMOVE( ROOT, "mov `d0, `s0", r1, k);
    emit2( ROOT, "bl ___gtsf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #0\n"+
		"movne `d0, #1", i, r0 );
}%

BINOP(CMPGT, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    emit ( ROOT, "mov `d0, `s0l", r0, j);
    emit ( ROOT, "mov `d0, `s0h", r1, j);
    emit ( ROOT, "mov `d0, `s0l", r2, k);
    emit ( ROOT, "mov `d0, `s0h", r3, k);
    emit2( ROOT, "bl ___gtdf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1, r2, r3} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #0\n"+
		"movne `d0, #1", i, r0 );
}%


BINOP(CMPGE, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"movge `d0, #1\n"+
		"movlt `d0, #0", i, j, k );
}%

BINOP(CMPGE, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movge `d0, #1\n"+
		"movlt `d0, #0", i, j, k );
}%

BINOP(CMPGE, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    declare( r1, HClass.Float );
    declare( r0, HClass.Float );

    /* result from ___ge is inverted. */
    emitMOVE( ROOT, "mov `d0, `s0", r0, j);
    emitMOVE( ROOT, "mov `d0, `s0", r1, k);
    emit2( ROOT, "bl ___gesf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #1\n"+
		"movne `d0, #0", i, r0 );
}%

BINOP(CMPGE, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    /* result from ___ge is inverted. */
    emit ( ROOT, "mov `d0, `s0l", r0, j);
    emit ( ROOT, "mov `d0, `s0h", r1, j);
    emit ( ROOT, "mov `d0, `s0l", r2, k);
    emit ( ROOT, "mov `d0, `s0h", r3, k);
    emit2( ROOT, "bl ___gedf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1, r2, r3} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #1\n"+
		"movne `d0, #0", i, r0 );
}%


BINOP(CMPLE, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"movle `d0, #1\n"+
		"movgt `d0, #0", i, j, k );
}%

BINOP(CMPLE, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movle `d0, #1\n"+
		"movgt `d0, #0", i, j, k );
}%

BINOP(CMPLE, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    declare( r1, HClass.Float );
    declare( r0, HClass.Float );
    
    /* result from ___le is inverted. */
    emitMOVE( ROOT, "mov `d0, `s0", r0, j);
    emitMOVE( ROOT, "mov `d0, `s0", r1, k);
    emit2( ROOT, "bl ___lesf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #1\n"+
		"movne `d0, #0", i, r0 );
}%

BINOP(CMPLE, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    /* result from ___le is inverted. */
    emit ( ROOT, "mov `d0, `s0l", r0, j);
    emit ( ROOT, "mov `d0, `s0h", r1, j);
    emit ( ROOT, "mov `d0, `s0l", r2, k);
    emit ( ROOT, "mov `d0, `s0h", r3, k);
    emit2( ROOT, "bl ___ledf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1, r2, r3} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #1\n"+
		"movne `d0, #0", i, r0 );
}%

BINOP(CMPLT, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"movlt `d0, #1\n"+
		"movge `d0, #0", i, j, k );
}%

BINOP(CMPLT, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movlt `d0, #1\n"+
		"movge `d0, #0", i, j, k );
}%

BINOP(CMPLT, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    declare( r1, HClass.Float );
    declare( r0, HClass.Float );

    emitMOVE( ROOT, "mov `d0, `s0", r0, j);
    emitMOVE( ROOT, "mov `d0, `s0", r1, k);
    emit2( ROOT, "bl ___ltsf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #0\n"+
		"movne `d0, #1", i, r0 );
}%

BINOP(CMPLT, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    emit ( ROOT, "mov `d0, `s0l", r0, j);
    emit ( ROOT, "mov `d0, `s0h", r1, j);
    emit ( ROOT, "mov `d0, `s0l", r2, k);
    emit ( ROOT, "mov `d0, `s0h", r3, k);
    emit2( ROOT, "bl ___ltdf2",
	   new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0, r1, r2, r3} );
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, #0\n"+
	        "moveq `d0, #0\n"+
		"movne `d0, #1", i, r0 );
}%

BINOP<p,i>(OR, j, k) = i
%{
    emit( ROOT, "orr `d0, `s0, `s1", i, j, k );
}%
BINOP<p,i>(OR, j, CONST<p,i>(c)) = i
%pred %( isOpd2Imm(c) )%
%{
    emit( ROOT, "orr `d0, `s0, #"+c, i, j );
}%
BINOP<p,i>(OR, j, BINOP<p,i>(shiftop, k, CONST<p,i>(c))) = i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    emit( ROOT, "orr `d0, `s0, `s1, "+shiftOp2Str(shiftop)+" #"+c, i, j, k );
}%

BINOP<l>(OR, j, k) = i %{

    emit( ROOT, "orr `d0l, `s0l, `s1l", i, j, k );
    emit( ROOT, "orr `d0h, `s0h, `s1h", i, j, k );
}%

BINOP<p,i>(shiftop, j, k) = i
%pred %( isShiftOp(shiftop) )%
%{
    // FIXME: this pattern is incorrect if k>31.
    // java lang spec says shift should occur according to
    // 'least significant five bits' of k; StrongARM uses
    // least significant *byte*... w/ result 0 if k>31.
    emit( ROOT, "mov `d0, `s0, "+shiftOp2Str(shiftop)+" `s1", i, j, k );
}%

BINOP<p,i>(shiftop, j, CONST(c)) = i 
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    emit( ROOT, "mov `d0, `s0, "+shiftOp2Str(shiftop)+" #"+c, i, j);
}%

BINOP<l>(SHL, j, k) = i %{
    declare( r2, HClass.Int );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emitMOVE( ROOT, "mov `d0, `s0 ", r2, k );
    emit2(ROOT, "bl ___ashldi3",
	  new Temp[]{r0,r1,r2,r3,IP,LR},new Temp[]{r0,r1,r2});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<l>(SHR, j, k) = i %{
    declare( r2, HClass.Int );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emitMOVE( ROOT, "mov `d0, `s0 ", r2, k );
    emit2(ROOT, "bl ___ashrdi3",
	  new Temp[]{r0,r1,r2,r3,IP,LR},new Temp[]{r0,r1,r2});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<l>(USHR, j, k) = i %{
    declare( r2, HClass.Int );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emitMOVE( ROOT, "mov `d0, `s0 ", r2, k );
    emit2(ROOT, "bl ___lshrdi3",
	  new Temp[]{r0,r1,r2,r3,IP,LR},new Temp[]{r0,r1,r2});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%


BINOP<p,i>(XOR, j, k) = i
%{
    emit( ROOT, "eor `d0, `s0, `s1", i, j, k );
}%
BINOP<p,i>(XOR, j, CONST<p,i>(c)) = i
%pred %( isOpd2Imm(c) )%
%{
    emit( ROOT, "eor `d0, `s0, #"+c, i, j );
}%
BINOP<p,i>(XOR, j, BINOP<p,i>(shiftop, k, CONST<p,i>(c))) = i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    emit( ROOT, "eor `d0, `s0, `s1, "+shiftOp2Str(shiftop)+" #"+c, i, j, k );
}%

BINOP<l>(XOR, j, k) = i %{

    emit( ROOT, "eor `d0l, `s0l, `s1l", i, j, k );
    emit( ROOT, "eor `d0h, `s0h, `s1h", i, j, k );
}%


CONST<l,d>(c) = i %{

    long val = (ROOT.type()==Type.LONG) ? ROOT.value.longValue()
	: Double.doubleToLongBits(ROOT.value.doubleValue());
    // DOUBLEs are stored "backwards" on StrongARM.  No, I have no clue
    // why.  They just are.
    String lomod = (ROOT.type()==Type.LONG) ? "l" : "h";
    String himod = (ROOT.type()==Type.LONG) ? "h" : "l";
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0"+lomod, (int)val, "lo("+ROOT.value+")"),
		    new Temp[]{ i }, null));
    val>>>=32;
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0"+himod, (int)val, "hi("+ROOT.value+")"),
		    new Temp[]{ i }, null));
}% 

CONST<f,i>(c) = i %{

    int val = (ROOT.type()==Type.INT) ? ROOT.value.intValue()
	: Float.floatToIntBits(ROOT.value.floatValue());
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0", val, ROOT.value.toString()),
		    new Temp[]{ i }, null));
}%

CONST<p>(c) = i %{
    // the only CONST of type Pointer we should see is NULL
    Util.assert(c==null);
    emit(new Instr( instrFactory, ROOT, 
		    "mov `d0, #0 @ null", new Temp[]{ i }, null));
}%

// these next three rules just duplicate the above three with MOVE at the root.
// they should probably be deleted once move collation is working in the
// register allocator.

MOVE(TEMP(dst), CONST<l,d>(c)) %{
    Temp i = makeTwoWordTemp(dst);
    CONST cROOT = (CONST) ROOT.getSrc();
    long val = (cROOT.type()==Type.LONG) ? cROOT.value.longValue()
	: Double.doubleToLongBits(cROOT.value.doubleValue());
    // DOUBLEs are stored "backwards" on StrongARM.  No, I have no clue
    // why.  They just are.
    String lomod = (ROOT.type()==Type.LONG) ? "l" : "h";
    String himod = (ROOT.type()==Type.LONG) ? "h" : "l";
    declare( i, code.getTreeDerivation().typeMap( ROOT.getSrc() ) );

    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0"+lomod, (int)val, "lo("+cROOT.value+")"),
		    new Temp[]{ i }, null));
    val>>>=32;
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0"+himod, (int)val, "hi("+cROOT.value+")"),
		    new Temp[]{ i }, null));
}% 

MOVE(TEMP(dst), CONST<f,i>(c)) %{
    Temp i = makeTemp(dst);	
    CONST cROOT = (CONST) ROOT.getSrc();
    int val = (cROOT.type()==Type.INT) ? cROOT.value.intValue()
	: Float.floatToIntBits(cROOT.value.floatValue());
    declare( i, code.getTreeDerivation().typeMap( ROOT.getSrc()) );
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0", val, cROOT.value.toString()),
		    new Temp[]{ i }, null));
}%

MOVE(TEMP(dst), CONST<p>(c)) %{
    // the only CONST of type Pointer we should see is NULL
    Temp i = makeTemp(dst);
    declare( i, code.getTreeDerivation().typeMap( ROOT.getSrc()) );
    emit(new Instr( instrFactory, ROOT, 
		    "mov `d0, #0 @ null", new Temp[]{ i }, null));
}%

BINOP<p,i>(MUL, j, k) = i %{

    emit( ROOT, "mul `d0, `s0, `s1", i, j, k );
    // `d0 and `s0 can't be same register on ARM, so we insert a
    // dummy use of `s0 following the mul to keep it live.
    emit(new Instr( instrFactory, ROOT, "@ dummy",
		    null, new Temp[] { j }));
}%
    // strong arm has funky multiply & accumulate instruction.
BINOP<p,i>(ADD, l, BINOP<p,i>(MUL, j, k)) = i %{

    emit(new Instr( instrFactory, ROOT, "mla `d0, `s0, `s1, `s2",
		    new Temp[] { i }, new Temp[] { j, k, l } ));
    // `d0 and `s0 can't be same register on ARM, so we insert a
    // dummy use of `s0 following the mul to keep it live.
    emit(new Instr( instrFactory, ROOT, "@ dummy",
		    null, new Temp[] { j }));
}%

BINOP<l>(MUL, j, k) = i %{
    // TODO: use the SMULL instruction instead	     
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___muldi3", // uses & stomps on these registers
	 new Temp[]{r0,r1,r2,r3,IP,LR}, new Temp[]{r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<f>(MUL, j, k) = i %{
    declare( r1, HClass.Float );
    declare( r0, HClass.Float );

    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___mulsf3",
	      new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<d>(MUL, j, k) = i %{
    declare( r3, HClass.Void );
    declare( r2, HClass.Void );
    declare( r1, HClass.Void );
    declare( r0, HClass.Void );

    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___muldf3", // uses & stomps on these registers
	 new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<p,i>(DIV, j, k) = i %{

    declare( r1, code.getTreeDerivation().typeMap(ROOT.getRight()));
    declare( r0, code.getTreeDerivation().typeMap(ROOT.getLeft()));

    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___divsi3",
	      new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<l>(DIV, j, k) = i %{

    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___divdi3",	// uses and stomps on these registers
	 new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<f>(DIV, j, k) = i %{

    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___divsf3",
	      new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<d>(DIV, j, k) = i %{

    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___divdf3",
	 new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<p,i>(REM, j, k) = i %{
    declare( r1, code.getTreeDerivation().typeMap(ROOT.getRight()));
    declare( r0, code.getTreeDerivation().typeMap(ROOT.getLeft()));

    // XXX is this correct?  mod-vs-rem
    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___modsi3",
	      new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<l>(REM, j, k) = i %{
    // XXX is this correct?  mod-vs-rem
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___moddi3",
	 new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

// addressing modes for MEM are pretty rich.
// we can do offsets and scaling in same oper.

/* ACK! Our assembler doesn't support this, even though our processor does. =(
MEM<s:8,s:16,u:16>(e) = i %{ // addressing mode 3

    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    if (ROOT.isSmall() && ROOT.bitwidth()==16) suffix+="h";
    emit(new InstrMEM(instrFactory, ROOT,
		      "ldr"+suffix+" `d0, [`s0]",
		      new Temp[]{ i }, new Temp[]{ e }));
}%
*/
MEM<s:8>(e) = i %{ /* hack. ARMv4 has a special instr for this. */

    emit(new InstrMEM(instrFactory, ROOT, "ldrb `d0, [`s0] @ load signed byte",
		      new Temp[]{ i }, new Temp[]{ e }));
    emit( ROOT, "mov `d0, `s0, asl #24", i, i);
    emit( ROOT, "mov `d0, `s0, asr #24", i, i);
}%
MEM<s:16,u:16>(e) = i %{ /* hack. ARMv4 has a special instr for this. */

    emit(new InstrMEM(instrFactory, ROOT, "ldr `d0, [`s0] @ load halfword",
		      new Temp[]{ i }, new Temp[]{ e }));
    emit( ROOT, "mov `d0, `s0, asl #16", i, i);
    if (ROOT.signed())
	emit( ROOT, "mov `d0, `s0, asr #16", i, i);
    else
	emit( ROOT, "mov `d0, `s0, lsr #16", i, i);
}%
MEM<u:8,p,i,f>(e) = i %{ // addressing mode 2

    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0]",
		     new Temp[]{ i }, new Temp[]{ e }));
}%
MEM<u:8,p,i,f>(BINOP<p>(ADD, j, k)) = i %{ // addressing mode 2

    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, `s1]",
		     new Temp[]{ i }, new Temp[]{ j, k }));
}%
MEM<u:8,p,i,f>(BINOP<p>(ADD, j, BINOP(shiftop, k, CONST<p,i>(c)))) = i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, `s1, " +
		                          shiftOp2Str(shiftop)+" #"+c+"]",
		     new Temp[]{ i }, new Temp[]{ j, k }));
}%
MEM<u:8,p,i,f>(BINOP<p>(ADD, j, UNOP(NEG, k))) = i %{ // addressing mode 2

    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, -`s1]",
		     new Temp[]{ i }, new Temp[]{ j, k }));
}%
MEM<u:8,p,i,f>(BINOP<p>(ADD, j, UNOP(NEG, BINOP(shiftop, k, CONST<p,i>(c)))))=i
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, -`s1, " +
		                          shiftOp2Str(shiftop)+" #"+c+"]",
		     new Temp[]{ i }, new Temp[]{ j, k }));
}%
MEM<u:8,p,i,f>(BINOP(ADD, j, CONST<i,p>(c))) = i
%pred %( is12BitOffset(c) )%
%{

    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, #"+c+"]",
		     new Temp[]{ i }, new Temp[]{ j }));
}%
MEM<l,d>(e) = i %{

    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr `d0l, [`s0]",
		     new Temp[]{ i }, new Temp[]{ e }));
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr `d0h, [`s0, #4]",
		     new Temp[]{ i }, new Temp[]{ e }));
}%

// can use adr for 8 bit offsets to variables close by,
// but need to use ldr for far away symbolic variables
NAME(id) = i %{
    // produces a pointer

    Label target = new Label("2"+id);
    Instr i2 = new Instr(instrFactory, ROOT,
			 "ldr `d0, 1f\n" + "b 2f", 
			 new Temp[]{ i }, null, false, 
			 Arrays.asList(new Label[]{ target })) {
			     public boolean hasModifiableTargets() {
				 return false; 
			     }};
    
    emit(i2);
    
    Util.assert(i2.succC().size() == 1, "linear control flow");

    // these may need to be included in the previous instr to preserve
    // ordering semantics, but for now this way they indent properly
    emitNoFallLABEL( ROOT, "1:", new Label("1"));
    emitNoFallDIRECTIVE( ROOT, "\t.word " + id);
    // FSK: changed above to NoFall emits so that this is not treated
    // as the start of a new basic block.
    i2 = emitLABEL( ROOT, "2:", target);
    
    Util.assert(i2.predC().size() == 1, 
		"> one predecessor "+ i2.predC());

}%

/* Not sure yet how to handle this 
MEM<f,i,p>(NAME(id)) = i %{

    emit(new Instr( instrFactory, ROOT,
		    "ldr `d0, " + id, 
		    new Temp[]{ i }, null ));
}%
MEM<d,l>(NAME(id)) = i %{

    emit(new Instr( instrFactory, ROOT,
		    "ldr `d0l, " + id, 
		    new Temp[]{ i }, null ));
    emit(new Instr( instrFactory, ROOT,
		    "ldr `d0h, " + id + "+4", 
		    new Temp[]{ i }, null ));
}%
*/

TEMP<p,i,f>(id) = i %{
    i = makeTemp( ROOT.temp );
}%
TEMP<l,d>(id) = i %{
    i = makeTwoWordTemp( ROOT.temp );		
}%


UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    Util.assert(false, "Spec file doesn't handle long-to-byte conversion directly");
}%
UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{

    Util.assert(false, "Spec file doesn't handle float-to-byte conversion directly");
}%
UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{

    Util.assert(false, "Spec file doesn't handle double-to-byte conversion directly");
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    Util.assert(false, "Spec file doesn't handle long-to-char conversion directly");
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{

    Util.assert(false, "Spec file doesn't handle float-to-char conversion directly");
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{

    Util.assert(false, "Spec file doesn't handle double-to-char conversion directly");
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    Util.assert(false, "Spec file doesn't handle long-to-short conversion directly");
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{

    Util.assert(false, "Spec file doesn't handle float-to-short conversion directly");
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{

    Util.assert(false, "Spec file doesn't handle double-to-short conversion directly");
}%


UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{

    emit( ROOT, "mov `d0, `s0, asl #24", i, arg);
    emit( ROOT, "mov `d0, `s0, asr #24", i, i);
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{

    emit( ROOT, "mov `d0, `s0, asl #16", i, arg);
    emit( ROOT, "mov `d0, `s0, lsr #16", i, i);
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{

    emit( ROOT, "mov `d0, `s0, asl #16", i, arg);
    emit( ROOT, "mov `d0, `s0, asr #16", i, i);
}%


UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___floatdidf",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%
UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
		
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(ROOT, "bl ___floatsidf",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%
UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{

    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(ROOT, "bl ___extendsfdf2",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );

}%
/* this is useless.  Should never really be in Tree form.
UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
	// a move, basically.

    emit( ROOT, "mov `d0l, `s0l @ unop d2d", i, arg );
    emit( ROOT, "mov `d0h, `s0h @ unop d2d", i, arg );
}%
*/

UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___floatdisf",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{

    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(    ROOT, "bl ___floatsisf",
	      new Temp[] {r0,r1,r2,r3,IP,LR},new Temp[] {r0} );   
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
/* useless.  should never really be in tree form.
UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{

    emitMOVE( ROOT, "mov `d0, `s0", i, arg );
}%
*/
UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{

    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___truncdfsf2",
	  new Temp[] {r0,r1,r2,r3,IP,LR},new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    emit( ROOT, "mov `d0, `s0l", i, arg );
}%
UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.POINTER )% %{

    emitMOVE( ROOT, "mov `d0, `s0", i, arg );
}%
UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{

    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(    ROOT, "bl ___fixsfsi",
	      new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{

    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___fixdfsi",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

/* useless.  should never really be in tree form.
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    emit( ROOT, "mov `d0l, `s0l @ unop l2l", i, arg );
    emit( ROOT, "mov `d0h, `s0h", i, arg );
}%
*/
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{

    emit( ROOT, "mov `d0l, `s0", i, arg );
    emit( ROOT, "mov `d0h, `s0l, asr #31", i, i );
}%
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
	
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(ROOT, "bl ___fixsfdi",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{

    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___fixdfdi",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );	 
}%


UNOP(NEG, arg) = i
%pred %( ROOT.operandType()==Type.INT || ROOT.operandType()==Type.POINTER )%
%{

    emit( ROOT, "rsb `d0, `s0, #0", i, arg );
}% 
UNOP(NEG, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    // uses condition codes, so keep together
    emit( ROOT, "rsbs `d0l, `s0l, #0\n" +
    	        "rsc  `d0h, `s0h, #0", i, arg );
    // make sure d0l isn't assigned same reg as `s0h
    emit2( ROOT, "@ dummy use of `s0l `s0h", null, new Temp[]{arg});
}% 
UNOP(NEG, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{

    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(    ROOT, "bl ___negsf2",
	      new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
UNOP(NEG, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )%
%{

    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___negdf2",
	  new Temp[] {r0,r1,r2,r3,IP,LR}, new Temp[] {r0,r1} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );	 
}%

UNOP(NOT, arg) = i
%pred %( ROOT.operandType()==Type.INT )%
%{
    emit( ROOT, "mvn `d0, `s0", i, arg );
}% 
    // the UNOP(NOT, CONST(k)) case was left out; it should never show up in
    // optimized code.
UNOP(NOT, BINOP<p,i>(shiftop, j, CONST<p,i>(c))) = i
%pred %( ROOT.operandType()==Type.INT && isShiftOp(shiftop)&& is5BitShift(c) )%
%{
    emit( ROOT, "mvn `d0, `s0, "+shiftOp2Str(shiftop)+" #"+c, i, j );
}% 
UNOP(NOT, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{

    emit( ROOT, "mvn `d0l, `s0l", i, arg );
    emit( ROOT, "mvn `d0h, `s0h", i, arg );
}% 

/* STATEMENTS */
METHOD(params) %{
    // mark entry point.
    emit(new InstrENTRY( instrFactory, ROOT ));
    // move arguments to temporaries.
    int loc=0;
    // skip param[0], which is the explicit 'exceptional return address'
    for (int i=1; i<params.length; i++) {
	if (params[i] instanceof TwoWordTemp) {
	    declare(params[i], HClass.Void);
	    if (loc<=2) { // both halves in registers
		// ack.  emitMOVE isn't working with long/double types.
		emit( ROOT, "mov `d0l, `s0", params[i],regfile.reg[loc++]);
		emit( ROOT, "mov `d0h, `s0", params[i],regfile.reg[loc++]);
	    } else if (loc==3) { // one half in register, one on stack
		// ack.  emitMOVE isn't working with long/double types.
		emit( ROOT, "mov `d0l, `s0", params[i],regfile.reg[loc++]);
		emit(new InstrMEM( instrFactory, ROOT,
				   "ldr `d0h, [`s0, #"+(4*(loc++)-12)+"]",
				   new Temp[] {params[i]}, new Temp[] {FP}));
	    } else { // both halves on stack.
		emit(new InstrMEM( instrFactory, ROOT,
				   "ldr `d0l, [`s0, #"+(4*(loc++)-12)+"]",
				   new Temp[] {params[i]}, new Temp[] {FP}));
		emit(new InstrMEM( instrFactory, ROOT,
				   "ldr `d0h, [`s0, #"+(4*(loc++)-12)+"]",
				   new Temp[] {params[i]}, new Temp[] {FP}));
	    }
	} else { // single word.
	    declare(params[i], 
		    code.getTreeDerivation().typeMap(ROOT.getParams()[i]));
	    if (loc<4) { // in register
		emitMOVE( ROOT, "mov `d0, `s0", params[i], regfile.reg[loc++]);
	    } else { // on stack
		emit(new InstrMEM( instrFactory, ROOT,
				   "ldr `d0, [`s0, #"+(4*(loc++)-12)+"]",
				   new Temp[] {params[i]}, new Temp[] {FP}));
	    }
	}
    }
}%

CJUMP(test, iftrue, iffalse) %{
    Instr j1 = emit( ROOT, "cmp `s0, #0 \n" +
			   "beq `L0", 
			   null, new Temp[]{ test },
			   new Label[]{ iffalse });
    Instr j2 = emitJUMP( ROOT, "b `L0", iftrue );
}%

CJUMP(BINOP(cmpop, j, k), iftrue, iffalse)
%pred %( isCmpOp(cmpop) &&
	 ( ((BINOP) ROOT.getTest()).operandType()==Type.POINTER ||
	   ((BINOP) ROOT.getTest()).operandType()==Type.INT ) )%
%{
    emit( ROOT, "cmp `s0, `s1\n" +
	        "b"+cmpOp2Str(cmpop)+" `L0",
	  null, new Temp[] { j , k }, new Label[] { iftrue });
    emitJUMP( ROOT, "b `L0", iffalse );
}%

CJUMP(BINOP(cmpop, j, CONST<i,p>(c)), iftrue, iffalse)
%pred %( isCmpOp(cmpop) && (c==null || isOpd2Imm(c)) )%
%{  // this is a frequent special case.
    emit( ROOT, "cmp `s0, #"+(c==null?"0 @ null":c.toString())+"\n" +
	        "b"+cmpOp2Str(cmpop)+" `L0",
	  null, new Temp[] { j }, new Label[] { iftrue });
    emitJUMP( ROOT, "b `L0", iffalse );
}%
CJUMP(BINOP(cmpop, j, CONST<i>(c)), iftrue, iffalse)
%pred %( isCmpOp(cmpop) && isOpd2Imm(negate(c)) )%
%{  // this is a frequent special case.
    emit( ROOT, "cmn `s0, #"+negate(c)+"\n" +
	        "b"+cmpOp2Str(cmpop)+" `L0",
	  null, new Temp[] { j }, new Label[] { iftrue });
    emitJUMP( ROOT, "b `L0", iffalse );
}%

EXP(e) %{
			/* this is a statement that's just an
			   expression; just throw away 
			   calculated value */
}%

JUMP(NAME(id)) %{ // direct jump
    emitJUMP( ROOT, "b `L0", id );
}%

JUMP(e) %{
    List labelList = LabelList.toList( ROOT.targets );
    Instr j = 
       emit(new Instr( instrFactory, ROOT, 
		       "mov `d0, `s0",
		       new Temp[]{ PC },
		       // fake use of PC so that the register allocator
		       // doesn't think that PC is not live above this point
		       new Temp[]{ e, PC },
		       false, labelList ) {
			      public boolean hasModifiableTargets(){ 
				     return false; 
			      }
    });
}%

LABEL(id) %{
    if (ROOT.exported) {
      emitLABEL( ROOT, "\t.global "+ROOT.label+"\n"+
		    ROOT.label + ":", ROOT.label);
    } else {
      emitLABEL( ROOT, ROOT.label + ":", ROOT.label);
    }
}%

MOVE<p,i,f>(TEMP(dst), src) %{
    dst = makeTemp(dst);
    declare( dst, code.getTreeDerivation().typeMap(ROOT.getSrc()) );
    emitMOVE( ROOT, "mov `d0, `s0", dst, src );
}%

MOVE<d,l>(TEMP(dst), src) %{
    dst = makeTwoWordTemp(dst);
    Util.assert( dst instanceof TwoWordTemp, "why is dst: "+dst + 
		 " a normal Temp? " + harpoon.IR.Tree.Print.print(ROOT));

    Util.assert(src instanceof TwoWordTemp, "why is src: "+src + 
		 " a normal Temp? " + harpoon.IR.Tree.Print.print(ROOT));

    declare( dst, code.getTreeDerivation().typeMap( ROOT.getSrc() ) );

        // not certain an emitMOVE is legal with the l/h modifiers
    emit( ROOT, "mov `d0l, `s0l", dst, src );
    emit( ROOT, "mov `d0h, `s0h", dst, src );
}%

/* ACK! Our assembler doesn't support this, even though our processor does. =(
MOVE(MEM<s:16,u:16>(d), src) %{ // addressing mode 3
    emit(new InstrMEM(instrFactory, ROOT,
		      "strh `s0, [`s1]",
		      null, new Temp[]{ src, d }));
}%
*/
MOVE(MEM<s:16,u:16>(d), src) %{ /* hack. ARMv4 has a special instr for this. */
    emit(new InstrMEM(instrFactory, ROOT,
		      "strb `s0, [`s1, #0] @ store halfword lo",
		      null, new Temp[]{ src, d }));
    emit( ROOT, "mov `d0, `s0, ror #8", src, src );
    emit(new InstrMEM(instrFactory, ROOT,
		      "strb `s0, [`s1, #1] @ store halfword hi",
		      null, new Temp[]{ src, d }));
    emit( ROOT, "mov `d0, `s0, ror #24", src, src );
}%
MOVE(MEM<s:8,u:8,p,i,f>(d), src) %{ // addressing mode 2
    String suffix="";
    if (((MEM)ROOT.getDst()).isSmall() && ((MEM)ROOT.getDst()).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1]",
		      null, new Temp[]{ src, d }));   
}%
    // register plus (scaled) register (addressing mode 2)
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, d1, d2)), src) %{
    String suffix="";
    if (((MEM)ROOT.getDst()).isSmall() && ((MEM)ROOT.getDst()).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1, `s2]",
		      null, new Temp[]{ src, d1, d2 }));   
}%
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, d1, BINOP(shiftop, d2, CONST<p,i>(c)))),
     src)
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    String suffix="";
    if (((MEM)ROOT.getDst()).isSmall() && ((MEM)ROOT.getDst()).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1, `s2, " +
		                           shiftOp2Str(shiftop)+" #"+c+"]",
		      null, new Temp[]{ src, d1, d2 }));   
}%
    // register minus (scaled) register (addressing mode 2)
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, d1, UNOP(NEG, d2))), src)
%{
    String suffix="";
    if (((MEM)ROOT.getDst()).isSmall() && ((MEM)ROOT.getDst()).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1, -`s2]",
		      null, new Temp[]{ src, d1, d2 }));   
}%
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, d1,
				 UNOP(NEG,
				      BINOP(shiftop, d2, CONST<p,i>(c))))),
     src)
%pred %( isShiftOp(shiftop) && is5BitShift(c) )%
%{
    String suffix="";
    if (((MEM)ROOT.getDst()).isSmall() && ((MEM)ROOT.getDst()).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1, -`s2, " +
		                           shiftOp2Str(shiftop)+" #"+c+"]",
		      null, new Temp[]{ src, d1, d2 }));   
}%
    // register plus/minus a constant (addressing mode 2)
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, d, CONST<i,p>(c))), src)
%pred %( is12BitOffset(c) )%
%{
    String suffix="";
    if (((MEM)ROOT.getDst()).isSmall() && ((MEM)ROOT.getDst()).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1, #"+c+"]",
		      null, new Temp[]{ src, d }));   
}%

MOVE(MEM<l,d>(dst), src) %{
    emit(new InstrMEM(instrFactory, ROOT, "str `s0l, [`s1]",
		      null, new Temp[]{ src, dst }));   
    emit(new InstrMEM(instrFactory, ROOT, "str `s0h, [`s1, #4]",
		      null, new Temp[]{ src, dst }));   
}%

RETURN<i,f,p>(val) %{
    declare( r0, code.getTreeDerivation().typeMap( ROOT.getRetval() ));
    emitMOVE( ROOT, "mov `d0, `s0", r0, val );
    // mark exit point.
    emit(new InstrEXIT( instrFactory, ROOT ));
}%

RETURN<l,d>(val) %{
    // these should really be InstrMOVEs!
    declare( r0, HClass.Void );
    declare( r1, HClass.Void );
    emit( ROOT, "mov `d0, `s0l", r0, val);
    emit( ROOT, "mov `d0, `s0h", r1, val);
    // mark exit point.
    emit(new InstrEXIT( instrFactory, ROOT ));
}%


THROW(val, handler) %{
    // ignore handler, as our runtime does clever things instead.
    emitMOVE( ROOT, "mov `d0, `s0", r0, val );
    emit( ROOT, "bl _lookup @ (only r0 & fp are preserved during lookup)",
	         new Temp[] { r1, r2, r3, LR }, // clobbers
		 new Temp[] { FP }, true, null); 
    // mark exit point.
    emit(new InstrEXIT( instrFactory, ROOT ));
}%

  // slow version when we don't know exactly which method we're calling.
CALL(retval, retex, func, arglist, handler)
%pred %( !ROOT.isTailCall )%
%{
    CallState cs = emitCallPrologue(ROOT, arglist, 
				    buildTypeHCs(ROOT, code.getTreeDerivation()));
    Label rlabel = new Label(), elabel = new Label();
    retex = makeTemp(retex);
    // next two instructions are *not* InstrMOVEs, as they have side-effects
    declare( LR, HClass.Void );
    emit2( ROOT, "adr `d0, "+rlabel, new Temp[] { LR }, null );
    // call uses 'func' as `s0
    // we add a fake use of PC so that it remains live above the call.
    cs.callUses.add(PC); cs.callUses.add(0, func);
    // note that r0-r3, LR and IP are clobbered by the call.
    declare( r0, HClass.Void ); declare( r1, HClass.Void );
    declare( r2, HClass.Void ); declare( r3, HClass.Void );
    declare( PC, HClass.Void ); declare( IP, HClass.Void );
    
    emitCallNoFall( ROOT,cs.prependSPOffset("mov `d0, `s0 @ clobbers r0-r3,LR,IP"),
		new Temp[]{ PC, r0, r1, r2, r3, IP, LR },
                (Temp[]) cs.callUses.toArray(new Temp[cs.callUses.size()]),
                new Label[] { rlabel, elabel } );
    // make handler stub.
    emitLABEL( ROOT, elabel+":", elabel);
    emitHandlerStub(ROOT, retex, handler);
    // normal return
    emitLABEL( ROOT, rlabel+":", rlabel);
    emitCallEpilogue(ROOT, retval,
		     ((ROOT.getRetval()==null)?null:
		      code.getTreeDerivation().typeMap(ROOT.getRetval())), cs);
    // emit fixup table.
    emitCallFixup(ROOT, rlabel, elabel);
}%
  // optimized version when we know exactly which method we're calling.
CALL(retval, retex, NAME(funcLabel), arglist, handler)
%pred %( !ROOT.isTailCall )%
%{
    CallState cs = emitCallPrologue(ROOT, arglist, 
				    buildTypeHCs(ROOT, code.getTreeDerivation()));
    Label rlabel = new Label(), elabel = new Label();
    retex = makeTemp(retex);
    // do the call.  bl has a 24-bit offset field, which should be plenty.
    // note that r0-r3, LR and IP are clobbered by the call.
    declare( LR, HClass.Void );
    emit2( ROOT, "adr `d0, "+rlabel, new Temp[] { LR }, null );

    declare( r0, HClass.Void ); declare( r1, HClass.Void );
    declare( r2, HClass.Void ); declare( r3, HClass.Void );
    declare( PC, HClass.Void ); declare( IP, HClass.Void );

    emitCallNoFall( ROOT, cs.prependSPOffset("b "+funcLabel +
					 " @ clobbers r0-r3, LR, IP"),
		new Temp[] { r0,r1,r2,r3,IP,LR },
                (Temp[]) cs.callUses.toArray(new Temp[cs.callUses.size()]),
                new Label[] { rlabel, elabel } );
    // make handler stub.
    emitLABEL( ROOT, elabel+":", elabel);
    emitHandlerStub(ROOT, retex, handler);
    // normal return
    emitLABEL( ROOT, rlabel+":", rlabel);
    emitCallEpilogue(ROOT, retval,
		     ((ROOT.getRetval()==null)?null:
		      code.getTreeDerivation().typeMap(ROOT.getRetval())), cs);
    // emit fixup table.
    emitCallFixup(ROOT, rlabel, elabel);
}%
  // slow version when we don't know exactly which method we're calling.
NATIVECALL(retval, func, arglist) %{
    CallState cs = emitCallPrologue(ROOT, arglist, 
				    buildTypeHCs(ROOT, code.getTreeDerivation()));
    // next two instructions are *not* InstrMOVEs, as they have side-effects
    emit( ROOT, "mov `d0, `s0", LR, PC );
    // call uses 'func' as `s0
    // we add a fake use of PC so that it remains live above the call.
    cs.callUses.add(PC); cs.callUses.add(0, func);
    // note that r0-r3, LR and IP are clobbered by the call.
    emitNativeCall( ROOT, cs.prependSPOffset("mov `d0, `s0 @ clobbers r0-r3, LR, IP"),
	   new Temp[]{ PC, r0, r1, r2, r3, IP, LR },
	   (Temp[]) cs.callUses.toArray(new Temp[cs.callUses.size()]),
	   true, null);
    // clean up.
    emitCallEpilogue(ROOT, retval, 
		     ((ROOT.getRetval()==null)?null:
		      code.getTreeDerivation().typeMap(ROOT.getRetval())), cs);
}%
  // optimized version when we know exactly which method we're calling.
NATIVECALL(retval, NAME(funcLabel), arglist) %{
    CallState cs = emitCallPrologue(ROOT, arglist, 
				    buildTypeHCs(ROOT, code.getTreeDerivation()));
    // do the call.  bl has a 24-bit offset field, which should be plenty.
    // note that r0-r3, LR and IP are clobbered by the call.
    emitNativeCall( ROOT, cs.prependSPOffset("bl "+funcLabel +
				   " @clobbers r0-r3, LR, IP"),
	  new Temp[] { r0,r1,r2,r3,IP,LR },
	  (Temp[]) cs.callUses.toArray(new Temp[cs.callUses.size()]),
          true, null );
    // clean up.
    emitCallEpilogue(ROOT, retval, 
		     ((ROOT.getRetval()==null)?null:
		      code.getTreeDerivation().typeMap(ROOT.getRetval())),  cs);
}%

DATUM(CONST<i,f>(exp)) %{
    int i = (ROOT.getData().type()==Type.INT) ? exp.intValue()
		: Float.floatToIntBits(exp.floatValue());
    String lo = "0x"+Integer.toHexString(i);
    emitDIRECTIVE( ROOT, "\t.word "+lo+" @ "+exp);
}%

DATUM(CONST<l,d>(exp)) %{
    long l = (ROOT.getData().type()==Type.LONG) ? exp.longValue()
		: Double.doubleToLongBits(exp.doubleValue());
    String lo = "0x"+Integer.toHexString((int)l);
    String hi = "0x"+Integer.toHexString((int)(l>>32));
    // doubles are stored in reverse order on the StrongARM.  No, I don't
    // know why.  I suspect the StrongARM library designers were on *crack*!
    if (ROOT.getData().type()==Type.LONG)
	emitDIRECTIVE( ROOT, "\t.word "+lo+" @ lo("+exp+")");
    emitDIRECTIVE( ROOT, "\t.word "+hi+" @ hi("+exp+")");
    if (ROOT.getData().type()==Type.DOUBLE)
	emitDIRECTIVE( ROOT, "\t.word "+lo+" @ lo("+exp+")");
}%

DATUM(CONST<p>(exp)) %{
    emitDIRECTIVE( ROOT, "\t.word 0 @ null pointer constant");
}%

DATUM(CONST<s:8,u:8>(exp)) %{
    String chardesc = (exp.intValue()>=32 && exp.intValue()<127 
		       && exp.intValue()!=96 /* backquotes cause problems */
		       && exp.intValue()!=34 /* so do double quotes */) ?
	("\t@ char "+((char)exp.intValue())) : "";
    emitDIRECTIVE( ROOT, "\t.byte "+exp+chardesc);
}%

DATUM(CONST<s:16,u:16>(exp)) %{
    String chardesc = (exp.intValue()>=32 && exp.intValue()<127
		       && exp.intValue()!=96 /* backquotes cause problems */
		       && exp.intValue()!=34 /* so do double quotes */) ?
	("\t@ char "+((char)exp.intValue())) : "";
    emitDIRECTIVE( ROOT, "\t.short "+exp+chardesc);
}%

DATUM(NAME(l)) %{
    emitDIRECTIVE( ROOT, "\t.word "+l);
}%

ALIGN(n) %{
    emitDIRECTIVE( ROOT, "\t.balign "+n);
}%

SEGMENT(CLASS) %{
    emitDIRECTIVE( ROOT, ".data 1\t@.section class");

}%

SEGMENT(CODE) %{
    // gas 2.7 does not support naming the code section...not
    // sure what to do about this yet...
    // emitDIRECTIVE( ROOT, ".code 32\t@.section code");
    emitDIRECTIVE( ROOT, ".text 0\t@.section code");
}%

SEGMENT(GC) %{
    emitDIRECTIVE( ROOT, ".data 2\t@.section gc");
}%

SEGMENT(INIT_DATA) %{
    emitDIRECTIVE( ROOT, ".data 3\t@.section init_data");
}%

SEGMENT(STATIC_OBJECTS) %{
    emitDIRECTIVE( ROOT, ".data 4\t@.section static_objects");
}%

SEGMENT(STATIC_PRIMITIVES) %{
    emitDIRECTIVE( ROOT, ".data 5\t@.section static_primitives");
}%

SEGMENT(STRING_CONSTANTS) %{
    emitDIRECTIVE( ROOT, ".data 6\t@.section string_constants");
}%

SEGMENT(STRING_DATA) %{
    emitDIRECTIVE( ROOT, ".data 7\t@.section string_data");
}%

SEGMENT(REFLECTION_OBJECTS) %{
    emitDIRECTIVE( ROOT, ".data 8\t@.section reflection_objects");
}%

SEGMENT(REFLECTION_DATA) %{
    emitDIRECTIVE( ROOT, ".data 9\t@.section reflection_data");
}%

SEGMENT(GC_INDEX) %{
    emitDIRECTIVE( ROOT, ".data 10\t@.section gc_index");
}%

SEGMENT(TEXT) %{
    emitDIRECTIVE( ROOT, ".text  \t@.section text");
}%

SEGMENT(ZERO_DATA) %{
   // gas 2.7 does not allow BSS subsections...use .comm and .lcomm
   // for the variables to be initialized to zero
   // emitDIRECTIVE( ROOT, ".bss   \t@.section zero");
}%
// Local Variables:
// mode:java
// End:
