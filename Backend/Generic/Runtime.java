// Runtime.java, created Wed Sep  8 14:24:18 1999 by cananian
// Copyright (C) 1999 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Backend.Generic;

import harpoon.ClassFile.HClass;
import harpoon.Backend.Maps.NameMap;

import java.util.List;
/**
 * A <code>Runtime</code> provides class data constructors which correspond
 * to a particular architecture/runtime combination.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: Runtime.java,v 1.1.2.1 1999-09-09 00:36:21 cananian Exp $
 */
public abstract class Runtime {
    /** Returns a <code>NameMap</code> valid for this <code>Runtime</code>. */
    public abstract NameMap nameMap();

    /** returns a list of <code>HData</code>s which are needed for the
     *  given class. */
    public abstract List classData(HClass hc);
}
