// CodeGen.spec, created Tue Jul 6 12:12:41 1999 by pnkfelix
// Copyright (C) 1999 Felix S. Klock II <pnkfelix@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Backend.StrongARM;

import harpoon.ClassFile.HCodeElement;
import harpoon.ClassFile.HMethod;
import harpoon.ClassFile.HCode;
import harpoon.IR.Assem.Instr;
import harpoon.IR.Assem.InstrEdge;
import harpoon.IR.Assem.InstrMEM;
import harpoon.IR.Assem.InstrJUMP;
import harpoon.IR.Assem.InstrMOVE;
import harpoon.IR.Assem.InstrLABEL;
import harpoon.IR.Assem.InstrDIRECTIVE;
import harpoon.IR.Assem.InstrFactory;
import harpoon.IR.Tree.Bop;
import harpoon.IR.Tree.Uop;
import harpoon.IR.Tree.Type;
import harpoon.IR.Tree.TEMP;
import harpoon.IR.Tree.Typed;
import harpoon.IR.Tree.PreciselyTyped;
import harpoon.IR.Tree.ExpList;
import harpoon.Backend.Generic.Code;
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

import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.Map;
import java.util.HashMap;
import java.util.Iterator;

/**
 * <code>StrongARM.CodeGen</code> is a code-generator for the ARM architecture.
 * 
 * @see Jaggar, <U>ARM Architecture Reference Manual</U>
 * @author  Felix S. Klock II <pnkfelix@mit.edu>
 * @version $Id: CodeGen.spec,v 1.1.2.79 1999-10-19 19:57:45 cananian Exp $
 */
