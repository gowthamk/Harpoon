#ifndef TABLE_SIZE
#define TABLE_SIZE 102407
#endif
#ifndef HASH
#define HASH(key,obj) ((((int)key)+((int)obj))%TABLE_SIZE)
#endif

/* #define MAKE_POINTER_VERSION to make a version that doesn't prevent
 * objects or values from being garbage collected (i'm assuming keys
 * are statically allocated).  Only non-null values are considered
 * legit (i.e. 'default_value' should always be NULL). */

struct TABLE_ELEMENT {
  void *key, *obj;
  TYPE value;
} TABLE[TABLE_SIZE]; /* should be initialized to all zeroes */
/* tombstone has obj==null, but key non-null. */
/* (when MAKE_POINTER_VERSION, tombstone has value==null) */

#ifdef MAKE_POINTER_VERSION
# define hideobj(x) ((void *) HIDE_POINTER(obj))
# define TOMB value
#else
# define hideobj(x) x
# define TOMB obj
#endif

/* quadratic hashing (i think that's what it is) */

static TYPE GET(void *key, void *obj, TYPE default_value) {
  struct TABLE_ELEMENT *t;
  int hash = HASH(key, obj);
  obj = hideobj(obj);
  for (t=&TABLE[hash]; t->key!=NULL; t=&TABLE[hash]) {
    if (t->key==key && t->obj==obj) return t->value;
    hash = (hash*hash) % TABLE_SIZE;
  }
  return default_value;
}
static void REMOVE(void *key, void *obj) {
  struct TABLE_ELEMENT *t;
  int hash = HASH(key, obj);
  obj = hideobj(obj);
  for (t=&TABLE[hash]; t->key!=NULL; t=&TABLE[hash]) {
    if (t->key==key && t->obj==obj) { /* found it */
      t->TOMB = NULL; /* leave a tombstone */
      GC_unregister_disappearing_link(&(t->TOMB));
      return;
    }
    hash = (hash*hash) % TABLE_SIZE;
  }
  /* not found */
  return;
}
static void SET(void *key, void *obj, TYPE newval, TYPE default_value) {
  struct TABLE_ELEMENT *t;
  int hash;
#ifdef MAKE_POINTER_VERSION
  assert(default_value==NULL); /* doesn't work otherwise */
#endif
  if (newval==default_value) {
    REMOVE(key, obj);
    return;
  }
  hash = HASH(key, obj);
  for (t=&TABLE[hash]; t->TOMB!=NULL; t=&TABLE[hash]) {
    hash = (hash*hash) % TABLE_SIZE;
  }
  /* found either an empty spot or a tombstone */
  t->key = key; t->obj = hideobj(obj); t->value = newval;
  GC_general_register_disappearing_link(&(t->TOMB), obj);
  return;
}

#undef hideobj
#undef TOMB
