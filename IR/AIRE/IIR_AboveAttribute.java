// IIR_AboveAttribute.java, created by cananian
package harpoon.IR.AIRE;

/**
 * <code>IIR_AboveAttribute</code> 
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_AboveAttribute.java,v 1.2 1998-10-11 00:32:15 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_AboveAttribute extends IIR_Attribute
{

// PUBLIC:
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    public IR_Kind get_kind()
    { return IR_Kind.IR_ABOVE_ATTRIBUTE; }
    //CONSTRUCTOR:
    public IIR_AboveAttribute() {}

    //METHODS:  
    //MEMBERS:  

// PROTECTED:
} // END class

