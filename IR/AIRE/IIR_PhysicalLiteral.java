// IIR_PhysicalLiteral.java, created by cananian
package harpoon.IR.AIRE;

/**
 * <code>IIR_PhysicalLiteral</code> 
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_PhysicalLiteral.java,v 1.2 1998-10-11 00:32:23 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_PhysicalLiteral extends IIR_Expression
{

// PUBLIC:
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    public IR_Kind get_kind()
    { return IR_Kind.IR_PHYSICAL_LITERAL; }
    //CONSTRUCTOR:
    public IIR_PhysicalLiteral() { }
    //METHODS:  
    public void set_abstract_literal(IIR abstract_literal)
    { _abstract_literal = abstract_literal; }
 
    public IIR get_abstract_literal()
    { return _abstract_literal; }
 
    //MEMBERS:  

// PROTECTED:
    IIR _abstract_literal;
} // END class

