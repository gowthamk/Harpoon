// CALL.java, created Wed Aug  5 06:48:50 1998
package harpoon.IR.QuadSSA;

import harpoon.ClassFile.*;
import harpoon.Temp.Temp;
/**
 * <code>CALL</code> objects represent method invocations.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: CALL.java,v 1.2 1998-08-07 13:38:12 cananian Exp $
 */

public class CALL extends Quad {
    /** The method to invoke. */
    public HMethod method;
    /** Parameters to pass to the method. */
    public Temp[] params;
    /** Destination for the method's return value. */
    public Temp retval;
    /** Creates a <code>CALL</code>. <code>params</code> should match
     *  exactly the number of parameters in the method descriptor,
     *  and <code>retval</code> should be <code>null</code> if the
     *  method returns no value. */
    public CALL(String sourcefile, int linenumber,
		HMethod method, Temp[] params, Temp retval) {
	super(sourcefile, linenumber);
	this.method = method;
	this.params = params;
	this.retval = retval;
	// XXX should check params and retval here against method.
    }
    /** Create a <Code>CALL</code> to a method with a <code>void</code>
     *  return-value descriptor. */
    public CALL(String sourcefile, int linenumber,
		HMethod method, Temp[] params) {
	this(sourcefile, linenumber, method, params, null);
    }
}
