// IIR_BreakList.java, created by cananian
package harpoon.IR.AIRE;

/**
 * The <code>IIR_BreakList</code> class represents ordered sets containing
 * zero or more <code>IIR_BreakElement</code>s.
 *
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_BreakList.java,v 1.3 1998-10-11 00:32:16 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_BreakList extends IIR_List
{

// PUBLIC:
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    public IR_Kind get_kind()
    { return IR_Kind.IR_BREAK_LIST; }
    //CONSTRUCTOR:
    public IIR_BreakList() { }
    //METHODS:  
    public void prepend_element(IIR_BreakElement element)
    { super._prepend_element(element); }
    public void append_element(IIR_BreakElement element)
    { super._append_element(element); }
    public boolean 
	insert_after_element(IIR_BreakElement existing_element,
			     IIR_BreakElement new_element)
    { return super._insert_after_element(existing_element, new_element); }
    public boolean
	insert_before_element(IIR_BreakElement existing_element,
			      IIR_BreakElement new_element)
    { return super._insert_before_element(existing_element, new_element); }
    public boolean remove_element(IIR_BreakElement existing_element)
    { return super._remove_element(existing_element); }
    public IIR_BreakElement 
	get_successor_element(IIR_BreakElement element)
    { return (IIR_BreakElement)super._get_successor_element(element); }
    public IIR_BreakElement 
	get_predecessor_element(IIR_BreakElement element)
    { return (IIR_BreakElement)super._get_predecessor_element(element); }
    public IIR_BreakElement get_first_element()
    { return (IIR_BreakElement)super._get_first_element(); }
    public IIR_BreakElement get_nth_element(int index)
    { return (IIR_BreakElement)super._get_nth_element(index); }
    public IIR_BreakElement get_last_element()
    { return (IIR_BreakElement)super._get_last_element(); }
    public int get_element_position(IIR_BreakElement element)
    { return super._get_element_position(element); }
    //MEMBERS:  

// PROTECTED:
} // END class

