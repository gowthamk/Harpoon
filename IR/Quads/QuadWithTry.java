// QuadWithTry.java, created Sat Dec 19 23:55:52 1998 by cananian
package harpoon.IR.Quads;

import harpoon.ClassFile.*;
import harpoon.Util.Util;

/**
 * <code>QuadWithTry</code> is a code view with explicit try-block
 * handlers.  <code>QuadWithTry</code> is not in SSA form.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: QuadWithTry.java,v 1.1.2.1 1998-12-27 21:26:55 cananian Exp $
 * @see QuadNoSSA
 * @see QuadSSA
 */
public class QuadWithTry extends Code /* which extends HCode */ {
    /** The name of this code view. */
    public static final String codename = "quad-with-try";
    
    /** Creates a <code>QuadWithTry</code> object from a
     *  <code>harpoon.IR.Bytecode.Code</code> object. */
    QuadWithTry(harpoon.IR.Bytecode.Code bytecode) {
        super(bytecode.getMethod(), null);
	quads = Translate.trans(bytecode, this);
    }
    private QuadWithTry(HMethod parent, Quad quads) {
	super(parent, quads);
    }
    /** Clone this code representation.  The clone has its own copy of
     *  the quad graph. */
    public HCode clone(HMethod newMethod) {
	QuadWithTry qwt = new QuadWithTry(newMethod, null);
	qwt.quads = Quad.clone(qwt.qf, quads);
	return qwt;
    }
    /**
     * Return the name of this code view.
     * @return the string <code>"quad-with-try"</code>.
     */
    public String getName() { return codename; }

    public static void register() {
	HCodeFactory f = new HCodeFactory() {
	    public HCode convert(HMethod m) {
		HCode c = m.getCode(harpoon.IR.Bytecode.Code.codename);
		return (c==null) ? null :
		    new QuadWithTry((harpoon.IR.Bytecode.Code)c);
	    }
	    public String getCodeName() { return codename; }
	};
	HMethod.register(f);
    }
}
