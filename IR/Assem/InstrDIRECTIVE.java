// InstrDIRECTIVE.java, created Mon May 17 16:08:00 1999 by andyb
// Copyright (C) 1999 Andrew Berkheimer <andyb@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.IR.Assem;

import harpoon.ClassFile.HCodeElement;
import harpoon.Temp.Label;
import harpoon.Temp.TempMap;

/**
 * <code>InstrDIRECTIVE</code> is used to represents assembler
 * directives.
 *
 * @author  Andrew Berkheimer <andyb@mit.edu>
 * @version $Id: InstrDIRECTIVE.java,v 1.1.2.5 2000-01-05 23:22:05 pnkfelix Exp $
 */
public class InstrDIRECTIVE extends Instr {

    public InstrDIRECTIVE(InstrFactory inf, HCodeElement src, String a) {
        this(inf, src, a, true);
    } 

    private InstrDIRECTIVE(InstrFactory inf, HCodeElement src,
			   String a, boolean falls) {
	super(inf, src, a, null, null, falls, null);
    }

    public static InstrDIRECTIVE makeNoFall
	(InstrFactory inf, HCodeElement src, String a) {
	return new InstrDIRECTIVE(inf, src, a, false);
    }

    public Instr rename(InstrFactory inf, TempMap defMap, TempMap useMap) {
	return new InstrDIRECTIVE(inf, this, getAssem());
    }

    public void accept(InstrVisitor v) { v.visit(this); }
}
