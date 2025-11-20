"""
Test script to demonstrate why pendulum heuristic output differs
when data is structured as jobs-rows vs jobs-columns
"""

from heuristics import pendulum_heuristic
from makespan import calculate_makespan
import numpy as np

# Example: 5 jobs, 3 machines
# The test.fsp file has data formatted as:
#   7 4 9 3 6   (machine 0: times for jobs 0,1,2,3,4)
#   5 8 6 9 4   (machine 1: times for jobs 0,1,2,3,4)
#   9 3 7 4 8   (machine 2: times for jobs 0,1,2,3,4)

# This is JOBS AS COLUMNS (each row is a machine)
data_jobs_as_columns = [
    [7, 4, 9, 3, 6],  # Machine 0: processing times for 5 jobs
    [5, 8, 6, 9, 4],  # Machine 1: processing times for 5 jobs
    [9, 3, 7, 4, 8],  # Machine 2: processing times for 5 jobs
]

# Expected format: JOBS AS ROWS (each row is a job, columns are machines)
# We need to transpose to get:
data_jobs_as_rows = [
    [7, 5, 9],  # Job 0: times on machines 0,1,2
    [4, 8, 3],  # Job 1: times on machines 0,1,2
    [9, 6, 7],  # Job 2: times on machines 0,1,2
    [3, 9, 4],  # Job 3: times on machines 0,1,2
    [6, 4, 8],  # Job 4: times on machines 0,1,2
]

print("=" * 70)
print("ANALYSIS: Why Pendulum Heuristic Output Differs")
print("=" * 70)

print("\n1. DATA STRUCTURE EXPLANATION:")
print("-" * 70)
print("Your code expects: processing_times[job_idx][machine_idx]")
print("  - processing_times[i] = all machine times for job i")
print("  - processing_times[i][j] = time for job i on machine j")

print("\n2. JOBS-AS-ROWS (CORRECT FORMAT):")
print("-" * 70)
print("Each row = one job, each column = one machine")
print("Matrix structure:")
for i, job in enumerate(data_jobs_as_rows):
    print(f"  Job {i}: {job} (times on machines 0, 1, 2)")

print("\n3. JOBS-AS-COLUMNS (WRONG FORMAT):")
print("-" * 70)
print("Each row = one machine, each column = one job")
print("Matrix structure:")
for i, machine in enumerate(data_jobs_as_columns):
    print(f"  Machine {i}: {machine} (times for jobs 0, 1, 2, 3, 4)")

print("\n" + "=" * 70)
print("4. RUNNING PENDULUM HEURISTIC ON BOTH FORMATS:")
print("=" * 70)

# Run pendulum on correct format (jobs as rows)
print("\nA. JOBS-AS-ROWS (CORRECT):")
print("-" * 70)
sequence_rows = pendulum_heuristic(data_jobs_as_rows)
makespan_rows = calculate_makespan(data_jobs_as_rows, sequence_rows)

print(f"Sequence: {sequence_rows}")
print(f"Makespan: {makespan_rows}")

# Calculate job totals for jobs-as-rows
print("\nJob totals (sum across machines):")
for i in range(len(data_jobs_as_rows)):
    total = sum(data_jobs_as_rows[i])
    m1_time = data_jobs_as_rows[i][0]
    print(f"  Job {i}: total={total}, machine0_time={m1_time}")

# Run pendulum on wrong format (jobs as columns) - this will give wrong results!
print("\nB. JOBS-AS-COLUMNS (WRONG - what happens if you don't transpose):")
print("-" * 70)
sequence_columns = pendulum_heuristic(data_jobs_as_columns)
# Note: This will fail or give wrong results because makespan expects jobs-rows format
print(f"Sequence (wrong!): {sequence_columns}")
print("WARNING: This is interpreting machines as jobs!")

# Calculate what the heuristic "sees" when given jobs-as-columns
print("\nWhat the heuristic sees (treating machines as jobs):")
for i in range(len(data_jobs_as_columns)):
    total = sum(data_jobs_as_columns[i])
    m1_time = data_jobs_as_columns[i][0]
    print(f"  'Job' {i} (actually Machine {i}): total={total}, 'machine0'={m1_time}")

print("\n" + "=" * 70)
print("5. THE ROOT CAUSE:")
print("=" * 70)
print("""
The pendulum heuristic algorithm works as follows:

1. Calculate total processing time for each job:
   totals[j] = sum(processing_times[j])  # Sums across machines
   
2. Calculate machine-1 time for each job:
   m1_times[j] = processing_times[j][0]  # Time on first machine
   
3. Choose first job: min(m1_times[j], ...)
   
4. Sort remaining by total time, then place in pendulum pattern

WHEN DATA IS JOBS-AS-COLUMNS (WRONG):
  - processing_times[0] = [7, 4, 9, 3, 6]  # Actually Machine 0's times!
  - The heuristic thinks this is Job 0 with 5 "machines"
  - totals[0] = 7+4+9+3+6 = 29  # Sum of all job times on machine 0
  - m1_times[0] = 7  # Actually the time for job 0 on machine 0
  
WHEN DATA IS JOBS-AS-ROWS (CORRECT):
  - processing_times[0] = [7, 5, 9]  # Job 0's times on 3 machines
  - totals[0] = 7+5+9 = 21  # Sum across machines for job 0
  - m1_times[0] = 7  # Time for job 0 on machine 0

These are COMPLETELY DIFFERENT calculations, leading to different sequences!
""")

print("\n" + "=" * 70)
print("6. VERIFICATION:")
print("=" * 70)
print("\nIf you transpose jobs-as-columns, you should get jobs-as-rows:")
transposed = list(map(list, zip(*data_jobs_as_columns)))
print("Transposed matrix:")
for i, job in enumerate(transposed):
    print(f"  Job {i}: {job}")

print("\n[OK] This matches the jobs-as-rows format!")
print("\nSOLUTION: Always ensure your data is in jobs-rows format!")
print("  - If data comes as jobs-columns, transpose it first")
print("  - processing_times[job_idx][machine_idx] is the expected format")

