/* JNI function dispatch table. */
#include <jni.h>
#include <jni-private.h>

const struct JNINativeInterface FLEX_JNI_vtable = {
  0,
  
  0,
  0,
  0,
  FNI_GetVersion,
            
  (typeof(&FNI_DefineClass)) FNI_Unimplemented,
  FNI_FindClass,
  0,
  0,
  0,
  (typeof(&FNI_GetSuperclass)) FNI_Unimplemented,
  (typeof(&FNI_IsAssignableFrom)) FNI_Unimplemented,
  0,
            
  FNI_Throw,
  FNI_ThrowNew,
  FNI_ExceptionOccurred,
  FNI_ExceptionDescribe,
  FNI_ExceptionClear,
  FNI_FatalError,
  0,
  0,
            
  FNI_NewGlobalRef,
  FNI_DeleteGlobalRef,
  FNI_DeleteLocalRef,
  FNI_IsSameObject,
  0,
  0,
            
  (typeof(&FNI_AllocObject)) FNI_Unimplemented,
  (typeof(&FNI_NewObject)) FNI_Unimplemented,
  (typeof(&FNI_NewObjectV)) FNI_Unimplemented,
  (typeof(&FNI_NewObjectA)) FNI_Unimplemented,
            
  (typeof(&FNI_GetObjectClass)) FNI_Unimplemented,
  (typeof(&FNI_IsInstanceOf)) FNI_Unimplemented,
            
  FNI_GetMethodID,
            
  (typeof(&FNI_CallObjectMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallObjectMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallObjectMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallBooleanMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallBooleanMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallBooleanMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallByteMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallByteMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallByteMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallCharMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallCharMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallCharMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallShortMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallShortMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallShortMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallIntMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallIntMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallIntMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallLongMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallLongMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallLongMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallFloatMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallFloatMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallFloatMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallDoubleMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallDoubleMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallDoubleMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallVoidMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallVoidMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallVoidMethodA)) FNI_Unimplemented,
            
  (typeof(&FNI_CallNonvirtualObjectMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualObjectMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualObjectMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualBooleanMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualBooleanMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualBooleanMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualByteMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualByteMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualByteMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualCharMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualCharMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualCharMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualShortMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualShortMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualShortMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualIntMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualIntMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualIntMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualLongMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualLongMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualLongMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualFloatMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualFloatMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualFloatMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualDoubleMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualDoubleMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualDoubleMethodA)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualVoidMethod)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualVoidMethodV)) FNI_Unimplemented,
  (typeof(&FNI_CallNonvirtualVoidMethodA)) FNI_Unimplemented,
            
  FNI_GetFieldID,
            
  (typeof(&FNI_GetObjectField)) FNI_Unimplemented,
  (typeof(&FNI_GetBooleanField)) FNI_Unimplemented,
  (typeof(&FNI_GetByteField)) FNI_Unimplemented,
  (typeof(&FNI_GetCharField)) FNI_Unimplemented,
  (typeof(&FNI_GetShortField)) FNI_Unimplemented,
  (typeof(&FNI_GetIntField)) FNI_Unimplemented,
  (typeof(&FNI_GetLongField)) FNI_Unimplemented,
  (typeof(&FNI_GetFloatField)) FNI_Unimplemented,
  (typeof(&FNI_GetDoubleField)) FNI_Unimplemented,
  (typeof(&FNI_SetObjectField)) FNI_Unimplemented,
  (typeof(&FNI_SetBooleanField)) FNI_Unimplemented,
  (typeof(&FNI_SetByteField)) FNI_Unimplemented,
  (typeof(&FNI_SetCharField)) FNI_Unimplemented,
  (typeof(&FNI_SetShortField)) FNI_Unimplemented,
  (typeof(&FNI_SetIntField)) FNI_Unimplemented,
  (typeof(&FNI_SetLongField)) FNI_Unimplemented,
  (typeof(&FNI_SetFloatField)) FNI_Unimplemented,
  (typeof(&FNI_SetDoubleField)) FNI_Unimplemented,
            
  FNI_GetStaticMethodID,
            
  FNI_CallStaticObjectMethod,
  FNI_CallStaticObjectMethodV,
  FNI_CallStaticObjectMethodA,
  FNI_CallStaticBooleanMethod,
  FNI_CallStaticBooleanMethodV,
  FNI_CallStaticBooleanMethodA,
  FNI_CallStaticByteMethod,
  FNI_CallStaticByteMethodV,
  FNI_CallStaticByteMethodA,
  FNI_CallStaticCharMethod,
  FNI_CallStaticCharMethodV,
  FNI_CallStaticCharMethodA,
  FNI_CallStaticShortMethod,
  FNI_CallStaticShortMethodV,
  FNI_CallStaticShortMethodA,
  FNI_CallStaticIntMethod,
  FNI_CallStaticIntMethodV,
  FNI_CallStaticIntMethodA,
  FNI_CallStaticLongMethod,
  FNI_CallStaticLongMethodV,
  FNI_CallStaticLongMethodA,
  FNI_CallStaticFloatMethod,
  FNI_CallStaticFloatMethodV,
  FNI_CallStaticFloatMethodA,
  FNI_CallStaticDoubleMethod,
  FNI_CallStaticDoubleMethodV,
  FNI_CallStaticDoubleMethodA,
  FNI_CallStaticVoidMethod,
  FNI_CallStaticVoidMethodV,
  FNI_CallStaticVoidMethodA,
            
  FNI_GetStaticFieldID,
            
  (typeof(&FNI_GetStaticObjectField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticBooleanField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticByteField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticCharField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticShortField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticIntField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticLongField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticFloatField)) FNI_Unimplemented,
  (typeof(&FNI_GetStaticDoubleField)) FNI_Unimplemented,
            
  (typeof(&FNI_SetStaticObjectField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticBooleanField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticByteField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticCharField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticShortField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticIntField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticLongField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticFloatField)) FNI_Unimplemented,
  (typeof(&FNI_SetStaticDoubleField)) FNI_Unimplemented,
            
  (typeof(&FNI_NewString)) FNI_Unimplemented,
  (typeof(&FNI_GetStringLength)) FNI_Unimplemented,
  (typeof(&FNI_GetStringChars)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseStringChars)) FNI_Unimplemented,
            
  (typeof(&FNI_NewStringUTF)) FNI_Unimplemented,
  (typeof(&FNI_GetStringUTFLength)) FNI_Unimplemented,
  (typeof(&FNI_GetStringUTFChars)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseStringUTFChars)) FNI_Unimplemented,
            
  (typeof(&FNI_GetArrayLength)) FNI_Unimplemented,
             
  (typeof(&FNI_NewObjectArray)) FNI_Unimplemented,
  (typeof(&FNI_GetObjectArrayElement)) FNI_Unimplemented,
  (typeof(&FNI_SetObjectArrayElement)) FNI_Unimplemented,
            
  (typeof(&FNI_NewBooleanArray)) FNI_Unimplemented,
  (typeof(&FNI_NewByteArray)) FNI_Unimplemented,
  (typeof(&FNI_NewCharArray)) FNI_Unimplemented,
  (typeof(&FNI_NewShortArray)) FNI_Unimplemented,
  (typeof(&FNI_NewIntArray)) FNI_Unimplemented,
  (typeof(&FNI_NewLongArray)) FNI_Unimplemented,
  (typeof(&FNI_NewFloatArray)) FNI_Unimplemented,
  (typeof(&FNI_NewDoubleArray)) FNI_Unimplemented,
            
  (typeof(&FNI_GetBooleanArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_GetByteArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_GetCharArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_GetShortArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_GetIntArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_GetLongArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_GetFloatArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_GetDoubleArrayElements)) FNI_Unimplemented,
            
  (typeof(&FNI_ReleaseBooleanArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseByteArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseCharArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseShortArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseIntArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseLongArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseFloatArrayElements)) FNI_Unimplemented,
  (typeof(&FNI_ReleaseDoubleArrayElements)) FNI_Unimplemented,
            
  (typeof(&FNI_GetBooleanArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_GetByteArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_GetCharArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_GetShortArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_GetIntArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_GetLongArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_GetFloatArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_GetDoubleArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetBooleanArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetByteArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetCharArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetShortArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetIntArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetLongArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetFloatArrayRegion)) FNI_Unimplemented,
  (typeof(&FNI_SetDoubleArrayRegion)) FNI_Unimplemented,
            
  (typeof(&FNI_RegisterNatives)) FNI_Unimplemented,
  FNI_UnregisterNatives,
            
  FNI_MonitorEnter,
  FNI_MonitorExit,
            
#if 0
  FNI_GetJavaVM,
#endif
};