%%


    // FIELDS
    // first = null OR first instr passed to emit(Instr)
    private Instr first;

    // last = null OR last instr passed to emit(Instr)
    private Instr last; 
    
    // InstrFactory to generate Instrs from
    private InstrFactory instrFactory;
    
    // Frame for instructions to access to get platform specific variables (Register Temps, etc) 
    private Frame frame;

    private Temp r0, r1, r2, r3, r4, r5, r6, PC, SP, FP, LR;


    public CodeGen(Frame frame) {
	last = null;
	this.frame = frame;
	RegFileInfo regfile = (RegFileInfo) frame.getRegFileInfo();
	r0 = regfile.reg[0];
	r1 = regfile.reg[1];
	r2 = regfile.reg[2];
	r3 = regfile.reg[3];
	r4 = regfile.reg[4];
	r5 = regfile.reg[5];
	r6 = regfile.reg[6];
	PC = regfile.PC;
	SP = regfile.SP;
	FP = regfile.FP;
	LR = regfile.LR;
    }

    /** Emits <code>i</code> as the next instruction in the
        instruction stream.
    */	
    private Instr emit(Instr i) {
	debug( "Emitting "+i.toString() );
	if (first == null) {
	    first = i;
	}	   
	// its correct that last==null the first time this is called
	i.layout(last, null);
	last = i;
	return i;
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
	return emit(new InstrMOVE( instrFactory, root, assem,
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

    /* InstrDIRECTIVE emit helper. */
    private Instr emitDIRECTIVE( HCodeElement root, String assem ) {
	return emit( new InstrDIRECTIVE( instrFactory, root, assem ));
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

    /** Helper for setting up registers/memory with the strongARM standard
     *  calling convention.  Returns the stack offset necessary. */
    private int emitCallPrologue(INVOCATION ROOT, TempList list) {
      int stackOffset = 0;

      for (int index=0; list != null; index++) { 
	Temp temp = list.head;
	if (temp instanceof TwoWordTemp) {
	  // arg takes up two words
	  switch(index) {
	  case 0: case 1: case 2: // put in registers 
	    // not certain an emitMOVE is legal with the l/h modifiers
	    emit( ROOT, "mov `d0, `s0l",
		  frame.getRegFileInfo().getRegister(index) ,
		  temp );
	    index++;			     
	    emit( ROOT, "mov `d0, `s0h",
		  frame.getRegFileInfo().getRegister(index),
		  temp );
	    break;			     
	  case 3: // spread between regs and stack
	    // not certain an emitMOVE is legal with the l/h modifiers
	    emit( ROOT, "mov `d0, `s0l",
		  frame.getRegFileInfo().getRegister(index),
		  temp );
	    index++;
	    stackOffset += 4;
	    emit(new InstrMEM( instrFactory, ROOT,
			       "str `s0h, [`s1, #-4]!",
			       new Temp[]{ SP }, // SP *implicitly* modified
			       new Temp[]{ temp, SP })); 
	    break;
	  default: // start putting args in memory
	    emit(new InstrMEM( instrFactory, ROOT,
			       "str `s0l, [`s1, #-4]!", 
			       new Temp[] { SP }, // SP *implicitly* modified 
			       new Temp[]{ SP, temp }));
	    index++;
	    stackOffset += 4;
	    emit(new InstrMEM( instrFactory, ROOT,
			       "str `s0h, [`s1, #-4]!",
			       new Temp[]{ SP }, // SP *implicitly* modified
			       new Temp[]{ temp, SP })); 
	    stackOffset += 4;
	    break;
	  }
	} else {
	  // arg is one word
	  if (index < 4) {
	    emitMOVE( ROOT, "mov `d0, `s0", 
		      frame.getRegFileInfo().getRegister(index), temp);
	  } else {
	    emit(new InstrMEM(
			      instrFactory, ROOT,
			      "str `s0, [`s1, #-4]!",
			      new Temp[]{ SP }, // SP *implicitly* modified
			      new Temp[]{ temp, SP }));
	    stackOffset += 4;
	  }
	}
	list = list.tail;    	
      }
      return stackOffset;
    }
    /** Emit a fixup table entry */
    private void emitCallFixup(INVOCATION ROOT, Label retex) {
      // this '1f' and '1:' business is taking advantage of a GNU
      // Assembly feature to avoid polluting the global name space with
      // local labels
      // these may need to be included in the previous instr to preserve
      // ordering semantics, but for now this way they indent properly
      emitDIRECTIVE( ROOT, ".text 10\t@.section fixup");
      emitDIRECTIVE( ROOT, "\t.word 1f, "+retex+" @ (retaddr, handler)");
      emitDIRECTIVE( ROOT, ".text 0 \t@.section code");
      emitLABEL( ROOT, "1:", new Label("1")); 
    }
    /** Finish up a CALL or NATIVECALL. */
    private void emitCallEpilogue(INVOCATION ROOT,
				  Temp retval, int stackOffset) {
      // this will break if stackOffset > 255 (ie >63 args)
      Util.assert( stackOffset < 256, 
		   "Update the spec file to handle large SP offsets");
      emit( ROOT, "add `d0, `s0, #" + stackOffset, SP , SP );
      if (ROOT.retval.isDoubleWord()) {
	retval = makeTwoWordTemp(retval);
	// not certain an emitMOVE is legal with the l/h modifiers
	emit( ROOT, "mov `d0l, `s0", retval, r0 );
	emit( ROOT, "mov `d0h, `s0", retval, r1 );
      } else {
	retval = makeTemp(retval);
	emitMOVE( ROOT, "mov `d0, `s0", retval, r0 );
      }  
    }
%%
%start with %{
       // *** METHOD PROLOGUE *** 

       // initialize state variables each time gen() is called
       first = null; last = null;
       origTempToNewTemp = new HashMap();
       this.instrFactory = inf;

}%
%end with %{
       // *** METHOD EPILOGUE *** 
       Util.assert(first != null, "Should always generate some instrs");
       return first;
}%
    /* this comment will be eaten by the .spec processor (unlike comments above) */
	
/* EXPRESSIONS */ 
BINOP<p,i>(ADD, j, k) = i %{		
    Temp i = makeTemp();		
    emit( ROOT, "add `d0, `s0, `s1", i, j, k);
}%

BINOP<l>(ADD, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "adds `d0l, `s0l, `s1l\n"+
		"adc  `d0h, `s0h, `s1h", i, j, k );
}%

BINOP<f>(ADD, j, k) = i %{
    /* call auxillary fp routines */
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2( ROOT, "bl ___addsf", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<d>(ADD, j, k) = i %{
    /* call auxillary fp routines */
    Temp i = makeTwoWordTemp();		
        // not certain an emitMOVE is legal with the l/h modifiers
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___adddf3", // uses & stomps on these registers
	 new Temp[]{r0,r1,r2,r3,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<p,i>(AND, j, k) = i %{
    Temp i = makeTemp();		
    emit( ROOT, "and `d0, `s0, `s1", i, j, k );
}%

BINOP<l>(AND, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "and `d0l, `s0l, `s1l", i, j, k );
    emit( ROOT, "and `d0h, `s0h, `s1h", i, j, k );
}%

BINOP(CMPEQ, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"moveq `d0, #1\n"+
		"movne `d0, #0", i, j, k );
}%

BINOP(CMPEQ, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0l, `s1l\n"+
		"cmpeq `s0h, `s1h\n"+
		"moveq `d0, #1\n"+
		"movne `d0, #0", i, j, k );
}%
  
BINOP(CMPEQ, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr( instrFactory, ROOT, 
		    "mov `d1, `s1\n"+
		    "mov `d0, `s0\n"+
		    "bl ___eqsf2\n"+
		    "cmp `s2, #0\n"+
		    "moveq `d2, #1\n"+
		    "movne `d2, #0", 
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP(CMPEQ, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them

    // FSK: TODO: this is wrong, need to use the %extra detail added
    //      by Scott a while ago to request an additional register to
    //      store some temporary work into.  This occurs in other
    //      patterns too; basically I need to audit the SPEC file and
    //      revise a fair number of the patterns.
    emit(new Instr(instrFactory, ROOT,
		   "mov `d2, `s1l\n"+
		   "mov `d3, `s1h\n"+
		   "mov `d0, `s0l\n"+
		   "mov `d1, `s0h\n"+
		   "bl ___eqdf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d4, #1\n"+
		   "movne `d4, #0",
		   new Temp[]{ r0, r1, r2, r3, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP<p,i>(CMPGT, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(ROOT, "cmp `s0, `s1\n"+	
	       "movgt `d0, #1\n"+	
	       "movne `d0, #0", i, j, k );
}%

BINOP(CMPGT, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movgt `d0, #1\n"+
		"movle `d0, #0", i, j, k );
}%

BINOP(CMPGT, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d1, `s1\n"+
		   "mov `d0, `s0\n"+
		   "bl ___gtsf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP(CMPGT, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d2, `s1l\n"+
		   "mov `d3, `s1h\n"+
		   "mov `d0, `s0l\n"+
		   "mov `d1, `s0h\n"+
		   "bl ___gtdf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%


BINOP(CMPGE, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"movge `d0, #1\n"+
		"movlt `d0, #0", i, j, k );
}%

BINOP(CMPGE, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movge `d0, #1\n"+
		"movlt `d0, #0", i, j, k );
}%

BINOP(CMPGE, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d1, `s1\n"+
		   "mov `d0, `s0\n"+
		   "bl ___gesf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP(CMPGE, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d2, `s1l\n"+
		   "mov `d3, `s1h\n"+
		   "mov `d0, `s0l\n"+
		   "mov `d1, `s0h\n"+
		   "bl ___gedf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%


BINOP(CMPLE, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"movle `d0, #1\n"+
		"movgt `d0, #0", i, j, k );
}%

BINOP(CMPLE, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movle `d0, #1\n"+
		"movgt `d0, #0", i, j, k );
}%

BINOP(CMPLE, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d1, `s1\n"+
		   "mov `d0, `s0\n"+
		   "bl ___lesf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP(CMPLE, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d2, `s1l\n"+
		   "mov `d3, `s1h\n"+
		   "mov `d0, `s0l\n"+
		   "mov `d1, `s0h\n"+
		   "bl ___ledf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP(CMPLT, j, k) = i
%pred %( ROOT.operandType()==Type.POINTER || ROOT.operandType()==Type.INT )%
%{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0, `s1\n"+
		"movlt `d0, #1\n"+
		"movge `d0, #0", i, j, k );
}%

BINOP(CMPLT, j, k) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit( ROOT, "cmp `s0h, `s1h\n"+
		"cmpeq `s0l, `s1l\n"+
		"movlt `d0, #1\n"+
		"movge `d0, #0", i, j, k );
}%

BINOP(CMPLT, j, k) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d1, `s1\n"+
		   "mov `d0, `s0\n"+
		   "bl ___ltsf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP(CMPLT, j, k) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    // don't move these into seperate Instrs; there's an implicit
    // dependency on the condition register so we don't want to risk
    // reordering them
    emit(new Instr(instrFactory, ROOT,
		   "mov `d2, `s1l\n"+
		   "mov `d3, `s1h\n"+
		   "mov `d0, `s0l\n"+
		   "mov `d1, `s0h\n"+
		   "bl ___ltdf2\n"+
		   "cmp `s2, #0\n"+
		   "moveq `d2, #1\n"+
		   "movne `d2, #0",
		   new Temp[]{ r0, r1, i, LR },
		   new Temp[]{ j, k, r0 }));
}%

BINOP<p,i>(OR, j, k) = i %{
    Temp i = makeTemp();		
    emit( ROOT, "orr `d0, `s0, `s1", i, j, k );
}%

BINOP<l>(OR, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "orr `d0l, `s0l, `s1l", i, j, k );
    emit( ROOT, "orr `d0h, `s0h, `s1h", i, j, k );
}%

BINOP<p,i>(SHL, j, k) = i %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0, lsl `s1", i, j, k );
}%

BINOP<l>(SHL, j, k) = i %{
    Temp i = makeTwoWordTemp();
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit( ROOT, "mov `d0, `s0 ", r2, k );
    emit2(ROOT, "bl ___ashldi3", new Temp[]{r0,r1,r2,LR},new Temp[]{r0,r1,r2});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<p,i>(SHR, j, k) = i %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0, lsr `s1", i, j, k );
}%
BINOP<l>(SHR, j, k) = i %{
    Temp i = makeTwoWordTemp();
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit( ROOT, "mov `d0, `s0 ", r2, k );
    emit2(ROOT, "bl ___ashrdi3", new Temp[]{r0,r1,r2,LR},new Temp[]{r0,r1,r2});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%


BINOP<p,i>(USHR, j, k) = i %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0, asr `s1", i, j, k );
}%
BINOP<l>(USHR, j, k) = i %{
    Temp i = makeTwoWordTemp();
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit( ROOT, "mov `d0, `s0 ", r2, k );
    emit2(ROOT, "bl ___lshrdi3", new Temp[]{r0,r1,r2,LR},new Temp[]{r0,r1,r2});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%


BINOP<p,i>(XOR, j, k) = i %{
    Temp i = makeTemp();		
    emit( ROOT, "eor `d0, `s0, `s1", i, j, k );
}%
BINOP<l>(XOR, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "eor `d0l, `s0l, `s1l", i, j, k );
    emit( ROOT, "eor `d0h, `s0h, `s1h", i, j, k );
}%


CONST<l,d>(c) = i %{
    Temp i = makeTwoWordTemp();
    long val = (ROOT.type()==Type.LONG) ? ROOT.value.longValue()
	: Double.doubleToLongBits(ROOT.value.doubleValue());
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0l", (int)val, "lo("+ROOT.value+")"),
		    new Temp[]{ i }, null));
    val>>>=32;
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0h", (int)val, "hi("+ROOT.value+")"),
		    new Temp[]{ i }, null));
}% 

