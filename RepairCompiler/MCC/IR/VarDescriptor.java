package MCC.IR;

public class VarDescriptor extends Descriptor {
    
    private static int count = 0;
    boolean isglobal=false;

    TypeDescriptor td = null;

    SetDescriptor sd=null;

    public SetDescriptor getSet() {
	return sd;
    }

    public void setSet(SetDescriptor sd) {
	this.sd=sd;
    }

    public VarDescriptor(String name) {
        super(name);
    }

    public VarDescriptor(String name, TypeDescriptor td) {
        super(name);
        this.td = td;
    }

    public VarDescriptor(String name, String safename, TypeDescriptor td, boolean global) {
        super(name, safename);
        this.td = td;
	this.isglobal=global;
    }

    public boolean isGlobal() {
	return isglobal;
    }
    
    public void setType(TypeDescriptor td) {
        this.td = td;
    }

    public TypeDescriptor getType() {
        return td;
    }

    public static VarDescriptor makeNew() {
        return makeNew("tempvar");
    }

    public static VarDescriptor makeNew(String name) {
        return new VarDescriptor(name + count++);
    }

}
