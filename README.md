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

```bash
# Run with sample data (automatically generated)
python main.py

# Run with your own CSV file
python main.py your_data.csv

# Run only NEH heuristic (no improvements)
python main.py your_data.csv --no-improvements

# Use specific improvement methods
python main.py your_data.csv --methods 2opt insert

# Quiet mode (minimal output)
python main.py your_data.csv --quiet

# Create sample data
python main.py --create-sample sample.csv --sample-jobs 6 --sample-machines 4
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
- **2-opt**: Tries all possible job swaps to find improvements
- **Insert**: Tries moving each job to every other position
- **VNS**: Combines multiple neighborhood structures with perturbation
- **Genetic**: Evolves a population of solutions using crossover and mutation

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

- NEH heuristic: O(n³m) where n = jobs, m = machines
- Local search methods: Depends on neighborhood size and iterations
- Genetic algorithm: Most computationally intensive but often finds better solutions
- For large problems (>20 jobs), consider using fewer improvement methods

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
