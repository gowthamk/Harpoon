#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include <jni.h>
#include <jni-private.h>

int name2class_compare(const void *key, const void *element) {
  const char *name = key;
  const struct FNI_name2class *n2c = element;
  return strcmp(name, n2c->name);
}
jclass FNI_FindClass(JNIEnv *env, const char *name) {
  const struct FNI_name2class * result;
  assert(FNI_NO_EXCEPTIONS(env));
  result =
    bsearch(name, &name2class_start, &name2class_end-&name2class_start,
	    sizeof(name2class_start), name2class_compare);
  if (result==NULL) {
    FNI_ThrowNew(env, FNI_FindClass(env, "java/lang/NoClassDefFoundError"),
		 name);
    return NULL;
  }
  return FNI_WRAP(result->class_object);
}

int class2info_compare(const void *key, const void *element) {
  const struct oobj *class_object = key;
  const struct FNI_class2info *c2i = element;
  return class_object - c2i->class_object;
}
struct FNI_classinfo *FNI_GetClassInfo(jclass clazz) {
  const struct FNI_class2info * result;
  assert(clazz!=NULL);
  result =
    bsearch(FNI_UNWRAP(clazz),
	    &class2info_start, &class2info_end - &class2info_start,
	    sizeof(class2info_start), class2info_compare);
  return (result==NULL) ? NULL : result->info;
}

struct name_and_sig {
  const char *name; const char *sig;
};
int name2member_compare(const void *key, const void *element) {
  const struct name_and_sig *ns = key;
  const struct _jmethodID *methodID = element;
  int r;
  r = strcmp(ns->name, methodID->name);
  return (r!=0) ? r : strcmp(ns->sig, methodID->desc);
}
union _jmemberID *FNI_GetMemberID(jclass clazz,
				   const char *name, const char *sig) {
  struct FNI_classinfo *info = FNI_GetClassInfo(clazz);
  struct name_and_sig ns = { name, sig };
  union _jmemberID * result;
  return (info==NULL) ? NULL :
    bsearch(&ns, info->memberinfo, info->memberend - info->memberinfo,
	    sizeof(union _jmemberID), name2member_compare);
}

#define GETID(name, rtype, extype) \
rtype FNI_Get##name##ID(JNIEnv *env, jclass clazz, \
			const char *name, const char *sig) { \
  rtype result; \
  assert(FNI_NO_EXCEPTIONS(env)); \
  result = (rtype) FNI_GetMemberID(clazz, name, sig); \
  if (result==NULL) { \
    char msg[strlen(name)+strlen(sig)+2]; \
    strcpy(msg, name); strcat(msg, " "), strcat(msg, sig); \
    FNI_ThrowNew(env, FNI_FindClass(env, extype), msg); \
    return NULL; \
  } \
  return result; \
}
GETID(Method, jmethodID, "java/lang/NoSuchMethodError")
GETID(StaticMethod, jmethodID, "java/lang/NoSuchMethodError")
GETID(Field, jfieldID, "java/lang/NoSuchFieldError")
GETID(StaticField, jfieldID, "java/lang/NoSuchFieldError")
