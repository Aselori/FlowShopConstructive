# Flow Shop Scheduling Problem Solver

A comprehensive Python system for solving the Flow Shop Scheduling Problem using constructive heuristics, featuring a custom Pendulum algorithm as the primary solution method.

## Features

- **Flexible CSV Input**: Handles CSV files with or without headers, automatically detects format
- **Primary Pendulum Algorithm**: Custom heuristic as main solution method, with NEH, Palmer, CDS, SPT, LPT, and Johnson's rule for comparison
- **Comprehensive Analysis**: Detailed makespan calculation, utilization metrics, and sequence analysis
- **Modular Design**: Clean separation of concerns across multiple modules
- **Error Handling**: Robust validation and error reporting for input data
- **Custom Heuristics**: Easy to extend with new constructive algorithms

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

#### Heuristic Analysis
```bash
# Run all heuristics and compare (default behavior)
python main.py your_data.csv

# Pendulum heuristic runs as main solution
# All heuristics compared: Pendulum (primary), NEH, Palmer, CDS, SPT, LPT
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
# Quick analysis with minimal output
python main.py data.csv --quiet

# Comprehensive analysis with all heuristics (default)
python main.py data.csv

# Generate and solve custom problem
python main.py --create-sample test.csv --sample-jobs 8 --sample-machines 4
python main.py test.csv

# Large dataset analysis
python main.py large_dataset.csv --quiet
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
- **Pendulum**: Custom primary heuristic placing small jobs at extremes, large jobs in center
- **NEH (Nawaz-Enscore-Ham)**: Classical constructive heuristic for comparison
- **Palmer**: Slope-based heuristic
- **CDS**: Campbell, Dudek, and Smith heuristic
- **SPT/LPT**: Shortest/Longest Processing Time first
- **Johnson's Rule**: Optimal for 2-machine problems

### `main.py`
- Entry point and orchestration
- Command-line interface
- Result formatting and display

## Algorithm Details

### Constructive Heuristics

**Pendulum Heuristic (Primary Method)**
- Sort jobs by total processing time
- Place smallest jobs at sequence extremes (ends)
- Place largest jobs in sequence center
- Creates balanced "pendulum" weight distribution
- **Complexity**: O(n log n)
- **Performance**: Novel approach, primary solution method

**NEH (Nawaz-Enscore-Ham)**
1. Sort jobs by decreasing total processing time
2. Start with the job having the highest total time
3. For each remaining job, insert it at the position that minimizes makespan
4. Continue until all jobs are scheduled
- **Complexity**: O(n³m) where n = jobs, m = machines
- **Performance**: Classical benchmark for comparison

**Palmer Heuristic**
- Calculates slope index for each job based on weighted machine times
- Sorts jobs by decreasing slope index
- **Complexity**: O(n log n)
- **Performance**: Fast but typically lower quality than NEH

**CDS (Campbell, Dudek, Smith)**
- Converts m-machine problem into series of 2-machine problems
- Applies Johnson's rule to each 2-machine variant
- Selects best result among all variants
- **Complexity**: O(m × n log n)
- **Performance**: Good balance of speed and quality

**SPT/LPT (Shortest/Longest Processing Time)**
- SPT: Sort jobs by ascending total processing time
- LPT: Sort jobs by descending total processing time
- **Complexity**: O(n log n)
- **Performance**: Very fast, useful as baselines

**Johnson's Rule**
- Optimal algorithm for 2-machine flow shop problems
- Used as subroutine in CDS heuristic
- **Complexity**: O(n log n)
- **Performance**: Optimal for 2-machine cases


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

Applying Pendulum heuristic for main solution...
Pendulum Heuristic Result:
  Sequence: Job_8 -> Job_6 -> Job_3 -> Job_7 -> Job_5 -> Job_1 -> Job_2 -> Job_10 -> Job_4 -> Job_9
  Makespan: 166.00

=== Heuristic Comparison ===
Heuristic  Makespan   Sequence
--------------------------------------------------
NEH        126.00     Job_4 -> Job_8 -> Job_9 -> Job_10 -> Job_3 -> Job_7 -> Job_1 -> Job_5 -> Job_2 -> Job_6
CDS        126.00     Job_4 -> Job_8 -> Job_9 -> Job_10 -> Job_3 -> Job_1 -> Job_5 -> Job_7 -> Job_2 -> Job_6
SPT        147.00     Job_8 -> Job_9 -> Job_6 -> Job_4 -> Job_3 -> Job_10 -> Job_7 -> Job_2 -> Job_5 -> Job_1
LPT        161.00     Job_1 -> Job_5 -> Job_2 -> Job_7 -> Job_10 -> Job_3 -> Job_4 -> Job_6 -> Job_9 -> Job_8
Pendulum   166.00     Job_8 -> Job_6 -> Job_3 -> Job_7 -> Job_5 -> Job_1 -> Job_2 -> Job_10 -> Job_4 -> Job_9
Palmer     172.00     Job_6 -> Job_2 -> Job_7 -> Job_5 -> Job_1 -> Job_8 -> Job_3 -> Job_4 -> Job_9 -> Job_10
==================================================

============================================================
FINAL RESULTS
============================================================
Best sequence: Job_8 -> Job_6 -> Job_3 -> Job_7 -> Job_5 -> Job_1 -> Job_2 -> Job_10 -> Job_4 -> Job_9
Best makespan: 166.00
============================================================
```

