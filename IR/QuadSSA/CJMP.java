// CJMP.java, created Wed Aug  5 07:07:32 1998 by cananian
package harpoon.IR.QuadSSA;

import harpoon.ClassFile.*;
/**
 * <code>CJMP</code> represents conditional branches.
 * succ[0] is if-false, succ[1] is if-true branch.
 * op is canonical.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: CJMP.java,v 1.2 1998-08-07 13:38:12 cananian Exp $
 */

public abstract class CJMP extends Quad {
    /** Equality condition. */
    public static final int EQ = 0;
    /** Greater-than-or-equal-to. */
    public static final int GE = 1;
    /** Greater-than. */
    public static final int GT = 2;
    public int op;
    /** Creates a <code>CJMP</code>. */
    public CJMP(String sourcefile, int linenumber, int op) {
        super(sourcefile, linenumber);
	this.op = op;
    }
    /** Swap if-true and if-false targets. */
    public abstract void invert();
}
