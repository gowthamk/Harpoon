package harpoon.Interpret.Tree;

/**
 * This exception is thrown when the type of a <code>Pointer</code>
 * within the Tree interpreter is changed.  This is necessary because 
 * the type of a <code>Pointer</code> cannot be determined when it is
 * created.  
 *
 * @author  Duncan Bryce <duncan@lcs.mit.edu>
 * @version $Id: PointerTypeChangedException.java,v 1.1.2.1 1999-03-27 22:05:09 duncan Exp $
 */
public class PointerTypeChangedException extends RuntimeException {
    /** The <code>Pointer</code> whose type is changed */
    public Pointer ptr;

    /** Class constructor */
    public PointerTypeChangedException(Pointer ptr) {
	super();
	this.ptr = ptr;
    }
}
