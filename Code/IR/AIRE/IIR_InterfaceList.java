// IIR_InterfaceList.java, created by cananian
// Copyright (C) 1998 C. Scott Ananian <cananian@alumni.princeton.edu>
// Licensed under the terms of the GNU GPL; see COPYING for details.
package harpoon.IR.AIRE;

/**
 * The predefined <code>IIR_InterfaceList</code> class represents ordered
 * sets containing zero or more <code>IIR_InterfaceDeclaration</code>s.
 * Interface class lists appear as predefined public data elements within
 * <code>IIR_SubprogramDeclaration</code>s.
 *
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_InterfaceList.java,v 1.4 1998-10-11 02:37:19 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_InterfaceList extends IIR_List
{

// PUBLIC:
    /** Accept a visitor class. */
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    /**
     * Returns the <code>IR_Kind</code> of this class (IR_INTERFACE_LIST).
     * @return <code>IR_Kind.IR_INTERFACE_LIST</code>
     */
    public IR_Kind get_kind()
    { return IR_Kind.IR_INTERFACE_LIST; }
    //CONSTRUCTOR:
    public IIR_InterfaceList(){}
    //METHODS:  
    public void prepend_element(IIR_InterfaceDeclaration element)
    { super._prepend_element(element); }
    public void append_element(IIR_InterfaceDeclaration element)
    { super._append_element(element); }
    public boolean 
	insert_after_element(IIR_InterfaceDeclaration existing_element,
			     IIR_InterfaceDeclaration new_element)
    { return super._insert_after_element(existing_element, new_element); }
    public boolean
	insert_before_element(IIR_InterfaceDeclaration existing_element,
			      IIR_InterfaceDeclaration new_element)
    { return super._insert_before_element(existing_element, new_element); }
    public boolean remove_element(IIR_InterfaceDeclaration existing_element)
    { return super._remove_element(existing_element); }
    public IIR_InterfaceDeclaration 
	get_successor_element(IIR_InterfaceDeclaration element)
    { return (IIR_InterfaceDeclaration)super._get_successor_element(element); }
    public IIR_InterfaceDeclaration 
	get_predecessor_element(IIR_InterfaceDeclaration element)
    { return (IIR_InterfaceDeclaration)super._get_predecessor_element(element); }
    public IIR_InterfaceDeclaration get_first_element()
    { return (IIR_InterfaceDeclaration)super._get_first_element(); }
    public IIR_InterfaceDeclaration get_nth_element(int index)
    { return (IIR_InterfaceDeclaration)super._get_nth_element(index); }
    public IIR_InterfaceDeclaration get_last_element()
    { return (IIR_InterfaceDeclaration)super._get_last_element(); }
    public int get_element_position(IIR_InterfaceDeclaration element)
    { return super._get_element_position(element); }
    //MEMBERS:  

// PROTECTED:
} // END class

