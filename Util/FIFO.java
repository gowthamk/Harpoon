package harpoon.Util;

import java.util.EmptyStackException;
/**
 * The <code>FIFO</code> class represents a first-in-first-out
 * list of objects.
 * 
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: FIFO.java,v 1.1 1998-09-11 03:52:31 cananian Exp $
 */

public class FIFO {

    class List {
	Object item;
	List next;
	List(Object item, List next) {
	    this.item = item; this.next = next;
	}
    }

    List head = null;
    List tail = null;

    /** 
     * Pushes an item onto the front of this fifo.
     * @param item the item to be pushed onto this stack.
     * @return the <code>item</code> argument.
     */
    public synchronized Object push(Object item) {
	if (tail==null) { // empty.
	    tail = head = new List(item, null);
	} else {
	    tail.next = new List(item, null);
	    tail = tail.next;
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
	Object obj = peek();

	head = head.next;
	if (head==null) tail=null;

	return obj;
    }
    /**
     * Looks at the object at the back of this fifo without removing it.
     * @return the object at the end of this fifo.
     * @exception EmptyStackException if this fifo is empty.
     */
    public synchronized Object peek() {
	if (head==null) throw new EmptyStackException();
	return head.item;
    }
    /**
     * Tests if this stack is empty.
     * @return <code>true</code> if this stack is empty;
     *         <code>false</code> otherwise.
     */
    public boolean empty() {
	return (head==null);
    }
}
