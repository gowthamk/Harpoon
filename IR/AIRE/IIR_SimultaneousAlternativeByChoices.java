// IIR_SimultaneousAlternativeByChoices.java, created by cananian
package harpoon.IR.AIRE;

/**
 * <code>IIR_SimultaneousAlternativeByChoices</code> 
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_SimultaneousAlternativeByChoices.java,v 1.3 1998-10-11 00:32:25 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_SimultaneousAlternativeByChoices extends IIR_SimultaneousAlternative
{

// PUBLIC:
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    public IR_Kind get_kind()
    { return IR_Kind.IR_SIMULTANEOUS_ALTERNATIVE_BY_CHOICES; }
    //CONSTRUCTOR:
    public IIR_SimultaneousAlternativeByChoices( ) { }
    //METHODS:  
    //MEMBERS:  
    public IIR_ChoiceList choices;

// PROTECTED:
} // END class

