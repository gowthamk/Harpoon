// NEW.java, created Wed Aug  5 07:08:20 1998 by cananian
package harpoon.IR.QuadSSA;

import harpoon.ClassFile.*;
import harpoon.Temp.Temp;
/**
 * <code>NEW</code> represents an object creation operation.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: NEW.java,v 1.5 1998-08-24 19:30:02 cananian Exp $
 */

public class NEW extends Quad {
    public Temp dst;
    public HClass hclass;
    /** Creates a <code>NEW</code> object.  <code>NEW</code> creates
     *  a new instance of the class <code>hclass</code>. */
    public NEW(String sourcefile, int linenumber,
	       Temp dst, HClass hclass) {
        super(sourcefile, linenumber);
	this.dst = dst;
	this.hclass = hclass;
    }
    NEW(HCodeElement hce, Temp dst, HClass hclass) {
	this(hce.getSourceFile(), hce.getLineNumber(), dst, hclass);
    }
    /** Returns a human-readable representation of this quad. */
    public String toString() {
	return dst.toString() + " = NEW " + hclass.getName();
    }
}
