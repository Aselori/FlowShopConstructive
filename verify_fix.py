"""
Verify the fix works correctly
"""

from io_utils import read_taillard_txt
from heuristics import pendulum_heuristic
from makespan import calculate_makespan
import os

print("=" * 70)
print("VERIFYING THE FIX")
print("=" * 70)

file_path = os.path.join("..", "Instances", "test.fsp")
processing_times, job_names = read_taillard_txt(file_path)

print("\nAfter reading test.fsp:")
print(f"Number of jobs: {len(processing_times)}")
print(f"Number of machines per job: {len(processing_times[0]) if processing_times else 0}")

print("\nMatrix structure (should be jobs-as-rows now):")
for i, job in enumerate(processing_times):
    total = sum(job)
    print(f"  Job {i}: {job} (total={total})")

print("\nVerification:")
print("Expected Job 0: [7, 5, 9] (from Machine 0: 7, Machine 1: 5, Machine 2: 9)")
print(f"Actual Job 0:   {processing_times[0]}")
if processing_times[0] == [7.0, 5.0, 9.0]:
    print("[OK] CORRECT!")
else:
    print("[X] WRONG!")

print("\n" + "=" * 70)
print("TESTING PENDULUM HEURISTIC")
print("=" * 70)

sequence = pendulum_heuristic(processing_times)
makespan = calculate_makespan(processing_times, sequence)

print(f"\nSequence: {sequence}")
print(f"Makespan: {makespan}")

print("\nExpected behavior:")
print("- Job with min machine-0 time should be selected first")
print("- Job totals should be calculated correctly")
print("- Sequence should follow pendulum pattern")

print("\nJob characteristics:")
for i, job in enumerate(processing_times):
    m0_time = job[0]
    total = sum(job)
    print(f"  Job {i}: machine0={m0_time}, total={total}")

# Verify: Job 3 has min machine0 time (3.0)
if processing_times[3][0] == 3.0:
    print("\n[OK] Job 3 has minimum machine-0 time (3.0) - should be selected first")
    if sequence[0] == 3:
        print("[OK] Job 3 is selected first in sequence - CORRECT!")
    else:
        print(f"[X] Job {sequence[0]} is first instead - may indicate an issue")

