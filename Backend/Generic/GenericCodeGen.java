// CodeGen.java, created Wed Jul 28 18:19:29 1999 by pnkfelix
// Copyright (C) 1999 Felix S. Klock II <pnkfelix@mit.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.Backend.Generic;

import harpoon.IR.Tree.Code;
import harpoon.IR.Assem.Instr;
import harpoon.IR.Tree.Print;

/**
 * <code>CodeGen</code> is a general class for specific Backends to
 * extend.  Typically a Specfile for a specific backend will be
 * designed as an extension of this class.
 * 
 * @author  Felix S. Klock II <pnkfelix@mit.edu>
 * @version $Id: GenericCodeGen.java,v 1.1.2.8 1999-09-02 21:28:09 pnkfelix Exp $ */
public abstract class GenericCodeGen {

    private static boolean DEBUG = true;
    
    /** Creates a <code>CodeGen</code>. */
    public GenericCodeGen() {
        
    }
    
    /** Creates a <code>Instr</code> list from the
	<code>IR.Tree.Code</code> <code>tree</code>. 
	<BR> <B>effects:</B> Generates and returns a list of
	     <code>Instr</code>s to execute <code>tree</code>.
	@return The head of a list of <code>Instr</code>s
    */
    public abstract Instr gen(harpoon.IR.Tree.Code tree,
			      harpoon.IR.Assem.InstrFactory inf); 
    
    public void debug(String s) {
	if (DEBUG) System.out.println(s);
    }

    public String prettyPrint(harpoon.IR.Tree.Tree exp) {
	return Print.print(exp);
    }
    
} 
