// DataClaz.java, created Mon Oct 11 12:01:55 1999 by cananian
// Copyright (C) 1999 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Backend.Runtime1;

import harpoon.Analysis.ClassHierarchy;
import harpoon.Backend.Generic.Frame;
import harpoon.Backend.Maps.MethodMap;
import harpoon.Backend.Maps.NameMap;
import harpoon.ClassFile.HClass;
import harpoon.ClassFile.HConstructor;
import harpoon.ClassFile.HDataElement;
import harpoon.ClassFile.HMethod;
import harpoon.IR.Tree.Stm;
import harpoon.IR.Tree.ALIGN;
import harpoon.IR.Tree.CONST;
import harpoon.IR.Tree.DATA;
import harpoon.IR.Tree.LABEL;
import harpoon.IR.Tree.NAME;
import harpoon.IR.Tree.SEGMENT;
import harpoon.Util.HClassUtil;
import harpoon.Util.Util;

import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.ListIterator;
import java.util.Iterator;
import java.util.Set;
/**
 * <code>DataClaz</code> lays out the claz tables, including the
 * interface and class method dispatch tables.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: DataClaz.java,v 1.1.4.4 1999-10-20 07:05:57 cananian Exp $
 */
public class DataClaz extends Data {
    final TreeBuilder m_tb;
    final NameMap m_nm;
    
    /** Creates a <code>ClassData</code>. */
    public DataClaz(Frame f, HClass hc, ClassHierarchy ch) {
        super("class-data", hc, f);
	this.m_nm = f.getRuntime().nameMap;
	this.m_tb = (TreeBuilder) f.getRuntime().treeBuilder;
	this.root = build(hc, ch);
    }

    private HDataElement build(HClass hc, ClassHierarchy ch) {
	List stmlist = new ArrayList();
	// write the appropriate segment header
	stmlist.add(new SEGMENT(tf, null, SEGMENT.CLASS));
	// align things on word boundary.
	stmlist.add(new ALIGN(tf, null, 4));
	// first comes the interface method table.
	if (!hc.isInterface()) {
	    Stm s = interfaceMethods(hc, ch);
	    if (s!=null) stmlist.add(s);
	}
	// this is where the class pointer points.
	stmlist.add(new LABEL(tf, null, m_nm.label(hc), true));
	// class info points at a class object for this class
	// (which is generated in DataReflection1)
	stmlist.add(_DATA(m_nm.label(hc, "classobj")));
	// component type pointer.
	if (hc.isArray())
	    stmlist.add(_DATA(m_nm.label(hc.getComponentType())));
	else
	    stmlist.add(_DATA(new CONST(tf, null)));
	// the interface list is generated elsewhere
	stmlist.add(_DATA(m_nm.label(hc, "interfaces")));
	// class depth.
	int depth = m_tb.cdm.classDepth(hc);
	stmlist.add(_DATA(new CONST(tf, null, m_tb.POINTER_SIZE * depth)));
	// class display
	stmlist.add(display(hc, ch));
	// now class method table.
	if (!hc.isInterface()) {
	    Stm s = classMethods(hc, ch);
	    if (s!=null) stmlist.add(s);
	}
	return (HDataElement) Stm.toStm(stmlist);
    }

