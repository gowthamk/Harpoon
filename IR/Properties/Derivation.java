// Derivation.java, created Fri Jan 22 16:46:17 1999 by cananian
// Copyright (C) 1999 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.IR.Properties;

import harpoon.ClassFile.HCodeElement;
import harpoon.Temp.CloningTempMap;
import harpoon.Temp.Temp;
import harpoon.Temp.TempMap;

/**
 * <code>Derivation</code> provides a mean to access the derivation
 * of a particular derived pointer.  Given a compiler temporary, it
 * will enumerate the base pointers and signs needed to allow proper
 * garbage collection of the derived pointer.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: Derivation.java,v 1.1.2.4 1999-02-08 17:20:49 duncan Exp $
 */
public interface Derivation  {

    /** Map compiler temporaries to their derivations.
     * @return <code>null</code> if the temporary has no derivation (is
     *         a base pointer, for example), or the derivation otherwise.
     */
    public DList derivation(HCodeElement hce, Temp t);

    /** Structure of the derivation information. */
    public class DList {
	/** Base pointer. */
	public final Temp base;
	/** Sign of base pointer.  <code>true</code> if derived pointer
	 *  equals offset <b>+</b> base pointer, <code>false</code> if
	 *  derived pointer equals offset <b>-</b> base pointer. */
	public final boolean sign;
	/** Pointer to a continuation of the derivation, or <Code>null</code>
	 *  if there are no more base pointers associated with this derived
	 *  pointer. */
	public final DList next;
	/** Constructor. */
	public DList(Temp base, boolean sign, DList next) {
	    this.base = base; this.sign = sign; this.next = next;
	}
      
      /** Returns a clone of this <code>DList</code> */
      public DList clone(CloningTempMap ctm) {
	return new DList(((this.base==null)?null:ctm.tempMap(this.base)),
			 this.sign, 
			 ((this.next==null)?null:this.next.clone(ctm)));
      }

      /** Returns a new <code>DList</code> with the <code>Temp</code>s 
       *  renamed by the supplied mapping */
      public DList rename(TempMap tempMap)
	{
	  return new DList((this.base==null)?null:tempMap.tempMap(this.base),
			   this.sign,
			   (this.next==null)?null:this.next.rename(tempMap));
	}
    }
}
