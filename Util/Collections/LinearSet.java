// LinearSet.java, created Wed Aug  4 12:03:54 1999 by pnkfelix
// Copyright (C) 1999 Felix S. Klock II <pnkfelix@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Util.Collections;

import java.util.AbstractSet;
import java.util.Set;
import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * <code>LinearSet</code> is a simplistic light-weight
 * <code>Set</code> designed for use when the number of entries is
 * small.  It is backed by an <code>List</code>.
 * 
 * @author  Felix S. Klock II <pnkfelix@mit.edu>
 * @version $Id: LinearSet.java,v 1.1.2.1 2000-05-23 17:12:49 pnkfelix Exp $
 */
public class LinearSet extends AbstractSet {
    private List list;

    /** Creates a <code>LinearSet</code>. Uses an
	<code>ArrayList</code> as the backing store.*/
    public LinearSet() {
        list = new ArrayList();
    }

    /** Creates a <code>LinearSet</code> with given capacity. 
	Uses an <code>ArrayList</code> as the backing store.
     */
    public LinearSet(final int capacity) {
        list = new ArrayList(capacity);
    }

    /** Creates a <code>LinearSet</code>, filling it with the elements
	of <code>set</code>.  Uses an <code>ArrayList</code> as the
	backing store.
    */
    public LinearSet(final Set set) {
	int sz = set.size();
	list = new ArrayList(sz);
	Iterator iter = set.iterator();
	for(int i=0; i<sz; i++) {
	    list.add(iter.next());
	}
	((ArrayList)list).trimToSize();
    }

    /** Creates an empty <code>LinearSet</code>, using a
	<code>List</code> generated by <code>lf</code> as the backing
	store.  
    */
    public LinearSet(final ListFactory lf) {
	list = lf.makeList();
    }

    /** Creates an empty <code>LinearSet</code>, using a
	<code>List</code> generated by <code>lf</code> as the backing
	store, and fills it with the elements of <code>set</code>.
    */
    public LinearSet(final ListFactory lf, final Set set) {
	list = lf.makeList(set);
    }

    
    public Iterator iterator() {
	return list.iterator();
    }

    public int size() {
	return list.size();
    }

    public boolean add(Object o) {
	if (list.contains(o)) {
	    return false;
	} else {
	    list.add(o);
	    return true;
	}
    }

    public boolean remove(Object o) {
	int index = list.indexOf(o);
	if (index == -1) {
	    return false;
	} else {
	    list.remove(index);
	    return true;
	}
    }
}