CONST<f,i>(c) = i %{
    Temp i = makeTemp();		
    int val = (ROOT.type()==Type.INT) ? ROOT.value.intValue()
	: Float.floatToIntBits(ROOT.value.floatValue());
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0", val, ROOT.value.toString()),
		    new Temp[]{ i }, null));
}%

CONST<p>(c) = i %{
    // the only CONST of type Pointer we should see is NULL
    Temp i = makeTemp();
    emit(new Instr( instrFactory, ROOT, 
		    "mov `d0, #0 @ null", new Temp[]{ i }, null));
}%

// these next three rules just duplicate the above three with MOVE at the root.
// they should probably be deleted once move collation is working in the
// register allocator.

MOVE(TEMP(dst), CONST<l,d>(c)) %{
    Temp i = makeTwoWordTemp(dst);
    CONST cROOT = (CONST) ROOT.src;
    long val = (cROOT.type()==Type.LONG) ? cROOT.value.longValue()
	: Double.doubleToLongBits(cROOT.value.doubleValue());
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0l", (int)val, "lo("+cROOT.value+")"),
		    new Temp[]{ i }, null));
    val>>>=32;
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0h", (int)val, "hi("+cROOT.value+")"),
		    new Temp[]{ i }, null));
}% 

MOVE(TEMP(dst), CONST<f,i>(c)) %{
    Temp i = makeTemp(dst);	
    CONST cROOT = (CONST) ROOT.src;
    int val = (cROOT.type()==Type.INT) ? cROOT.value.intValue()
	: Float.floatToIntBits(cROOT.value.floatValue());
    emit(new Instr( instrFactory, ROOT,
		    loadConst32("`d0", val, cROOT.value.toString()),
		    new Temp[]{ i }, null));
}%