    /** Make class display table. */
    private Stm display(HClass hc, ClassHierarchy ch) {
	List clslist = new ArrayList();
	// we're going to build the list top-down and then reverse it.
	if (hc.isArray()) { // arrays are special.
	    HClass base = HClassUtil.baseClass(hc);
	    int dims = HClassUtil.dims(hc);
	    
	    // first step down the base class inheritance hierarchy.
	    for (HClass hcp = base; hcp!=null; hcp=hcp.getSuperclass())
		clslist.add(HClassUtil.arrayClass(hcp, dims));
	    // now down the Object array hierarchy.
	    HClass hcO = HClass.forName("java.lang.Object");
	    for (dims--; dims>=0; dims--)
		clslist.add(HClassUtil.arrayClass(hcO, dims));
	    // done.
	} else if (!hc.isInterface()) { // step down the inheritance hierarchy.
	    for (HClass hcp = hc; hcp!=null; hcp=hcp.getSuperclass())
		clslist.add(hcp);
	}
	// now reverse list.
	Collections.reverse(clslist);
	// okay, root should always be java.lang.Object.
	Util.assert(hc.isInterface() || hc.isPrimitive() ||
		    clslist.get(0)==HClass.forName("java.lang.Object"));
	// make statements.
	List stmlist = new ArrayList(m_tb.cdm.maxDepth());
	for (Iterator it=clslist.iterator(); it.hasNext(); )
	    stmlist.add(_DATA(m_nm.label((HClass)it.next())));
	while (stmlist.size() < m_tb.cdm.maxDepth())
	    stmlist.add(_DATA(new CONST(tf, null))); // pad with nulls.
	return Stm.toStm(stmlist);
    }
    /** Make class methods table. */
    private Stm classMethods(HClass hc, ClassHierarchy ch) {
	// collect all the methods.
	List methods = new ArrayList(Arrays.asList(hc.getMethods()));
	// weed out non-virtual methods.
	for (Iterator it=methods.iterator(); it.hasNext(); ) {
	    HMethod hm = (HMethod) it.next();
	    if (hm.isStatic() || hm instanceof HConstructor ||
		Modifier.isPrivate(hm.getModifiers()))
		it.remove();
	}
	// sort the methods using class method map.
	final MethodMap cmm = m_tb.cmm;
	Collections.sort(methods, new Comparator() {
	    public int compare(Object o1, Object o2) {
		HMethod hm1 = (HMethod) o1, hm2 = (HMethod) o2;
		int i1 = cmm.methodOrder(hm1);
		int i2 = cmm.methodOrder(hm2);
		return i1 - i2;
	    }
	});
	// make stms.
	List stmlist = new ArrayList(methods.size());
	Set callable = ch.callableMethods();
	int order=0;
	for (Iterator it=methods.iterator(); it.hasNext(); order++) {
	    HMethod hm = (HMethod) it.next();
	    Util.assert(cmm.methodOrder(hm)==order); // should be no gaps.
	    if (callable.contains(hm))
		stmlist.add(_DATA(m_nm.label(hm)));
	    else
		stmlist.add(_DATA(new CONST(tf, null))); // null pointer
	}
	return Stm.toStm(stmlist);
    }
    /** Make interface methods table. */
    private Stm interfaceMethods(HClass hc, ClassHierarchy ch) {
	// collect all interfaces implemented by this class
	Set interfaces = new HashSet();
	for (HClass hcp=hc; hcp!=null; hcp=hcp.getSuperclass())
	    interfaces.addAll(Arrays.asList(hcp.getInterfaces()));
	interfaces.retainAll(ch.classes());
	// all methods included in these interfaces.
	Set methods = new HashSet();
	for (Iterator it=interfaces.iterator(); it.hasNext(); )
	    methods.addAll(Arrays.asList(((HClass)it.next()).getMethods()));
	methods.retainAll(ch.callableMethods());
	// double-check that these are all interface methods
	for (Iterator it=methods.iterator(); it.hasNext(); )
	    Util.assert(((HMethod)it.next()).isInterfaceMethod());
	// remove duplicates (two methods with same signature)
	Set sigs = new HashSet();
	for (Iterator it=methods.iterator(); it.hasNext(); ) {
	    HMethod hm = (HMethod) it.next();
	    String sig = hm.getName() + hm.getDescriptor();
	    if (sigs.contains(sig)) it.remove();
	    else sigs.add(sig);
	}
	// okay, now sort by InterfaceMethodMap ordering.
	final MethodMap imm = m_tb.imm;
	List ordered = new ArrayList(methods);
	Collections.sort(ordered, new Comparator() {
	    public int compare(Object o1, Object o2) {
		HMethod hm1 = (HMethod) o1, hm2 = (HMethod) o2;
		int i1 = imm.methodOrder(hm1);
		int i2 = imm.methodOrder(hm2);
		return i1 - i2;
	    }
	});
	// okay, output in reverse order:
	List stmlist = new ArrayList(ordered.size());
	int last_order = -1;
	for (ListIterator it=ordered.listIterator(ordered.size());
	     it.hasPrevious(); ) {
	    HMethod hm = (HMethod) it.previous();
	    int this_order = imm.methodOrder(hm);
	    if (last_order!=-1) {
		Util.assert(this_order < last_order); // else not ordered
		for (int i=last_order-1; i > this_order; i--)
		    stmlist.add(_DATA(new CONST(tf, null))); // null
	    }
	    // look up name of class method with this signature
	    HMethod cm = hc.getMethod(hm.getName(), hm.getDescriptor());
	    // add entry for this method to table.
	    stmlist.add(_DATA(m_nm.label(cm)));
	    last_order = this_order;
	}
	if (last_order!=-1) {
	    Util.assert(last_order>=0);
	    for (int i=last_order; i > 0; i--)
		stmlist.add(_DATA(new CONST(tf, null)));
	}
	// done!
	return Stm.toStm(stmlist);
    }
}
