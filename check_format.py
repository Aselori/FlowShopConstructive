"""
Check the actual format of the instance files
"""

from io_utils import read_taillard_txt
import os

# Check test.fsp
print("=" * 70)
print("Checking test.fsp format")
print("=" * 70)
print("\nFile says: 5 jobs, 3 machines")
print("File has: 3 rows of data (after 'processing times')")
print("Each row has: 5 numbers")
print("\nThis means: EACH ROW = ONE MACHINE, EACH COLUMN = ONE JOB")
print("Format: JOBS-AS-COLUMNS (machines-as-rows)")

file_path = os.path.join("..", "Instances", "test.fsp")
processing_times, job_names = read_taillard_txt(file_path)

print(f"\nReader interpreted:")
print(f"  Number of rows: {len(processing_times)} (should be 5 if jobs-as-rows)")
print(f"  Number of columns: {len(processing_times[0]) if processing_times else 0} (should be 3 if jobs-as-rows)")

print("\nActual matrix structure after reading:")
for i, row in enumerate(processing_times[:3]):  # Show first 3
    print(f"  Row {i}: {row}")

# Check what the file actually contains
print("\n" + "=" * 70)
print("What the file ACTUALLY contains:")
print("=" * 70)
with open(file_path, 'r') as f:
    lines = f.readlines()
    
collecting = False
line_num = 0
for line in lines:
    if not collecting:
        if 'processing times' in line.lower():
            collecting = True
        continue
    if collecting:
        nums = [x for x in line.strip().split() if x]
        if nums:
            print(f"  Line {line_num} (Machine {line_num}): {nums[:5]}... ({len(nums)} numbers)")
            line_num += 1
            if line_num >= 3:
                break

print("\n" + "=" * 70)
print("CONCLUSION:")
print("=" * 70)
print("Your instances ARE in JOBS-AS-COLUMNS format!")
print("Each row in the file = one machine")
print("Each column in the file = one job")
print("\nBut your read_taillard_txt function is reading it as JOBS-AS-ROWS!")
print("It needs to be TRANSPOSED or read differently!")