MOVE(TEMP(dst), CONST<p>(c)) %{
    // the only CONST of type Pointer we should see is NULL
    Temp i = makeTemp(dst);
    emit(new Instr( instrFactory, ROOT, 
		    "mov `d0, #0 @ null", new Temp[]{ i }, null));
}%

BINOP<p,i>(MUL, j, k) = i %{
    Temp i = makeTemp();		
    emit( ROOT, "mul `d0, `s0, `s1", i, j, k );
}%

BINOP<l>(MUL, j, k) = i %{
    // TODO: use the SMULL instruction instead	     
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r1, j );
    emit( ROOT, "mov `d0, `s0h", r0, j );
    emit2(ROOT, "bl ___muldi3", // uses & stomps on these registers
	 new Temp[]{r0,r1,r2,r3,LR}, new Temp[]{r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<f>(MUL, j, k) = i %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___mulsf3", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<d>(MUL, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___muldf3", // uses & stomps on these registers
	 new Temp[] {r0,r1,r2,r3,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<p,i>(DIV, j, k) = i %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___divsi3", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<l>(DIV, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___divdi3",	// uses and stomps on these registers
	 new Temp[] {r0,r1,r2,r3,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<f>(DIV, j, k) = i %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___divsf3", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<d>(DIV, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___divdf3",
	 new Temp[] {r0,r1,r2,r3,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

BINOP<p,i>(REM, j, k) = i %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r1, k );
    emitMOVE( ROOT, "mov `d0, `s0", r0, j );
    emit2(    ROOT, "bl ___modsi3", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1});
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

BINOP<l>(REM, j, k) = i %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0, `s0l", r2, k );
    emit( ROOT, "mov `d0, `s0h", r3, k );
    emit( ROOT, "mov `d0, `s0l", r0, j );
    emit( ROOT, "mov `d0, `s0h", r1, j );
    emit2(ROOT, "bl ___moddi3",
	 new Temp[] {r0,r1,r2,r3,LR}, new Temp[] {r0,r1,r2,r3});
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%

// fix me: addressing mode for MEM is actually much richer than this.
// we can do offsets and scaling in same oper.

/* ACK! Our assembler doesn't support this, even though our processor does. =(
MEM<s:8,s:16,u:16>(e) = i %{ // addressing mode 3
    Temp i = makeTemp();
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
    Temp i = makeTemp();
    emit(new InstrMEM(instrFactory, ROOT, "ldrb `d0, [`s0] @ load signed byte",
		      new Temp[]{ i }, new Temp[]{ e }));
    emit( ROOT, "mov `d0, `s0, asl #24", i, i);
    emit( ROOT, "mov `d0, `s0, asr #24", i, i);
}%
MEM<s:16,u:16>(e) = i %{ /* hack. ARMv4 has a special instr for this. */
    Temp i = makeTemp();
    emit(new InstrMEM(instrFactory, ROOT, "ldr `d0, [`s0, #2] @ load halfword",
		      new Temp[]{ i }, new Temp[]{ e }));
    emit( ROOT, "mov `d0, `s0, asl #16", i, i);
    if (ROOT.signed())
	emit( ROOT, "mov `d0, `s0, asr #16", i, i);
    else
	emit( ROOT, "mov `d0, `s0, lsr #16", i, i);
}%
MEM<u:8,p,i,f>(e) = i %{ // addressing mode 2
    Temp i = makeTemp();		
    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0]",
		     new Temp[]{ i }, new Temp[]{ e }));
}%
MEM<u:8,p,i,f>(BINOP<p>(ADD, j, k)) = i %{ // addressing mode 2
    Temp i = makeTemp();		
    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, `s1]",
		     new Temp[]{ i }, new Temp[]{ j, k }));
}%
MEM<u:8,p,i,f>(BINOP(ADD, j, CONST<i,p>(c))) = i
%pred %( is12BitOffset(c) )%
%{
    Temp i = makeTemp();		
    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, #"+c+"]",
		     new Temp[]{ i }, new Temp[]{ j }));
}%
MEM<u:8,p,i,f>(BINOP(ADD, CONST<i,p>(c), j)) = i
%pred %( is12BitOffset(c) )%
%{
    Temp i = makeTemp();		
    String suffix="";
    if (ROOT.isSmall() && ROOT.signed()) suffix+="s";
    if (ROOT.isSmall() && ROOT.bitwidth()==8) suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
	             "ldr"+suffix+" `d0, [`s0, #"+c+"]",
		     new Temp[]{ i }, new Temp[]{ j }));
}%
MEM<l,d>(e) = i %{
    Temp i = makeTwoWordTemp();		
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
    Temp i = makeTemp();		
    Label target = new Label("2");
    emit( ROOT, "ldr `d0, 1f\n" +
		"b 2f", new Temp[]{ i }, null, false,
		Arrays.asList(new Label[]{ target }));
    // these may need to be included in the previous instr to preserve
    // ordering semantics, but for now this way they indent properly
    emitLABEL( ROOT, "1:", new Label("1"));
    emitDIRECTIVE( ROOT, "\t.word " + id);
    emitLABEL( ROOT, "2:", target);

}%