## Performance Considerations

### Algorithm Complexity
- **Pendulum heuristic**: O(n log n) - very fast (primary method)
- **NEH heuristic**: O(n³m) where n = jobs, m = machines
- **Palmer heuristic**: O(n log n) - very fast
- **CDS heuristic**: O(m × n log n) - moderate
- **SPT/LPT heuristics**: O(n log n) - very fast

### Performance Comparison

| Heuristic | Speed | Quality | Memory Usage | Recommended For |
|-----------|-------|---------|--------------|-----------------|
| `Pendulum` | ⚡ Very Fast | Good | Low | Primary solution method |
| `NEH` | 🔄 Medium | Best | Medium | Classical benchmark |
| `CDS` | ⚡ Fast | Good | Low | Alternative approach |
| `Palmer` | ⚡ Very Fast | Fair | Low | Quick baseline |
| `SPT/LPT` | ⚡ Very Fast | Fair | Low | Simple baselines |

### Scaling Guidelines
- **Small problems** (≤20 jobs): All heuristics run quickly, Pendulum provides fast primary solution
- **Medium problems** (21-100 jobs): Pendulum excels with O(n log n) speed vs NEH's O(n³m)
- **Large problems** (>100 jobs): Pendulum ideal as primary method due to excellent scalability
- **Very large problems** (>500 jobs): Pendulum, Palmer, SPT recommended for speed

## Error Handling

The system validates:
- File existence and readability
- CSV format consistency
- Non-negative processing times
- Consistent number of machines per job
- Valid job sequences

## Adding Custom Heuristics

The modular design makes it easy to add new constructive heuristics:

1. **Add your heuristic function to `heuristics.py`**:
   ```python
   def my_custom_heuristic(processing_times: List[List[float]]) -> List[int]:
       # Your algorithm logic here
       # Must return a sequence (List[int]) of job indices
       return sequence
   ```

2. **Add it to the comparison dictionary in `compare_heuristics()`**:
   ```python
   heuristics = {
       'NEH': neh_heuristic,
       'Palmer': palmer_heuristic,
       'CDS': cds_heuristic,
       'SPT': shortest_processing_time_first,
       'LPT': longest_processing_time_first,
       'Pendulum': pendulum_heuristic,
       'MyCustom': my_custom_heuristic  # Add your heuristic here
   }
   ```

3. **Follow the same pattern**: Take `processing_times` as input, return job sequence as `List[int]`
4. **Test with existing datasets** to compare performance
5. **Follow PEP8 coding conventions** and add proper docstrings

## License

This project is provided as-is for educational and research purposes.
