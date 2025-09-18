# Flow Shop Scheduling Problem Solver

A comprehensive Python system for solving the Flow Shop Scheduling Problem using constructive heuristics and improvement algorithms.

## Features

- **Flexible CSV Input**: Handles CSV files with or without headers, automatically detects format
- **Multiple Heuristics**: Implements NEH, Palmer, CDS, SPT, LPT, and Johnson's rule
- **Improvement Algorithms**: Local search (2-opt, insertion), Variable Neighborhood Search, and Genetic Algorithm
- **Comprehensive Analysis**: Detailed makespan calculation, utilization metrics, and sequence analysis
- **Modular Design**: Clean separation of concerns across multiple modules
- **Error Handling**: Robust validation and error reporting for input data

## Installation

1. Clone or download the project files
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Run with sample data (automatically generated)
python main.py

# Run with your own CSV file
python main.py your_data.csv
python main.py sample_flow_shop_data.csv
python main.py test_data_no_headers.csv
```

#### Improvement Method Selection
```bash
# Run only NEH heuristic (no improvements)
python main.py your_data.csv --no-improvements

# Use specific improvement methods
python main.py your_data.csv --methods 2opt
python main.py your_data.csv --methods insert
python main.py your_data.csv --methods vns
python main.py your_data.csv --methods genetic

# Combine multiple methods
python main.py your_data.csv --methods 2opt insert
python main.py your_data.csv --methods vns genetic
python main.py your_data.csv --methods 2opt insert vns genetic
```

#### Output Control
```bash
# Quiet mode (minimal output - just final results)
python main.py your_data.csv --quiet

# Full verbose output (default)
python main.py your_data.csv
```

#### Sample Data Generation
```bash
# Create sample data with default size (5 jobs, 3 machines)
python main.py --create-sample sample.csv

# Create custom sized sample data
python main.py --create-sample sample.csv --sample-jobs 6 --sample-machines 4
python main.py --create-sample large_test.csv --sample-jobs 10 --sample-machines 5
python main.py --create-sample small_test.csv --sample-jobs 3 --sample-machines 2
```

#### Complete Examples
```bash
# Quick analysis with genetic algorithm only
python main.py data.csv --methods genetic --quiet

# Comprehensive analysis with all methods
python main.py data.csv --methods 2opt insert vns genetic

# Fast local search only (for large problems)
python main.py large_data.csv --methods 2opt insert

# Generate and solve custom problem
python main.py --create-sample test.csv --sample-jobs 8 --sample-machines 4
python main.py test.csv --methods vns genetic
```

### Programmatic Usage

```python
from main import solve_flow_shop

# Solve with default settings
results = solve_flow_shop('data.csv')

# Access results
best_sequence = results['best_sequence']
best_makespan = results['best_makespan']
job_names = results['job_names']
```

## CSV Input Format

The system accepts two CSV formats:

### With Headers
```csv
Machine_1,Machine_2,Machine_3
5,3,8
7,2,6
4,9,3
```

### Without Headers (numbers only)
```csv
5,3,8
7,2,6
4,9,3
```

Each row represents a job, and each column represents processing time on a machine.

## Modules

### `io_utils.py`
- CSV reading and validation
- Automatic header detection
- Data consistency checking
- Error handling for malformed data

### `makespan.py`
- Makespan calculation for job sequences
- Completion time matrix generation
- Machine utilization analysis
- Sequence quality evaluation

### `heuristics.py`
- **NEH (Nawaz-Enscore-Ham)**: Primary constructive heuristic
- **Palmer**: Slope-based heuristic
- **CDS**: Campbell, Dudek, and Smith heuristic
- **SPT/LPT**: Shortest/Longest Processing Time first
- **Johnson's Rule**: Optimal for 2-machine problems

### `improvements.py`
- **2-opt Local Search**: Swap-based neighborhood search
- **Insertion Local Search**: Position-based neighborhood search
- **Variable Neighborhood Search**: Multi-neighborhood approach
- **Genetic Algorithm**: Population-based metaheuristic

### `main.py`
- Entry point and orchestration
- Command-line interface
- Result formatting and display

## Algorithm Details

### NEH Heuristic
1. Sort jobs by decreasing total processing time
2. Start with the job having the highest total time
3. For each remaining job, insert it at the position that minimizes makespan
4. Continue until all jobs are scheduled

### Improvement Methods

#### Local Search Algorithms

**2-opt Local Search (`2opt`)**
- **Method**: Swap-based neighborhood search
- **Complexity**: O(n²) per iteration
- **How it works**: Tries all possible pairs of job swaps to find improvements
- **Parameters**: Max iterations (1000)
- **Best for**: Quick improvements with minimal computational cost

**Insertion Local Search (`insert`)**
- **Method**: Position-based neighborhood search  
- **Complexity**: O(n²) per iteration
- **How it works**: Moves each job to every other position to find better sequences
- **Parameters**: Max iterations (1000)
- **Best for**: Finding different sequence structures than swap-based methods

#### Metaheuristic Algorithms

**Variable Neighborhood Search (`vns`)**
- **Method**: Multi-neighborhood approach with perturbation
- **How it works**: Combines 2-opt and insertion search with random perturbations
- **Parameters**: Max iterations (100), perturbation swaps (2)
- **Features**: Escapes local optima through diversification
- **Best for**: Balanced exploration and exploitation

**Genetic Algorithm (`genetic`)**
- **Method**: Population-based evolutionary algorithm
- **Default Parameters**:
  - Population size: 50
  - Mutation rate: 0.1 (10%)
  - Crossover rate: 0.8 (80%)
  - Elite size: 5
  - Generations: 50 (for improvements), 100 (standalone)
- **Operators**:
  - **Selection**: Tournament selection (size 3)
  - **Crossover**: Order crossover (OX) for permutation representation
  - **Mutation**: Swap mutation
  - **Replacement**: Elitism with generational replacement
- **Best for**: Complex problems where local search gets trapped

## Example Output

```
============================================================
FLOW SHOP SCHEDULING PROBLEM SOLVER
============================================================
Reading data from: sample_flow_shop_data.csv

