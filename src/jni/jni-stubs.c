#include <stdio.h>
#include <jni.h>
#include <jni-private.h>

jint FNI_GetVersion(JNIEnv *env) {
  return 0x00010001; /* JNI version 1.1 */
}

/* do-nothing stubs */
jint FNI_MonitorEnter(JNIEnv *env, jobject obj) {
  return 0;
}
jint FNI_MonitorExit(JNIEnv *env, jobject obj) {
  return 0;
}
jint FNI_UnregisterNatives(JNIEnv *env, jclass clazz) {
  return 0;
}

/* complain about an unimplemented method */
void FNI_Unimplemented(void) {
  fprintf(stderr, "Unimplemented JNI function.  Aborting.");
  abort();
}
