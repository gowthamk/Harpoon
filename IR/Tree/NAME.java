// NAME.java, created Wed Jan 13 21:14:57 1999 by cananian
// Copyright (C) 1998 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.IR.Tree;

import harpoon.ClassFile.HCodeElement;
import harpoon.Temp.CloningTempMap;
import harpoon.Temp.Label;
import harpoon.Util.Util;

/**
 * <code>NAME</code> objects are expressions which stand for symbolic
 * constants.  They usually correspond to some assembly language label
 * in the code or data segment.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>, based on
 *          <i>Modern Compiler Implementation in Java</i> by Andrew Appel.
 * @version $Id: NAME.java,v 1.1.2.15 2000-01-09 01:04:41 duncan Exp $
 */
public class NAME extends Exp implements harpoon.ClassFile.HDataElement {
    /** The label which this NAME refers to. */
    public final Label label;
    /** Constructor. */
    public NAME(TreeFactory tf, HCodeElement source,
		Label label) {
	super(tf, source);
	this.label=label;
	Util.assert(label!=null);
    }
    
    public Tree getFirstChild() { return null; } 
    
    public int kind() { return TreeKind.NAME; }
	
    public Exp build(ExpList kids) { return build(tf, kids); } 
    public Exp build(TreeFactory tf, ExpList kids) { 
	return new NAME(tf, this, label); 
    }

    /** Accept a visitor */
    public void accept(TreeVisitor v) { v.visit(this); }

    public Tree rename(TreeFactory tf, CloningTempMap ctm) {
        return new NAME(tf, this, this.label);
    }

    /** @return <code>Type.POINTER</code> */
    public int type() { return POINTER; }
    
    public String toString() {
        return "NAME("+label+")";
    }
}

