/* manage local references */
#include <jni.h>
#include <jni-private.h>

#include <assert.h>
#include <stdlib.h>
#include "config.h"
#ifdef WITH_DMALLOC
#include "dmalloc.h"
#endif
#ifdef BDW_CONSERVATIVE_GC
#include "gc.h"
#endif
#include "flexthread.h"

jobject FNI_NewLocalRef(JNIEnv *env, jobject_unwrapped obj) {
  struct FNI_Thread_State *fts = (struct FNI_Thread_State *) env;
  if (obj==NULL) return NULL; /* null stays null. */
  fts->localrefs_next->obj = obj;
  return (jobject) fts->localrefs_next++;
}

/* convenience function for runtime jni stub */
jobject_unwrapped FNI_Unwrap(jobject obj) {
  return FNI_UNWRAP(obj);
}

/* clear local refs in stack frame */
void FNI_DeleteLocalRefsUpTo(JNIEnv *env, jobject markerRef) {
  struct FNI_Thread_State *fts = (struct FNI_Thread_State *) env;
  fts->localrefs_next = markerRef;
}

void FNI_DeleteLocalRef(JNIEnv *env, jobject localRef) {
  struct FNI_Thread_State *fts = (struct FNI_Thread_State *) env;
  assert(FNI_NO_EXCEPTIONS(env));
  /* can't delete it w/o a lot of work; we just zero it out */
  localRef->obj=NULL; /* won't keep anything live */
}

/*-----------------------------------------------------------------*/
FLEX_MUTEX_DECLARE_STATIC(globalref_mutex);

/* global refs are stored in a doubly-linked list */
jobject FNI_NewGlobalRef(JNIEnv * env, jobject obj) {
  jobject_globalref result;
  assert(FNI_NO_EXCEPTIONS(env));
  assert(obj!=NULL);
  /* malloc away... */
  result = 
#ifdef BDW_CONSERVATIVE_GC
    GC_malloc_uncollectable
#else /* okay, use system-default malloc */
    malloc
#endif
    (sizeof(*result));
  result->jobject.obj = obj->obj;
  /* acquire global lock */
  FLEX_MUTEX_LOCK(&globalref_mutex);
  result->next = FNI_globalrefs.next;
  result->prev = &FNI_globalrefs;
  if (result->next) result->next->prev = result;
  FNI_globalrefs.next = result;
  /* release global lock */
  FLEX_MUTEX_UNLOCK(&globalref_mutex);
  /* done. */
  return (jobject) result;
}

void FNI_DeleteGlobalRef (JNIEnv *env, jobject _globalRef) {
  jobject_globalref globalRef = (jobject_globalref) _globalRef;
  assert(FNI_NO_EXCEPTIONS(env));
  /* acquire global lock */
  FLEX_MUTEX_LOCK(&globalref_mutex);
  /* always a prev, due to header; not always a next */
  globalRef->prev->next = globalRef->next;
  if (globalRef->next) globalRef->next->prev = globalRef->prev;
  /* release global lock */
  FLEX_MUTEX_UNLOCK(&globalref_mutex);
  /* clean up */
  globalRef->next = globalRef->prev = NULL; /* safety first */
#ifdef BDW_CONSERVATIVE_GC
  GC_free(globalRef);
#else /* system-default malloc... */
  free(globalRef);
#endif
}
