// TypeMapProxy.java, created Wed Nov 15 20:46:36 2000 by cananian
// Copyright (C) 2000 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Analysis.Maps;

import harpoon.ClassFile.HClass;
import harpoon.ClassFile.HCodeAndMaps;
import harpoon.ClassFile.HCodeElement;
import harpoon.Temp.Temp;
/**
 * A <code>TypeMapProxy</code> implements a <code>TypeMap</code> for
 * a cloned <code>HCode</code> given the <code>HCodeAndMaps</code> which
 * specifies its relationship to an <code>HCode</code> for which a
 * <code>TypeMap</code> is known.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: TypeMapProxy.java,v 1.3 2002-09-02 19:23:27 cananian Exp $
 */
public class TypeMapProxy<HCE extends HCodeElement>
    extends MapProxy<HCE> implements TypeMap<HCE> {
    private TypeMap<HCE> tm;

    /** Creates a <code>TypeMapProxy</code>. */
    public TypeMapProxy(HCodeAndMaps<HCE> hcam, TypeMap<HCE> tm) {
	super(hcam);
	this.tm = tm;
    }
    public HClass typeMap(HCE hce, Temp t) {
	return tm.typeMap(n2o(hce), n2o(t));
    }
}
