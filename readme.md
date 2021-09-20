# Prediction Failure Handling Simulation

## Overview

This simulation is part of a master thesis that is concerned with designing and implementing a prediction failure handling component.
The code in this project was primarily used to understand the behaviour of different prediction failure handling approaches. The project contains two runnable scripts.

1. simulation.py: Starts a test run
2. visualization/vis.py: Visualizes the last run based on the logs in **/logs**

## Examples


## Run it
### Dependencies
The simulation uses no dependencies, except numpy and matplotlib. Using pip, both modules can be installed with the following line:

    sudo pip3 install numpy matplotlib

### Configuration

In order to be able to run the simulation, the base directory has to be set in **config.py**:

    PROJECT_BASE: str = "/home/ml/Dropbox/Master-Arbeit/code/threshold_simulation"

### Makefile

Using the **Makefile**, the project can be run in four different ways:

1. `make run`: Runs the simulation using the plan saved in `logs/plan.log`
1. `make run_new`: Generates a new plan and runs it
1. `make vis`: Uses the current files in `logs` and generates a visualization corresponding to the previous logged run
1. `make run_vis`: Combines `run` and `vis`
