// Debug.java, created Thu Feb 10 19:06:16 2000 by salcianu
// Copyright (C) 2000 Alexandru SALCIANU <salcianu@retezat.lcs.mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Analysis.PointerAnalysis;

import java.util.Set;
import java.util.Arrays;
import java.util.Iterator;

import harpoon.Tools.UComp;

import harpoon.ClassFile.HMethod;
import harpoon.Analysis.MetaMethods.MetaMethod;

/**
 * <code>Debug</code>
 * 
 * @author  Alexandru SALCIANU <salcianu@retezat.lcs.mit.edu>
 * @version $Id: Debug.java,v 1.1.2.4 2000-03-20 21:29:00 salcianu Exp $
 */
public abstract class Debug {

    /** Returns a sorted array containing all the objects from
	<code>set</code>. Increasing lexicographic order of the
	string representation of the objects is used. */
    public static Object[] sortedSet(Set set){
	Object[] obj = set.toArray(new Object[set.size()]);
	Arrays.sort(obj,UComp.uc);
	return obj;
    }

    /** Provides a string representation of a set; the elements of the
	set appear in increasing lexicographic order.
	<code>set1.equals(set2) <==> stringImg(set1).equals(stringImg(set2)).</code>*/
    public static String stringImg(Set set){
	StringBuffer buffer = new StringBuffer();

	Object obj[] = sortedSet(set);

	buffer.append("[ ");
	for(int i=0; i<obj.length;i++){
	    buffer.append(obj[i]);
	    buffer.append(" ");
	}
	buffer.append("]");

	return buffer.toString();
    }

    public static String stringImg(Object[] v){

	if(v==null) return "null";

	StringBuffer buffer = new StringBuffer();

	Arrays.sort(v,UComp.uc);
	for(int i=0; i<v.length;i++){
	    buffer.append(v[i]);
	    buffer.append("\n");
	}

	return buffer.toString();
    }

    /** Displays a <i>split</i> relation (see the MetaCallGraph stuff). */
    public static void show_split(Relation split){
	for(Iterator it = split.keySet().iterator(); it.hasNext(); ){
	    HMethod hm = (HMethod) it.next();
	    System.out.print(hm);
	    System.out.println("  (" + split.getValuesSet(hm).size() +
			       " specialization(s))");
	    for(Iterator itmm = split.getValues(hm); itmm.hasNext(); ){
		System.out.print("  ");
		System.out.println((MetaMethod)itmm.next());
	    }
	}
    }

}
