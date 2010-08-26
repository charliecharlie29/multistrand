/*
   Copyright (c) 2007-2008 Caltech. All rights reserved.
   Coded by: Joseph Schaeffer (schaeffer@dna.caltech.edu)
*/
 
/* Move class and Move Tree class header */ 

#ifndef __MOVE_H__
#define __MOVE_H__

#define MOVE_INVALID 0
#define MOVE_CREATE  1
#define MOVE_DELETE  2
#define MOVE_SHIFT   4
#define MOVE_1       8
#define MOVE_2      16
#define MOVE_3      32

class Loop;

class Move
{
 public:
  Move( void );
  Move( int mtype, double mrate, Loop *affected_1, int index1, int index2 );
  Move( int mtype, double mrate, Loop *affected_1, int index1, int index2, int index3 );
  Move( int mtype, double mrate, Loop *affected_1, int index1, int index2, int index3, int index4 );
  Move( int mtype, double mrate, Loop *affected_1, int *indexarray );
  Move( int mtype, double mrate, Loop *affected_1, Loop *affected_2, int index1, int index2 );
  Move( int mtype, double mrate, Loop *affected_1, Loop *affected_2, int index1 );
  ~Move( void );
  double getRate( void );
  int getType( void );
  Loop *getAffected( int index );
  Loop *doChoice( void );
  friend class Loop;
  friend class HairpinLoop;
  friend class StackLoop;
  friend class InteriorLoop;
  friend class MultiLoop;
  friend class OpenLoop;
  friend class BulgeLoop;
  friend class StrandComplex;
 protected:
  int type;
  double rate;
  int index[4];
  Loop *affected[2];
};


class MoveContainer
{
 public:
  MoveContainer( void );
  virtual ~MoveContainer( void );
  virtual void addMove( Move *newmove ) = 0;
  // virtual void deleteMove( Move *oldmove ) = 0;
  // virtual void deleteMove( MoveContainer *oldcontainer ) = 0;
  double getRate( void );
  virtual void resetDeleteMoves( void ) = 0;
  virtual Move *getChoice( double *rnd ) = 0;
  virtual Move *getMove( Move *iterator ) = 0;  
 protected:
  double totalrate;

};

// not using this storage method yet... refer to the list...
class MoveTree : public Move
{
 public:
  ~MoveTree( void );

 private:
  Move *left, *right; // also an uplink?
  double totalrate;
};

class MoveList : public MoveContainer
{
 public:
  MoveList( int initial_size );
  ~MoveList( void );
  void addMove( Move *newmove );
  Move *getChoice( double *rnd );
  Move *getMove( Move *iterator );
  void resetDeleteMoves( void );
  //  friend class Move;
 private:
  Move **moves;
  Move **del_moves;
  int moves_size;
  int moves_index;
  int del_moves_size;
  int del_moves_index;
  int int_index;
};

#endif