# Subwoofer Transmission Line Optimization

This project implements a simulation-driven evolutionary framework for optimizing subwoofer transmission line (TL) geometries. The system couples a genetic algorithm (DEAP) with acoustic simulation (ABEC3) in a closed-loop architecture.

## Architecture

The codebase is organized into four main components:

* **`genetic_algorithm.py`** – Top-level orchestration: population initialization, evolutionary operators, fitness assignment, and generation loop.
* **`auto_eval`** – Simulation interface: converts a duct list into an ABEC LEScript, executes the simulation, and loads spectral results.
* **`eval_function_file`** – Fitness layer: computes multi-objective metrics from SPL and phase data.
* **`custom_logger`** – Logs generation statistics and runtime information.

This separation cleanly isolates optimization logic from simulation and signal processing.

## Representation

A TL is encoded as a variable-length list of ducts:

```python
pipe = [(L1, D1), (L2, D2), ..., (Ln, Dn)]
```

Each individual (type `Pipe`) carries a multi-objective fitness vector. The representation supports both structural and parametric variation.

## Optimization Pipeline

1. **Initialization**
   Randomly generate pipes within geometric constraints.

2. **Evaluation**
   For each individual:

   * Generate ABEC script
   * Run LEM/FEM simulation
   * Extract SPL and phase data
   * Compute fitness metrics

3. **Evolutionary Cycle (per generation)**

   * Tournament selection
   * Crossover (sublist exchange)
   * Mutation (add/remove ducts or Gaussian parameter perturbation)
   * Re-evaluate modified individuals
   * Replace population (optional elitism)

The evaluation computes metrics such as passband SPL mean and deviation, bandwidth, phase stability, and group delay statistics.

## Design Space and Constraints

The search space is:

* Discrete in topology (number of ducts)
* Continuous in geometry (length and cross-section)
* Multi-objective in performance

Constraints include duct length bounds, cross-section limits, maximum duct count, fixed line width, and passband parameters.

## Execution

Run:

```bash
python genetic_algorithm.py
```

The `main()` function seeds the RNG, initializes the population, iterates for a fixed number of generations, and loads the best geometry into ABEC. The framework provides a modular template for simulation-based evolutionary optimization of acoustic systems.
