#include "specs/x86/cache_aux.h"
int getfield(int type, int fieldindex);
int isArray(int type, int fieldindex);
int isPtr(int type, int fieldindex);
int numElements(int type, int fieldindex);
int size(int type);
int sizeBytes(int type);
int getnumfields(int type);
bool issubtype(int subtype, int type);
void computesizes(struct foo_state *);
