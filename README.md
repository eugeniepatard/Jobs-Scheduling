# Job Scheduling with Ant Colony Optimization (ACO)

## Project Description

This project implements a **static job scheduling** algorithm using the **Ant Colony Optimization (ACO)** approach. The goal is to efficiently schedule a set of tasks, optimizing the scheduling process through ACO and parallelizing parts of the computation using **OpenMPI** for enhanced performance.

The project was completed by a team of five members, and we used the ant algorithm to dispatch tasks. Our implementation is aimed at finding the optimal task assignment by simulating how ants solve optimization problems in nature.

## Features

- **Ant Colony Optimization**: The main algorithm used to dispatch and schedule jobs.
- **Parallelization**: Parts of the algorithm were parallelized using **OpenMPI** to improve performance on large task sets.
- **Visualization**: A visual representation of the job scheduling results is provided for better analysis and understanding.

## Repository Structure

The project contains several scripts to handle the different aspects of the scheduling algorithm:

### 1. `ACO_functions.py`

This script contains the core logic for the Ant Colony Optimization algorithm. It simulates how ants choose the next task by evaluating the desirability of each available task, based on a combination of task priority and pheromone levels. The algorithm updates the set of available tasks as jobs are completed and recalculates the probabilities for selecting the next task. It continually refines the solution by mimicking the way ants update their environment and adapt based on the trails they leave behind. The script is crucial for determining task order and optimizing the scheduling process by balancing exploration and exploitation, similar to how ants search for the best path.


### 2. `ACO_load_data.py`

This script is used to **load task data** from JSON files and convert them into a format that the algorithm can process. The tasks have dependencies and durations which are essential for scheduling. The script loads this information and creates a directed graph of tasks.

#### Input Data Format

The task data is stored in a JSON file with the following structure:

- **`nodes`**: Contains the list of tasks.
  - Each task has a **`Data`** field (in `HH:MM:SS` format) that represents the job duration.
  - **`Dependencies`**: A list of parent tasks (preceding jobs that must finish before the task can start).
  
Example of a node in the JSON file:
```json
{
  "nodes": {
    "1": {
      "Data": "00:30:00",  # Duration of 30 minutes
      "Dependencies": [0]   # Must start after task 0
    }
  }
}
