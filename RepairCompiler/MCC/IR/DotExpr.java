package MCC.IR;

import java.util.*;

public class DotExpr extends Expr {
    
    Expr left;
    String field;
    Expr index;

    public DotExpr(Expr left, String field, Expr index) {
        this.left = left;
        this.field = field;
        this.index = index;
    }

    public Set getRequiredDescriptors() {
        Set v = left.getRequiredDescriptors();
        
        if (index != null) {
            v.addAll(index.getRequiredDescriptors());
        }

        return v;
    }

    public void generate(CodeWriter writer, VarDescriptor dest) {
        VarDescriptor leftd = VarDescriptor.makeNew("left");

        writer.output("// " +  leftd.getSafeSymbol() + " <-- ");
        left.prettyPrint(writer);
        writer.outputline("");

        left.generate(writer, leftd);

        writer.output("// " +  leftd.getSafeSymbol() + " = ");
        left.prettyPrint(writer);
        writer.outputline("");

      
        StructureTypeDescriptor struct = (StructureTypeDescriptor) left.getType();        
        FieldDescriptor fd = struct.getField(field);
        LabelDescriptor ld = struct.getLabel(field);        
        Expr intindex = index;
        Expr offsetbits;

        if (ld != null) { /* label */
            assert fd == null;
            fd = ld.getField();
            assert fd != null;
            assert intindex == null;
            intindex = ld.getIndex();
        } 

        // #ATTN#: getOffsetExpr needs to be called with the fielddescriptor obect that is in teh vector list
        // this means that if the field is an arraydescriptor you have to call getOffsetExpr with the array 
        // descriptor not the underlying field descriptor

        /* we calculate the offset in bits */
        offsetbits = struct.getOffsetExpr(fd);                    

        if (fd instanceof ArrayDescriptor) {
            fd = ((ArrayDescriptor) fd).getField();
        } 
        
        if (intindex != null) {
            if (intindex instanceof IntegerLiteralExpr && ((IntegerLiteralExpr) intindex).getValue() == 0) {
                /* short circuit for constant 0 */                
            } else {
                Expr basesize = fd.getBaseSizeExpr();
                offsetbits = new OpExpr(Opcode.ADD, offsetbits, new OpExpr(Opcode.MULT, basesize, intindex));
            }
        }
        
        final SymbolTable st = writer.getSymbolTable();
        TypeDescriptor td = offsetbits.typecheck(new SemanticAnalyzer() {
                public IRErrorReporter getErrorReporter() { throw new IRException("badness"); }
                public SymbolTable getSymbolTable() { return st; }
            });

        if (td == null) {
            throw new IRException();
        } else if (td != ReservedTypeDescriptor.INT) {
            throw new IRException();
        }
               
        // #TBD#: ptr's to bits and byte's and stuff are a little iffy... 
        // right now, a bit* is the same as a int* = short* = byte* (that is there 
        // is no post-derefernce mask)

        if (offsetbits instanceof IntegerLiteralExpr) {
            int offsetinbits = ((IntegerLiteralExpr) offsetbits).getValue();
            int offset = offsetinbits >> 3; /* offset in bytes */

            if (fd.getType() instanceof ReservedTypeDescriptor && !fd.getPtr()) {
                int shift = offsetinbits - (offset << 3);            
                int mask = bitmask(((IntegerLiteralExpr)fd.getType().getSizeExpr()).getValue());
                               
                /* type var = ((*(int *) (base + offset)) >> shift) & mask */
                writer.outputline(getType().getGenerateType() + " " + dest.getSafeSymbol() + 
                                  " = ((*(int *)" + 
                                  "(" + leftd.getSafeSymbol() + " + " + offset + ")) " + 
                                  " >> " + shift + ") & 0x" + Integer.toHexString(mask) + ";");  
            } else { /* a structure address or a ptr! */
                String ptr = fd.getPtr() ? "*(int *)" : "";
                /* type var = [*(int *)] (base + offset) */
                writer.outputline(getType().getGenerateType() + " " + dest.getSafeSymbol() + 
                                  " = " + ptr + "(" + leftd.getSafeSymbol() + " + " + offset + ");");  
            }
        } else { /* offset in bits is an expression that must be generated */                        
            VarDescriptor ob = VarDescriptor.makeNew("offsetinbits");
            writer.output("// " + ob.getSafeSymbol() + " <-- ");
            offsetbits.prettyPrint(writer);
            writer.outputline("");
            offsetbits.generate(writer, ob);
            writer.output("// " + ob.getSafeSymbol() + " = ");
            offsetbits.prettyPrint(writer);
            writer.outputline("");

            /* derive offset in bytes */
            VarDescriptor offset = VarDescriptor.makeNew("offset");
            writer.outputline("int " + offset.getSafeSymbol() + " = " + ob.getSafeSymbol() + " >> 3;");
            
            if (fd.getType() instanceof ReservedTypeDescriptor && !fd.getPtr()) {
                VarDescriptor shift = VarDescriptor.makeNew("shift");
                writer.outputline("int " + shift.getSafeSymbol() + " = " + ob.getSafeSymbol() + 
                                  " - (" + offset.getSafeSymbol() + " << 3);");
                int mask = bitmask(((IntegerLiteralExpr)fd.getType().getSizeExpr()).getValue());
                
                /* type var = ((*(int *) (base + offset)) >> shift) & mask */
                writer.outputline(getType().getGenerateType() + " " + dest.getSafeSymbol() + 
                                  " = ((*(int *)" + 
                                  "(" + leftd.getSafeSymbol() + " + " + offset.getSafeSymbol() + ")) " + 
                                  " >> " + shift.getSafeSymbol() + ") & 0x" + Integer.toHexString(mask) + ";");  
            } else { /* a structure address or a ptr */
                String ptr = fd.getPtr() ? "*(int *)" : "";
                /* type var = [*(int *)] (base + offset) */
                writer.outputline(getType().getGenerateType() + " " + dest.getSafeSymbol() + 
                                  " = " + ptr + "(" + leftd.getSafeSymbol() + " + " + offset.getSafeSymbol() + ");");  
            }            
        }
    }

