package MCC.IR;

class Updates {
    static public final int EXPR=0;
    static public final int POSITION=1;
    static public final int ABSTRACT=2;
    int type=-1;
    int rightposition;
    Expr rightexpr;
    Expr leftexpr;
    Opcode opcode;
    boolean negate=false;

    public String toString() {
	if (type==EXPR)
	    return leftexpr.name()+opcode.toString()+rightexpr.name();
	else if (type==POSITION)
	    return leftexpr.name()+opcode.toString()+"Position("+String.valueOf(rightposition)+")";
	else if (type==ABSTRACT) {
	    if (negate) return "!"+leftexpr.name();
	    else return leftexpr.name();
	} else throw new Error("Unrecognized type");
    }

    public Updates(Expr lexpr, Expr rexpr, Opcode op, boolean negate) {
	if (!lexpr.isValue())
	    System.out.println("Building invalid update");
	leftexpr=lexpr;
	type=Updates.EXPR;

	op=Opcode.translateOpcode(negate,op);

	opcode=op;
	rightexpr=rexpr;
    }

    boolean isGlobal() {
	if (leftexpr instanceof VarExpr)
	    return true;
	else return false;
    }

    VarDescriptor getVar() {
	if (isGlobal()) {
	    return ((VarExpr)leftexpr).getVar();
	} else if (isField()) {
	    Expr e=leftexpr;
	    do {
		for(;e instanceof DotExpr;e=((DotExpr)e).getExpr()) ;
		if (e instanceof VarExpr)
		    break;
		if (e instanceof CastExpr)
		    e=((CastExpr)e).getExpr();
		else throw new Error("Unrecognized Expr:"+e.name());
	    } while(true);
	    return ((VarExpr)e).getVar();
	} else {
	    System.out.println(toString());
	    throw new Error("Unrecognized Update");
	}
    }

    Descriptor getDescriptor() {
	if (isGlobal()) {
	    return ((VarExpr)leftexpr).getVar();
	} else if (isField()) {
	    return ((DotExpr)leftexpr).getField();
	} else {
	    System.out.println(toString());
	    throw new Error("Unrecognized Update");
	}
    }

    boolean isField() {
	if (leftexpr instanceof DotExpr) {
	    assert ((DotExpr)leftexpr).getIndex()==null;
	    return true;
	} else
	    return false;
    }
    
    boolean isExpr() {
	return type==Updates.EXPR;
    }

    
    Opcode getOpcode() {
	return opcode;
    }

    public Updates(Expr lexpr, Expr rexpr) {
	if (!lexpr.isValue())
	    System.out.println("Building invalid update");
	leftexpr=lexpr;
	rightexpr=rexpr;
	type=Updates.EXPR;
	opcode=Opcode.EQ;
    }

    public Updates(Expr lexpr, int rpos) {
	if (!lexpr.isValue())
	    System.out.println("Building invalid update");
	leftexpr=lexpr;
	rightposition=rpos;
	type=Updates.POSITION;
	opcode=Opcode.EQ;
    }

    boolean isAbstract() {
	return type==Updates.ABSTRACT;
    }

    public Updates(Expr lexpr,boolean negates) {
	leftexpr=lexpr;
	type=Updates.ABSTRACT;
	negate=negates;
	opcode=null;
    }

    public int getType() {
	return type;
    }
    public Expr getLeftExpr() {
	return leftexpr;
    }
    public int getRightPos() {
	assert type==Updates.POSITION;
	return rightposition;
    }
    public Expr getRightExpr() {
	assert type==Updates.EXPR;
	return rightexpr;
    }
}
