// Code.java, created Mon Feb  8 16:55:15 1999 by duncan
// Copyright (C) 1998 Duncan Bryce <duncan@lcs.mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.IR.Tree;

import harpoon.Analysis.Maps.Derivation;
import harpoon.Analysis.Maps.Derivation.DList;
import harpoon.Analysis.Maps.TypeMap;
import harpoon.Backend.Generic.Frame;
import harpoon.ClassFile.HClass;
import harpoon.ClassFile.HCode;
import harpoon.ClassFile.HCodeAndMaps;
import harpoon.ClassFile.HCodeElement;
import harpoon.ClassFile.HMethod;
import harpoon.IR.Properties.CFGrapher; 
import harpoon.IR.Properties.UseDefer;
import harpoon.Util.ArrayFactory;
import harpoon.Util.Util;
import harpoon.Temp.LabelList;
import harpoon.Temp.Temp;
import harpoon.Temp.TempFactory;
import harpoon.Temp.TempMap;
import harpoon.Util.UnmodifiableIterator;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Set;
import java.util.Stack;

/**
 * <code>Tree.Code</code> is an abstract superclass of codeviews
 * using the components in <code>IR.Tree</code>.  It implements
 * shared methods for the various codeviews using <code>Tree</code>s.
 * 
 * @author  Duncan Bryce <duncan@lcs.mit.edu>
 * @version $Id: Code.java,v 1.1.2.51 2000-10-06 21:20:43 cananian Exp $
 */
public abstract class Code extends HCode {
    /** The Tree Objects composing this code view. */
    protected Tree tree;

    /** The Frame containing machine-specific information*/
    protected /* final */ Frame frame;

    /** Tree factory. */
    protected /* final */ TreeFactory tf;

    /** The method that this code view represents. */
    protected /* final */ HMethod parent;

    /** Create a proper TreeFactory. */
    public class TreeFactory extends harpoon.IR.Tree.TreeFactory {
	private int id=0;
	private final TempFactory tempf;
	TreeFactory(String scope) { this.tempf = Temp.tempFactory(scope); }
	public TempFactory tempFactory() { return tempf; }
	/** Returns the <code>HCode</code> to which all <code>Exp</code>s and
	 *  <code>Stm</code>s generated by this factory belong. */
	public Code getParent() { return Code.this; }
	/** Returns the <code>HMethod</code> to which all <code>Exp</code>s and
	 *  <code>Stm</code>s generated by this factory belong. */
	public HMethod getMethod() { return Code.this.getMethod(); }
	public Frame getFrame() { return Code.this.frame; } 
	synchronized int getUniqueID() { return id++; }
	public String toString() { 
	    return "Code.TreeFactory["+getParent().toString()+"]"; 
	}
	public int hashCode() { return Code.this.hashCode(); }
    }

    /** constructor. */
    protected Code(final HMethod parent, final Tree tree, 
		   final Frame frame) {
	final String scope = parent.getDeclaringClass().getName() + "." +
	    parent.getName() + parent.getDescriptor() + "/" + getName();

	this.parent = parent;
	this.tree   = tree;
	this.frame  = frame;
	this.tf     = new TreeFactory(scope);
    }
  
    /** Clone this code representation. The clone has its own copy
     *  of the Tree */
    public abstract HCodeAndMaps clone(HMethod newMethod, Frame frame);
    /** Helps to create a proper <code>HCodeAndMaps</code> during cloning */
    protected final HCodeAndMaps cloneHelper(final Code tc, 
					     final DerivationGenerator dg) {
	final Tree.CloneCallback ccb =
	    (dg==null) ? null : dg.cloneCallback(getTreeDerivation());
	final Map o2nTree = new HashMap(), n2oTree = new HashMap();
	final Map o2nTemp = new HashMap(), n2oTemp = new HashMap();
	tc.tree = Tree.clone(tc.tf, tree, new Tree.CloneCallback() {
	    public Tree callback(Tree o, Tree n, TempMap tm) {
		if (ccb!=null) n = ccb.callback(o, n, tm);
		o2nTree.put(o, n); n2oTree.put(n, o);
		if (n instanceof TEMP) {
		    Temp oT = ((TEMP)o).temp, nT = ((TEMP)n).temp;
		    o2nTemp.put(oT, nT); n2oTemp.put(nT, oT);
		}
		return n;
	    }
	});
	final Map o2nTreeIM = Collections.unmodifiableMap(o2nTree);
	final Map n2oTreeIM = Collections.unmodifiableMap(n2oTree);
	final TempMap o2nTempIM = new TempMap() {
	    public Temp tempMap(Temp t) { return (Temp) o2nTemp.get(t); }
	};
	final TempMap n2oTempIM = new TempMap() {
	    public Temp tempMap(Temp t) { return (Temp) n2oTemp.get(t); }
	};
	return new HCodeAndMaps() {
	    public HCode hcode() { return tc; }
	    public Map elementMap() { return o2nTreeIM; }
	    public TempMap tempMap() { return o2nTempIM; }
	    public HCode ancestorHCode() { return Code.this; }
	    public Map ancestorElementMap() { return n2oTreeIM; }
	    public TempMap ancestorTempMap() { return n2oTempIM; }
	};
    }
    /** Clone this code representation. The clone has its own copy
     *  of the Tree */
    public final HCodeAndMaps clone(HMethod newMethod) {
	return clone(newMethod, frame);
    }

