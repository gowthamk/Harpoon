#ifndef ROLE
#define ROLE
#include "RoleInference.h"
#include "CalculateDominators.h"

struct role {
  int hashcode;
  char * class;
  struct rolereferencelist * dominatingroots;
  struct rolefieldlist * pointedtofl;
  struct rolearraylist * pointedtoal;
  struct identity_relation * identities;
  struct rolefieldlist * nonnullfields;
};

struct rolereferencelist {
  char * classname;
  char * globalname;

  char * methodname;
  char * signature;
  char * lvname;
  char * sourcename;
  int linenumber;
  struct rolereferencelist *next;
};

struct rolearraylist {
  char *class;
  int duplicates;
  struct rolearraylist * next;
};

struct rolechange {
  long long origmethod;
  char *origrole;
  long long newmethod;
  char *newrole;
};

struct rolefieldlist {
  char * class;
  char * field;
  int duplicates;
  struct rolefieldlist * next;
};

void printrole(struct role * r, char * rolename);
void freerole(struct role * r);
struct role * calculaterole(struct genhashtable * dommapping,struct heap_object *ho);
struct identity_relation * find_identities(struct heap_object *ho);
void free_identities(struct identity_relation *irptr);
void print_identities(struct identity_relation *irptr);

void sortidentities(struct role *role);
int comparedomroots(struct rolereferencelist *r1, struct rolereferencelist *r2);
void insertdomroot(struct role * role, struct rolereferencelist * domroots);
void insertnonfl(struct role * role, struct rolefieldlist * domroots);
void insertrfl(struct role * role, struct rolefieldlist * domroots);
void insertral(struct role * role, struct rolearraylist * domroots);
int fieldcompare(struct rolefieldlist *field1, struct rolefieldlist *field2);
int compareidentity(struct identity_relation *ir1, struct identity_relation *ir2);
int equivalentroles(struct role *role1, struct role *role2);
void assignhashcode(struct role * role);
int rolehashcode(struct role *role);
int hashstring(char *strptr);
char * findrolestring(struct heap_state * heap, struct genhashtable * dommapping,struct heap_object *ho);
int equivalentstrings(char *str1, char *str2);
void setheapstate(struct heap_state *hs);
int rchashcode(struct rolechange *rc);
int equivalentrc(struct rolechange *rc1, struct rolechange *rc2);
void rolechange(struct heap_state *hs, struct heap_object *ho, char *newrole);
void printrolechange(struct heap_state * hs, struct rolechange *rc);
#endif
