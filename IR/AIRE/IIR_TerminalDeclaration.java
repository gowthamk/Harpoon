// IIR_TerminalDeclaration.java, created by cananian
package harpoon.IR.AIRE;

/**
 * The predefined <code>IIR_TerminalDeclaration</code> class.
 *
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_TerminalDeclaration.java,v 1.3 1998-10-11 00:32:28 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_TerminalDeclaration extends IIR_ObjectDeclaration
{

// PUBLIC:
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    public IR_Kind get_kind()
    { return IR_Kind.IR_TERMINAL_DECLARATION; }

    /** The constructor method initializes a terminal declaration with
     *  an unspecified source location, and unspecified declarator,
     *  and an unspecified nature. */
    public IIR_TerminalDeclaration() { }
    //METHODS:  
    public IIR_NatureDefinition get_nature()
    { return _nature; }
    public void set_nature(IIR_NatureDefinition nature)
    { _nature = nature; }
 
    //MEMBERS:  

// PROTECTED:
    IIR_NatureDefinition _nature;
} // END class

