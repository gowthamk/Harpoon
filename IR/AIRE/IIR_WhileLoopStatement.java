// IIR_WhileLoopStatement.java, created by cananian
package harpoon.IR.AIRE;

/**
 * <code>IIR_WhileLoopStatement</code> 
 * @author C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: IIR_WhileLoopStatement.java,v 1.4 1998-10-11 00:32:29 cananian Exp $
 */

//-----------------------------------------------------------
public class IIR_WhileLoopStatement extends IIR_SequentialStatement
{

// PUBLIC:
    public void accept(IIR_Visitor visitor ){visitor.visit(this);}
    public IR_Kind get_kind()
    { return IR_Kind.IR_WHILE_LOOP_STATEMENT; }
    //CONSTRUCTOR:
    public IIR_WhileLoopStatement() { }
    //METHODS:  
    public void set_while_condition(IIR while_condition)
    { _while_condition = while_condition; }
 
    public IIR get_while_condition()
    { return _while_condition; }
 
    //MEMBERS:  
    public IIR_SequentialStatementList sequence_of_statements;
    public IIR_DeclarationList loop_declarations;

// PROTECTED:
    IIR _while_condition;
} // END class