=== Data Summary ===
Number of jobs: 5
Number of machines: 3
Job names: Job_1, Job_2, Job_3, Job_4, Job_5
Processing time range: 2.00 - 19.00
Average processing time: 10.47
====================

Applying NEH heuristic for initial solution...
NEH Heuristic Result:
  Sequence: Job_4 -> Job_1 -> Job_5 -> Job_2 -> Job_3
  Makespan: 43.00

=== Heuristic Comparison ===
Heuristic  Makespan   Sequence
--------------------------------------------------
NEH        43.00      Job_4 -> Job_1 -> Job_5 -> Job_2 -> Job_3
CDS        43.00      Job_4 -> Job_1 -> Job_5 -> Job_2 -> Job_3
Palmer     45.00      Job_4 -> Job_1 -> Job_2 -> Job_5 -> Job_3
LPT        45.00      Job_4 -> Job_1 -> Job_2 -> Job_5 -> Job_3
SPT        49.00      Job_3 -> Job_2 -> Job_5 -> Job_1 -> Job_4
==================================================

Applying improvement algorithms...

=== Improvement Results ===
Method     Makespan   Improvement 
-----------------------------------
Initial    43.00      baseline    
2opt       43.00      0.0%        
Insert     43.00      0.0%        
Vns        43.00      0.0%        
===================================

============================================================
FINAL RESULTS
============================================================
Best sequence: Job_4 -> Job_1 -> Job_5 -> Job_2 -> Job_3
Best makespan: 43.00
Improvement over NEH: 0.0%
============================================================
```

## Performance Considerations

### Algorithm Complexity
- **NEH heuristic**: O(n³m) where n = jobs, m = machines
- **2-opt local search**: O(n² × iterations) - typically fast
- **Insertion local search**: O(n² × iterations) - similar to 2-opt
- **Variable Neighborhood Search**: O(n² × iterations × neighborhoods) - moderate
- **Genetic algorithm**: O(population × generations × n × m) - most intensive

### Performance Comparison

| Method | Speed | Quality | Memory Usage | Recommended For |
|--------|-------|---------|--------------|-----------------|
| `2opt` | ⚡ Very Fast | Good | Low | Quick optimization |
| `insert` | ⚡ Very Fast | Good | Low | Alternative neighborhoods |
| `vns` | 🔄 Medium | Better | Medium | Balanced approach |
| `genetic` | 🐌 Slow | Best | High | Complex/large problems |

### Scaling Guidelines
- **Small problems** (≤10 jobs): Use all methods
- **Medium problems** (11-20 jobs): Skip genetic or reduce generations
- **Large problems** (>20 jobs): Use only local search methods
- **Very large problems** (>50 jobs): Consider NEH only for initial assessment

## Error Handling

The system validates:
- File existence and readability
- CSV format consistency
- Non-negative processing times
- Consistent number of machines per job
- Valid job sequences

## Contributing

The modular design makes it easy to add new heuristics or improvement methods:

1. Add new heuristics to `heuristics.py`
2. Add new improvement methods to `improvements.py`
3. Update the main solver to include new methods
4. Follow PEP8 coding conventions

## License

This project is provided as-is for educational and research purposes.
