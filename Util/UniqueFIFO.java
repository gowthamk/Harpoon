package harpoon.Util;

import java.util.Hashtable;
import java.util.EmptyStackException;
/**
 * The <code>UniqueFIFO</code> class represents a first-in-first-out
 * list of <b>unique</b> objects.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: UniqueFIFO.java,v 1.2 1998-09-11 03:52:31 cananian Exp $
 */

public class UniqueFIFO extends FIFO {

    Hashtable uniq = new Hashtable();

    /** 
     * Pushes an item onto the front of this fifo, if it is unique.
     * Otherwise, does nothing.
     * @param item the item to be pushed onto this stack.
     * @return the <code>item</code> argument.
     */
    public synchronized Object push(Object item) {
	if (!uniq.containsKey(item)) {
	    uniq.put(item, item);
	    super.push(item);
	}
	return item;
    }
    /**
     * Removes the object at the back of this fifo and returns that
     * object as the value of this function.
     * @return The object at the end of the fifo.
     * @exception EmptyStackException if this fifo is empty.
     */
    public synchronized Object pull() {
	Object obj = super.pull();
	uniq.remove(obj);
	return obj;
    }
    /**
     * Looks at the object at the back of this fifo without removing it.
     * @return the object at the end of this fifo.
     * @exception EmptyStackException if this fifo is empty.
     */
    public synchronized Object peek() {
	return super.peek();
    }
}
