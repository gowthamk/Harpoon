// InstrJUMP.java, created Fri Aug 27 15:20:57 1999 by pnkfelix
// Copyright (C) 1999 Felix S. Klock II <pnkfelix@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.IR.Assem;
  
import harpoon.ClassFile.HCodeElement;
import harpoon.Temp.Label;
import harpoon.Temp.TempMap;

import java.util.Arrays;

/** <code>InstrJUMP</code> represents a shift in control flow to one
    target <code>Label</code> with no side-effects.  This instruction
    is being specialized to allow for easier detection of JUMPs which
    could guide optimizations (mainly in laying out basic blocks to
    allow for elimination of unnecessary JUMPs.)

    Execution of an <code>InstrJUMP</code> should have no side-effects
    other than changing the Program Counter to the target location in
    the code.  Thus, <code>InstrJUMP</code>s can be eliminated if
    control would already flow through the code in the same way
    without the JUMP in place.
    
    @author  Felix S. Klock II <pnkfelix@mit.edu>
    @version $Id: InstrJUMP.java,v 1.1.2.5 2000-10-19 22:39:07 pnkfelix Exp $ */
public class InstrJUMP extends Instr {
    
    /** Creates a <code>InstrJUMP</code>. */
    public InstrJUMP( InstrFactory inf, HCodeElement source,
		      String assem, Label target) {
        super(inf, source, assem, null, null, false, 
	      Arrays.asList(new Label[]{ target }));
    }

    public Instr rename(InstrFactory inf, TempMap defMap, TempMap useMap) {
	return new InstrJUMP(inf, this, getAssem(),
			     (Label)getTargets().get(0));
    }
    public void accept(InstrVisitor v) { v.visit(this); }

    public boolean isJump() { return true; }
}