    /** Returns a means to externally associate control flow with this
     *  tree code.  If this tree code is modified subsequent to a call
     *  to <code>getGrapher()</code>, the grapher is invalid, this method
     *  should be re-invoked to acquire a new grapher.  
     */ 
    public CFGrapher getGrapher() { return new TreeGrapher(this); }
    /** Returns a means to externally associate use/def information with
     *  this tree code. MOVE(TEMP(t), ...) and CALL/NATIVECALLs are treated
     *  as defs; all instances of TEMP in any of the subtrees returned
     *  by the <code>kids()</code> method are considered uses. Not
     *  valid for non-canonical forms. */
    public UseDefer getUseDefer() { return new TreeUseDefer(this); }

    /** Return the name of this code view. */
    public abstract String getName();
    
    /** Return the <code>HMethod</code> this codeview
     *  belongs to.  */
    public HMethod getMethod() { return this.parent; }

    public Frame getFrame() { return this.frame; }

    public abstract TreeDerivation getTreeDerivation();

    /** Returns the root of the Tree */
    public HCodeElement getRootElement() { 
	// Ensures that the root is a SEQ, and the first instruction is 
	// a SEGMENT.
	Tree first = (SEQ)this.tree;
	while(first.kind()==TreeKind.SEQ) first = ((SEQ)first).getLeft(); 
	Util.assert(first.kind()==TreeKind.SEGMENT); 
	return this.tree; 
    }

    /** Returns the leaves of the Tree */
    public HCodeElement[] getLeafElements() {
	// what exactly does 'leaf elements' *mean* in this context?
	return new Tree[0];
    }
  
    /**
     * Returns an ordered list of the <code>Tree</code> Objects
     * making up this code view.  The root of the tree
     * is in element 0 of the array.
     */
    public HCodeElement[] getElements() {
	return super.getElements();
    }

    /** 
     * Returns an <code>Iterator</code> of the <code>Tree</code> Objects 
     * making up this code view.  The root of the tree is the first element
     * of the Iterator.  Returns the elements of the tree in depth-first
     * pre-order.
     */
    public Iterator getElementsI() { 
	return new UnmodifiableIterator() {
	    Stack stack = new Stack(), aux = new Stack(); 
	    {   // initialize stack/set
		stack.push(getRootElement());
	    }
	    public boolean hasNext() { return !stack.isEmpty(); }
	    public Object next() {
		if (stack.isEmpty()) throw new NoSuchElementException();
		Tree t = (Tree) stack.pop();
		// Push successors on stack before returning
		// (reverse the order twice to get things right)
		for (Tree tp = t.getFirstChild(); tp!=null; tp=tp.getSibling())
		    aux.push(tp);
		while (!aux.isEmpty())
		    stack.push(aux.pop()); //LIFO twice.
		return t;
	    }
	};
    }
  
    // implement elementArrayFactory which returns Tree[]s.  
    public ArrayFactory elementArrayFactory() { return Tree.arrayFactory; }

    public void print(java.io.PrintWriter pw) {
	Print.print(pw,this);
    } 

    /** 
     * Returns true if this codeview is a canonical representation
     */
    public abstract boolean isCanonical();

    /** 
     * Removes the specified <code>Stm</code> from the tree in which it 
     * resides.
     * 
     * <br><b>Requires:</b>
     * <ol>
     *   <li><code>stm</code> is not of type <code>SEQ</code>. 
     *   <li><code>stm.getParent()</code> must be of type <code>SEQ</code>. 
     *   <li><code>stm</code> is an element of this codeview. 
     *   <li><code>stm</code> is not the root element of this codeview.
     * </ol>
     * <br><b>Effects:</b>
     *   Removes <code>stm</code> from this tree.
     */
    public void remove(Stm stm) { 
	Util.assert(stm.kind() != TreeKind.SEQ); 
	Util.assert(stm.getFactory() == this.tf); 
	Util.assert(this.tf.getParent() == this); 
	
	// All predecessors in canonical tree form must be SEQs
	SEQ pred = (SEQ)stm.getParent();
	Stm newPred;

	if      (pred.getLeft()==stm)  { newPred = pred.getRight(); } 
	else if (pred.getRight()==stm) { newPred = pred.getLeft(); } 
	else { throw new Error("Invalid tree form!"); }

	if (pred.getParent() == null) { 
	    // Pred has no parents, it must be the root of the tree. 
	    Util.assert(pred == this.tree); 
	    this.tree         = newPred; 
	    this.tree.unlink();
	}
	else { 
	    pred.replace(newPred); 
	}
    }
}


