package harpoon.ClassFile.Raw;

/**
 * The <code>CONSTANT_NameAndType_info</code> structure is used to
 * represent a field or method, without indicating which class or
 * interface type it belongs to.
 * @author  C. Scott Ananian <cananian@alumni.princeton.edu>
 * @version $Id: ConstantNameAndType.java,v 1.6 1998-07-31 06:21:55 cananian Exp $
 * @see "The Java Virtual Machine Specification, section 4.4.6"
 * @see Constant
 */
class ConstantNameAndType extends Constant {
  /** The value of the <code>name_index</code> must be a valid index
      into the <code>constant_pool</code> table.  The
      <code>constant_pool</code> entry at that index must be a
      <code>CONSTANT_Utf8_info</code> structure representing a valid
      Java field name or method name stored as a simple (not fully
      qualified) name, that is, as a Java identifier. */
  int name_index;
  /** the valud of the <code>descriptor_index</code> must be a valid
      index into the <code>constant_pool</code> table.  The
      <code>constant_pool</code> entry at that index must be a
      <code>CONSTANT_Utf8_info</code> structure representing a valid
      Java field descriptor or method descriptor. */
  int descriptor_index;

  /** Constructor. */
  ConstantNameAndType(ClassFile parent, ClassDataInputStream in) 
    throws java.io.IOException {
    super(parent);
    name_index = in.read_u2();
    descriptor_index = in.read_u2();
  }
  /** Constructor. */
  public ConstantNameAndType(ClassFile parent, 
			     int name_index, int descriptor_index) {
    super(parent);
    this.name_index = name_index;
    this.descriptor_index = descriptor_index;
  }

  /** Write to a bytecode file. */
  void write(ClassDataOutputStream out) throws java.io.IOException {
    out.write_u1(CONSTANT_NameAndType);
    out.write_u2(name_index);
    out.write_u2(descriptor_index);
  }

  // convenience.
  ConstantUtf8 name_index()
  { return (ConstantUtf8) parent.constant_pool[name_index]; }
  ConstantUtf8 descriptor_index()
  { return (ConstantUtf8) parent.constant_pool[descriptor_index]; }

  String name() { return name_index().val; }
  String descriptor() { return descriptor_index().val; }
}
