// IIR_ConfigurationDeclaration.java, created by cananian
package harpoon.IR.AIRE;

/**
 * <code>IIR_ConfigurationDeclaration</code> 
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_ConfigurationDeclaration.java,v 1.3 1998-10-11 00:32:18 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_ConfigurationDeclaration extends IIR_LibraryUnit
{

// PUBLIC:
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    public IR_Kind get_kind()
    { return IR_Kind.IR_CONFIGURATION_DECLARATION; }
    //CONSTRUCTOR:
    public IIR_ConfigurationDeclaration() { }
    //METHODS:  
    public void set_block_configuration(IIR_BlockConfiguration block_configuration)
    { _block_configuration = block_configuration; }
 
    public IIR_BlockConfiguration get_block_configuration()
    { return _block_configuration; }
 
    public void set_entity(IIR_EntityDeclaration entity)
    { _entity = entity; }
 
    public IIR_EntityDeclaration get_entity()
    { return _entity; }
 
    //MEMBERS:  
    public IIR_DeclarationList configuration_declarative_part;

// PROTECTED:
    IIR_BlockConfiguration _block_configuration;
    IIR_EntityDeclaration _entity;
} // END class

