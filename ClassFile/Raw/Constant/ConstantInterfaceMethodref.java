package ClassFile;

class ConstantInterfaceMethodref extends ConstantPoolInfo {
  int class_index;
  int name_and_type_index;
  
  ConstantInterfaceMethodref(ClassDataInputStream in) 
       throws java.io.IOException {
    class_index = in.read_u2();
    name_and_type_index = in.read_u2();
  }
}
