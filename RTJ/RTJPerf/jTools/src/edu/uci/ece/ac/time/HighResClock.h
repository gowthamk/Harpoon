// DO NOT EDIT THIS FILE - it is machine generated -*- c++ -*-

#ifndef __edu_uci_ece_ac_time_HighResClock__
#define __edu_uci_ece_ac_time_HighResClock__

#pragma interface

#include <java/lang/Object.h>

extern "Java"
{
  namespace edu
  {
    namespace uci
    {
      namespace ece
      {
        namespace ac
        {
          namespace time
          {
            class HighResClock;
            class HighResTime;
          }
        }
      }
    }
  }
};

class ::edu::uci::ece::ac::time::HighResClock : public ::java::lang::Object
{
public:
  static ::edu::uci::ece::ac::time::HighResTime *getTime ();
  static void getTime (::edu::uci::ece::ac::time::HighResTime *);
  static jlong getClockTickCount ();
  static ::edu::uci::ece::ac::time::HighResTime *clockTick2HighResTime (jlong);
  static void clockTick2HighResTime (jlong, ::edu::uci::ece::ac::time::HighResTime *);
  static jfloat getClockFrequency ();
  static jdouble getClockPeriod ();
  HighResClock ();

  static ::java::lang::Class class$;
};

#endif /* __edu_uci_ece_ac_time_HighResClock__ */
