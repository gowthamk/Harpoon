// Set.java, created Tue Sep 15 19:28:05 1998 by cananian
// Copyright (C) 1998 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Util;

import java.util.Hashtable;
import java.util.Enumeration;
/**
 * <code>Set</code>
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: Set.java,v 1.3.2.1 1998-11-23 22:54:21 marinov Exp $
 */

public class Set implements Worklist {
    protected Hashtable h;
    /** Creates a <code>SetTable</code>. */
    public Set() {
        h = new Hashtable();
    }
    public void remove(Object o) {
	h.remove(o);
    }
    public void union(Object o) {
	h.put(o, o);
    }
    public Object push(Object o) {
	return h.put(o, o);
    }
    public boolean contains(Object o) {
	return h.containsKey(o);
    }
    public boolean isEmpty() {
	return h.isEmpty();
    }
    public int size() { 
	return h.size(); 
    }
    public Object pull() {
	Object o = h.keys().nextElement();
	h.remove(o);
	return o;
    }
    public void copyInto(Object[] oa) {
	int i=0;
	for(Enumeration e = h.keys(); e.hasMoreElements(); )
	    oa[i++] = e.nextElement();
    }
    public Enumeration elements() { return h.keys(); }
    /** Returns a rather long string representation of this hashtable.
     *  @return a string representation of this hashtable. */
    public String toString() {
	StringBuffer sb = new StringBuffer("{");
	for (Enumeration e = elements(); e.hasMoreElements(); ) {
	    sb.append(e.nextElement().toString());
	    if (e.hasMoreElements())
		sb.append(", ");
	}
	sb.append("}");
	return sb.toString();
    }
}
