// THROW.java, created Thu Feb 18 16:59:53 1999 by duncan
// Copyright (C) 1998 Duncan Bryce  <duncan@lcs.mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.IR.Tree;

import harpoon.ClassFile.HCodeElement;
import harpoon.Temp.CloningTempMap;
import harpoon.Util.Util;

/**
 * <code>THROW</code> objects are used to represent a thrown exception.
 *
 * @author   Duncan Bryce  <duncan@lcs.mit.edu>, based on
 *          <i>Modern Compiler Implementation in Java</i> by Andrew Appel.
 * @version  $Id: THROW.java,v 1.1.2.11 1999-10-19 19:53:10 cananian Exp $
 */
public class THROW extends Stm implements Typed {
    /** The exceptional value to return */
    public Exp retex;
    /** The location of the exception-handling code */
    public Exp handler;

    /** Constructor 
     *  @param retex   the exceptional value to return 
     *  @param handler the location of the exception-handling code to branch to
     */
    public THROW(TreeFactory tf, HCodeElement source, 
		 Exp retex, Exp handler) {
	super(tf, source, 0);
	this.retex=retex;
	this.handler=handler;
	Util.assert(retex.type()==POINTER); 
	Util.assert(handler.type()==POINTER);
	Util.assert(tf == retex.tf, "This and Retex must have same tree factory");
	Util.assert(tf == handler.tf, "This and Handler must have the same tree factory");
    }		
  
    public ExpList kids() { return new ExpList
				(retex, new ExpList(handler, null)); }
    public int kind() { return TreeKind.THROW; }

    public Stm build(ExpList kids) { return build(tf, kids); } 
    public Stm build(TreeFactory tf, ExpList kids) { 
	Util.assert(tf == kids.head.tf);
	Util.assert(tf == kids.tail.head.tf);
	return new THROW(tf, this, kids.head, kids.tail.head);
    }

    /** Accept a visitor */
    public void accept(TreeVisitor v) { v.visit(this); }

    public Tree rename(TreeFactory tf, CloningTempMap ctm) {
	return new THROW
	    (tf,this,(Exp)retex.rename(tf,ctm),(Exp)handler.rename(tf,ctm));
    }

    /** @return <code>Type.POINTER</code> */
    public int type() { return POINTER; }
    public boolean isDoubleWord() { return Type.isDoubleWord(tf, POINTER); }
    public boolean isFloatingPoint() { return false; }
    
    public String toString() {
	return "THROW(#"+retex.getID()+", "+handler.getID()+")";
    }
}