/* Not sure yet how to handle this 
MEM<f,i,p>(NAME(id)) = i %{
    Temp i = makeTemp();		
    emit(new Instr( instrFactory, ROOT,
		    "ldr `d0, " + id, 
		    new Temp[]{ i }, null ));
}%
MEM<d,l>(NAME(id)) = i %{
    Temp i = makeTwoWordTemp();		
    emit(new Instr( instrFactory, ROOT,
		    "ldr `d0l, " + id, 
		    new Temp[]{ i }, null ));
    emit(new Instr( instrFactory, ROOT,
		    "ldr `d0h, " + id + "+4", 
		    new Temp[]{ i }, null ));
}%
*/

TEMP<p,i,f>(id) = i %{
    Temp i = makeTemp( ROOT.temp );
}%
TEMP<l,d>(id) = i %{
    TwoWordTemp i = makeTwoWordTemp( ROOT.temp );		
}%


UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle long-to-byte conversion directly");
}%
UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle float-to-byte conversion directly");
}%
UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle double-to-byte conversion directly");
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle long-to-char conversion directly");
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle float-to-char conversion directly");
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle double-to-char conversion directly");
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle long-to-short conversion directly");
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle float-to-short conversion directly");
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    Util.assert(false, "Spec file doesn't handle double-to-short conversion directly");
}%


