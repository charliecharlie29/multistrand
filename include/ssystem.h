/*
 Copyright (c) 2007-2008 Caltech. All rights reserved.
 Coded by: Joseph Schaeffer (schaeffer@dna.caltech.edu)
 */

/* SimulationSystem class header. This is the main object which controls the entire simulated system. */

#ifndef __SSYSTEM_H__
#define __SSYSTEM_H__

#include "energymodel.h"
#include "scomplexlist.h"
#include <vector>

typedef std::vector<bool> boolvector;
typedef std::vector<bool>::iterator boolvector_iterator;

class SimulationSystem {
public:
	SimulationSystem(SimOptions* options);
	SimulationSystem(PyObject* system_options);
	SimulationSystem(void);

	// helper method for constructors
	void construct(void);

	~SimulationSystem(void);

	void StartSimulation(void);
	void InitialInfo(void);	// printing function
	void printTransition(double); // printing function

	PyObject *calculateEnergy(PyObject *start_state, int typeflag);
	int getErrorFlag(void);

private:
	void StartSimulation_Standard(void);
	void StartSimulation_FirstStep(void);
	void StartSimulation_Trajectory(void);
	void StartSimulation_Transition(void);

	void SimulationLoop_Standard(void);
	void SimulationLoop_FirstStep(void);
	void SimulationLoop_Trajectory(long ointerval, double otime);
	void SimulationLoop_Transition(void);

	int InitializeSystem(PyObject *alternate_start = NULL);

	void InitializeRNG(void);
	void generateNextRandom(void);
	void finalizeRun(void);

	// helper function for sending current state to Python side
	void dumpCurrentStateToPython(void);
	void sendTrajectory_CurrentStateToPython(double current_time);
	void sendTransitionStateVectorToPython(boolvector transition_states,
			double current_time);


	void printAllMoves(void);


	EnergyModel *dnaEnergyModel;

	StrandComplex *startState;
	SComplexList *complexList;

	PyObject *system_options;
	SimOptions *simOptions;

	long current_seed;
	bool initial_trajectory;
	long simulation_mode;
	long simulation_count_remaining;
};

#endif