    private int bitmask(int bits) {
        int mask = 0;
        
        for (int i = 0; i < bits; i++) {
            mask <<= 1;
            mask += 1;
        }

        return mask;            
    }

    public void prettyPrint(PrettyPrinter pp) {
        left.prettyPrint(pp);
        pp.output("." + field);
        if (index != null) {
            pp.output("[");
            index.prettyPrint(pp);
            pp.output("]");
        }
    }

    public TypeDescriptor typecheck(SemanticAnalyzer sa) {
        TypeDescriptor lefttype = left.typecheck(sa);
        TypeDescriptor indextype = index == null ? null : index.typecheck(sa);

        if ((lefttype == null) || (index != null && indextype == null)) {
            return null;
        }

        if (indextype != null) {
            if (indextype != ReservedTypeDescriptor.INT) {
                sa.getErrorReporter().report(null, "Index must be of type 'int' not '" + indextype.getSymbol() + "'");
                return null;
            }
        }

        if (lefttype instanceof StructureTypeDescriptor) {            
            StructureTypeDescriptor struct = (StructureTypeDescriptor) lefttype;
            FieldDescriptor fd = struct.getField(field);
            LabelDescriptor ld = struct.getLabel(field);

            if (fd != null) { /* field */
                assert ld == null;

                if (indextype == null && fd instanceof ArrayDescriptor) {
                    sa.getErrorReporter().report(null, "Must specify an index what accessing array field '" + struct.getSymbol() + "." + fd.getSymbol() + "'");
                    return null;                
                } else if (indextype != null && !(fd instanceof ArrayDescriptor)) {
                    sa.getErrorReporter().report(null, "Cannot specify an index when accessing non-array field '" + struct.getSymbol() + "." + fd.getSymbol() + "'");
                    return null;
                }
                
                this.td = fd.getType();
            } else if (ld != null) { /* label */
                assert fd == null;

                if (index != null) { 
                    sa.getErrorReporter().report(null, "A label cannot be accessed as an array");
                    return null;
                }
                
                this.td = ld.getType();
            } else {
                sa.getErrorReporter().report(null, "No such field or label '" + field + "' in structure '" + struct.getSymbol() + "'");
                return null;
            }

            /* we promote bit, byte and short to integer types */
            if (this.td == ReservedTypeDescriptor.BIT ||
                this.td == ReservedTypeDescriptor.BYTE ||
                this.td == ReservedTypeDescriptor.SHORT) {
                this.td = ReservedTypeDescriptor.INT;
            }

            return this.td;
        } else {
            sa.getErrorReporter().report(null, "Left hand side of . expression must be a structure type, not '" + lefttype.getSymbol() + "'");
            return null;
        }
        
        
    }

}
        