UNOP(_2B, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0, asl #24", i, arg);
    emit( ROOT, "mov `d0, `s0, asr #24", i, i);
}%
UNOP(_2C, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0, asl #16", i, arg);
    emit( ROOT, "mov `d0, `s0, lsr #16", i, i);
}%
UNOP(_2S, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0, asl #16", i, arg);
    emit( ROOT, "mov `d0, `s0, asr #16", i, i);
}%


UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    TwoWordTemp i = makeTwoWordTemp();
    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___floatdidf", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%
UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
    TwoWordTemp i = makeTwoWordTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(ROOT, "bl ___floatsidf", new Temp[] {r0,r1,LR}, new Temp[] {r0} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%
UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTwoWordTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(ROOT, "bl ___extendsfdf2", new Temp[] {r0,r1,LR}, new Temp[] {r0} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );

}%
/* this is useless.  Should never really be in Tree form.
UNOP(_2D, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
	// a move, basically.
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0l, `s0l @ unop d2d", i, arg );
    emit( ROOT, "mov `d0h, `s0h @ unop d2d", i, arg );
}%
*/

UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___floatdisf", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(    ROOT, "bl ___floatsisf", new Temp[] {r0,LR},new Temp[] {r0} );   
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
/* useless.  should never really be in tree form.
UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", i, arg );
}%
*/
UNOP(_2F, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___truncdfsf2", new Temp[] {r0,r1,LR},new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0l", i, arg );
}%
UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.POINTER )% %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", i, arg );
}%
UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(    ROOT, "bl ___fixsfsi", new Temp[] {r0,LR}, new Temp[] {r0} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
UNOP(_2I, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___fixdfsi", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%

/* useless.  should never really be in tree form.
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0l, `s0l @ unop l2l", i, arg );
    emit( ROOT, "mov `d0h, `s0h", i, arg );
}%
*/
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0l, `s0", i, arg );
    emit( ROOT, "mov `d0h, `s0l asr #31", i, i );
}%
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTwoWordTemp();	
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(ROOT, "bl ___fixsfdi", new Temp[] {r0,r1,LR}, new Temp[] {r0} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );
}%
UNOP(_2L, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )% %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___fixdfdi", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );	 
}%


UNOP(NEG, arg) = i
%pred %( ROOT.operandType()==Type.INT || ROOT.operandType()==Type.POINTER )%
%{
    Temp i = makeTemp();		
    emit( ROOT, "rsb `d0, `s0, #0", i, arg );
}% 
UNOP(NEG, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "rsbs `d0l, `s0l\n" + // uses condition codes, so keep together
    	        "rsc  `d0h, `s0h", i, arg );
}% 
UNOP(NEG, arg) = i %pred %( ROOT.operandType()==Type.FLOAT )% %{
    Temp i = makeTemp();		
    emitMOVE( ROOT, "mov `d0, `s0", r0, arg );
    emit2(    ROOT, "bl ___negsf2", new Temp[] {r0,LR}, new Temp[] {r0} );
    emitMOVE( ROOT, "mov `d0, `s0", i, r0 );
}%
UNOP(NEG, arg) = i %pred %( ROOT.operandType()==Type.DOUBLE )%
%{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mov `d0, `s0l", r0, arg );
    emit( ROOT, "mov `d0, `s0h", r1, arg );
    emit2(ROOT, "bl ___negdf2", new Temp[] {r0,r1,LR}, new Temp[] {r0,r1} );
    emit( ROOT, "mov `d0l, `s0", i, r0 );
    emit( ROOT, "mov `d0h, `s0", i, r1 );	 
}%

UNOP(NOT, arg) = i %pred %( ROOT.operandType()==Type.INT )% %{
    Temp i = makeTemp();		
    emit( ROOT, "mvn `d0, `s0", i, arg );
}% 
UNOP(NOT, arg) = i %pred %( ROOT.operandType()==Type.LONG )% %{
    Temp i = makeTwoWordTemp();		
    emit( ROOT, "mvn `d0l, `s0l", i, arg );
    emit( ROOT, "mvn `d0h, `s0h", i, arg );
}% 

/* STATEMENTS */
METHOD(params) %{


}%

CJUMP(test, iftrue, iffalse) %{
    Instr j1 = emit( ROOT, "cmp `s0, #0 \n" +
			   "beq `L0", 
			   null, new Temp[]{ test },
			   new Label[]{ iffalse });
    Instr j2 = emitJUMP( ROOT, "b `L0", iftrue );
}%

