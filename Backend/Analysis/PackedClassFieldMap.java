// PackedClassFieldMap.java, created Wed Jul 11 20:26:56 2001 by cananian
// Copyright (C) 2000 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Backend.Analysis;

import harpoon.Backend.Maps.FieldMap;
import harpoon.ClassFile.HClass;
import harpoon.ClassFile.HField;
import harpoon.Util.Util;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.ListIterator;
import java.util.Map;
/**
 * <code>PackedClassFieldMap</code> is a <code>FieldMap</code> for
 * non-static fields of a class which attempts to maximally fill holes
 * in the data structure (even if this means commingling a subclass'
 * fields with those of its superclass) in order to minimize the
 * space required by objects.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: PackedClassFieldMap.java,v 1.1.2.1 2001-07-12 02:04:10 cananian Exp $
 */
public abstract class PackedClassFieldMap extends FieldMap {
    /** Creates a <code>PackedClassFieldMap</code>. */
    public PackedClassFieldMap() { /* no special initialization */ }
    
    /** Return an offset to the given field. */
    public int fieldOffset(HField hf) {
	Util.assert(!hf.isStatic());
	if (!fieldcache.containsKey(hf)) do_one(hf.getDeclaringClass());
	Util.assert(fieldcache.containsKey(hf));
	return ((Integer) fieldcache.get(hf)).intValue();
    }
    /** Return an unmodifiable List over all appropriate fields in the given
     *  class, in order from smallest to largest offset. */
    public List fieldList(HClass hc) {
	// get list of all fields in this class and its parents.
	List l = new ArrayList();
	for (HClass p = hc; p!=null; p=p.getSuperclass())
	    l.addAll(Arrays.asList(p.getDeclaredFields()));
	// weed out static fields
	for (Iterator it=l.iterator(); it.hasNext(); )
	    if (((HField)it.next()).isStatic())
		it.remove();
	// now sort by fieldOffset.
	Collections.sort(l, new Comparator() {
	    public int compare(Object o1, Object o2) {
		HField hf1=(HField)o1, hf2=(HField)o2;
		return fieldOffset(hf1) - fieldOffset(hf2);
	    }
	});
	// done!
	return l;
    }

    /** this method assigns "good" offsets to all the fields in class hc,
     *  using the assignments in hc's superclass and the list of free space
     *  in the superclass as starting points. */
    private void do_one(HClass hc) {
	Util.assert(hc!=null);
	// get the 'free space' structure of the parent.
	List free=new LinkedList(Arrays.asList(freespace(hc.getSuperclass())));
	// get all the fields of this class that we have to allocate.
	List l = new ArrayList(Arrays.asList(hc.getDeclaredFields()));
	// weed out static fields
	for (Iterator it=l.iterator(); it.hasNext(); )
	    if (((HField)it.next()).isStatic())
		it.remove();
	// we're going to allocate fields from largest to smallest,
	// so sort them first. (primarily sort by size, then by alignment)
	Collections.sort(l, new Comparator() {
	    public int compare(Object o1, Object o2) {
		HField hf1=(HField)o1, hf2=(HField)o2;
		// note reversed comparison here so that largest end up first.
		int r = fieldSize(hf2) - fieldSize(hf1);
		if (r==0) r = fieldAlignment(hf2) - fieldAlignment(hf1);
		return r;
	    }
	});
	// now allocate them one by one (largest to smallest, like we said)
	// the alloc_one method has the side effect of adding an entry to
	// the fieldcache.
	for (Iterator it=l.iterator(); it.hasNext(); )
	    alloc_one((HField)it.next(), free);
	// cache away the free list for the next guy (subclasses of this)
	freecache.put(hc, (Interval[])free.toArray(new Interval[free.size()]));
	// done!
    }
    /** this method tries to allocate the field hf as low in the object
     *  as possible, using the current list of free spaces in the class. */
    private void alloc_one(HField hf, List free) {
	int size = fieldSize(hf), align = fieldAlignment(hf);
	// go through free list, looking for a place to put this.
	for (ListIterator li = free.listIterator(); li.hasNext(); ) {
	    Interval i = (Interval) li.next();
	    Util.assert(i.low < i.high); // validity of interval.
	    // l and h will be the boundaries of the field, if we put it
	    // in this interval.
	    int l = i.low;
	    if ((l%align)!=0) l+= align - (l % align);
	    int h = l + size;
	    if (h <= i.high) { // yay, the field fits here!
		// update interval list.
		Interval bot = new Interval(i.low, l);
		Interval top = new Interval(h, i.high);
		li.remove(); // replace the old interval with the split ones
		if (bot.low < bot.high) li.add(bot);
		if (top.low < top.high) li.add(top);
		// cache field offset.
		fieldcache.put(hf, new Integer(l));
		// done!
		return;
	    }
	}
	// the last interval goes to infinity; we should always be able to
	// allocate at the end of the object (ie never get to this point)
	throw new Error("Should never get here!");
    }
    /** maps fields to already-computed offsets */
    private final Map fieldcache = new HashMap();

    /** this method returns the cached 'free space' list for class hc.
     *  if the free space list for hc has not already been created and
     *  cached, invokes do_one(hc) to create and cache it.  hc==null
     *  indicates the "non-existent superclass of everything", and
     *  naturally fields can be allocated anywhere in it.  This is
     *  represented as the interval [0, infinity). */
    private Interval[] freespace(HClass hc) {
	if (hc==null)
	    return new Interval[] { new Interval(0, Integer.MAX_VALUE) };
	if (!freecache.containsKey(hc)) do_one(hc);
	Util.assert(freecache.containsKey(hc));
	return (Interval[]) freecache.get(hc);
    }
    /** maps classes to 'free space' lists. */
    private final Map freecache = new HashMap();

    /** This class represents an open interval in the class, which we
     *  may assign a field to (if it fits). */
    private static class Interval {
	final int low, high;
	Interval(int low, int high) { this.low = low; this.high=high; }
    }
}