EXP(e) %{
			/* this is a statement that's just an
			   expression; just throw away 
			   calculated value */
}%

JUMP(e) %{
    List labelList = LabelList.toList( ROOT.targets );
    Instr j = 
       emit(new Instr( instrFactory, ROOT, 
		       "mov `d0, `s0",
		       new Temp[]{ PC },
		       new Temp[]{ e },
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
    emitMOVE( ROOT, "mov `d0, `s0", dst, src );
}%

MOVE<d,l>(TEMP(dst), src) %{
    dst = makeTwoWordTemp(dst);
    Util.assert( dst instanceof TwoWordTemp, "why is dst: "+dst + 
		 " a normal Temp? " + harpoon.IR.Tree.Print.print(ROOT));

    Util.assert(src instanceof TwoWordTemp, "why is src: "+src + 
		 " a normal Temp? " + harpoon.IR.Tree.Print.print(ROOT));
        // not certain an emitMOVE is legal with the l/h modifiers
    emit( ROOT, "mov `d0l, `s0l\n"+
		    "mov `d0h, `s0h", dst, src );
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
    if (((MEM)ROOT.dst).isSmall() && ((MEM)ROOT.dst).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1]",
		      null, new Temp[]{ src, d }));   
}%
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, d1, d2)), src) %{ // addressing mode 2
    String suffix="";
    if (((MEM)ROOT.dst).isSmall() && ((MEM)ROOT.dst).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1, `s2]",
		      null, new Temp[]{ src, d1, d2 }));   
}%
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, d, CONST<i,p>(c))), src)
%pred %( is12BitOffset(c) )%
%{
    String suffix="";
    if (((MEM)ROOT.dst).isSmall() && ((MEM)ROOT.dst).bitwidth()==8)
	 suffix+="b";
    emit(new InstrMEM(instrFactory, ROOT,
		      "str"+suffix+" `s0, [`s1, #"+c+"]",
		      null, new Temp[]{ src, d }));   
}%
MOVE(MEM<s:8,u:8,p,i,f>(BINOP<p>(ADD, CONST<i,p>(c), d)), src)
%pred %( is12BitOffset(c) )%
%{
    String suffix="";
    if (((MEM)ROOT.dst).isSmall() && ((MEM)ROOT.dst).bitwidth()==8)
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

RETURN(val) %{
    emitMOVE( ROOT, "mov `d0, `s0", r0, val );
    emit(new InstrMEM( instrFactory, ROOT, 
		       "ldmea `s0, { `d0, `d1, `d2 } @ RETURN",
		       new Temp[]{ FP, SP, PC },
		       new Temp[]{ FP },
		       false, null));
}%


THROW(val, handler) %{
    emitMOVE( ROOT, "mov `d0, `s0", r0, val );
    emit( ROOT, "bl _lookup @ (only r0 & fp are preserved during lookup)",
	         new Temp[] { r1, r2, r3, r4, r5, r6, LR }, // clobbers
		 new Temp[] { FP }, true, null); 
    emit(new InstrMEM( instrFactory, ROOT, 
		       "ldmea `s0, { `d0, `d1, `d2 } @ THROW",
		       new Temp[]{ FP, SP, PC },
		       new Temp[]{ FP },
		       false, null));
}%

  // slow version when we don't know exactly which method we're calling.
CALL(TEMP(retval), NAME(retex), func, arglist) %{
    int stackOffset = emitCallPrologue(ROOT, arglist);
    // next two instructions are *not* InstrMOVEs, as they have side-effects
    emit( ROOT, "mov `d0, `s0", LR, PC );
    emit( ROOT, "mov `d0, `s0", new Temp[]{ PC }, new Temp[]{ func }, 
	        new Label[] { retex } );
    // okay, clean up from call.
    emitCallFixup(ROOT, retex);
    emitCallEpilogue(ROOT, retval, stackOffset);
}%
  // optimized version when we know exactly which method we're calling.
CALL(TEMP(retval), NAME(retex), NAME(funcLabel), arglist) %{
    int stackOffset = emitCallPrologue(ROOT, arglist);
    // do the call.  bl has a 24-bit offset field, which should be plenty.
    emit( ROOT, "bl "+funcLabel, new Temp[] { LR }, new Temp[0],
                new Label[] { retex } );
    // okay, clean up from call.
    emitCallFixup(ROOT, retex);
    emitCallEpilogue(ROOT, retval, stackOffset);
}%
  // slow version when we don't know exactly which method we're calling.
NATIVECALL(TEMP(retval), func, arglist) %{
    int stackOffset = emitCallPrologue(ROOT, arglist);
    // next two instructions are *not* InstrMOVEs, as they have side-effects
    emit( ROOT, "mov `d0, `s0", LR, PC );
    emit( ROOT, "mov `d0, `s0", PC, func );
    // clean up.
    emitCallEpilogue(ROOT, retval, stackOffset);
}%
  // optimized version when we know exactly which method we're calling.
NATIVECALL(TEMP(retval), NAME(funcLabel), arglist) %{
    int stackOffset = emitCallPrologue(ROOT, arglist);
    // do the call.  bl has a 24-bit offset field, which should be plenty.
    emit( ROOT, "bl "+funcLabel, new Temp[] { LR }, new Temp[0], true, null );
    // clean up.
    emitCallEpilogue(ROOT, retval, stackOffset);
}%

DATA(CONST<i,f>(exp)) %{
    int i = (ROOT.data.type()==Type.INT) ? exp.intValue()
		: Float.floatToIntBits(exp.floatValue());
    String lo = "0x"+Integer.toHexString(i);
    emitDIRECTIVE( ROOT, "\t.word "+lo+" @ "+exp);
}%

DATA(CONST<l,d>(exp)) %{
    long l = (ROOT.data.type()==Type.LONG) ? exp.longValue()
		: Double.doubleToLongBits(exp.doubleValue());
    String lo = "0x"+Integer.toHexString((int)l);
    String hi = "0x"+Integer.toHexString((int)(l>>32));
    emitDIRECTIVE( ROOT, "\t.word "+lo+" @ lo("+exp+")");
    emitDIRECTIVE( ROOT, "\t.word "+hi+" @ hi("+exp+")");
}%

DATA(CONST<p>(exp)) %{
    emitDIRECTIVE( ROOT, "\t.word 0 @ null pointer constant");
}%

DATA(CONST<s:8,u:8>(exp)) %{
    String chardesc = (exp.intValue()>=32 && exp.intValue()<127) ?
	("\t@ char "+((char)exp.intValue())) : "";
    emitDIRECTIVE( ROOT, "\t.byte "+exp+chardesc);
}%

DATA(CONST<s:16,u:16>(exp)) %{
    String chardesc = (exp.intValue()>=32 && exp.intValue()<127) ?
	("\t@ char "+((char)exp.intValue())) : "";
    emitDIRECTIVE( ROOT, "\t.short "+exp+chardesc);
}%

DATA(NAME(l)) %{
    emitDIRECTIVE( ROOT, "\t.word "+l);
}%

ALIGN(n) %{
    emitDIRECTIVE( ROOT, "\t.align "+n);
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
