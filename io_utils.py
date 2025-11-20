"""
Input/Output utilities for Flow Shop Scheduling Problem.

This module provides functions for reading and validating CSV files
with automatic header detection and data validation. Extended to parse
Taillard-style TXT/FSP instances as well.
"""

import csv
import os
import re
from typing import List, Tuple
import pandas as pd


def detect_csv_format(file_path: str) -> Tuple[bool, int, int]:
    """
    Detect if CSV has headers and determine dimensions.
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            sample = file.read(1024)
            if not sample:
                raise ValueError("CSV file is empty")

        try:
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
        except Exception:
            delimiter = ','

        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter)
            rows = []
            for i, row in enumerate(reader):
                if i < 2:
                    rows.append(row)
                else:
                    break

        if not rows:
            raise ValueError("CSV file is empty")

        first_row = rows[0]
        second_row = rows[1] if len(rows) > 1 else None

        has_headers = False
        try:
            [float(x.strip()) for x in first_row if x.strip()]
        except (ValueError, TypeError):
            has_headers = True

        if has_headers and second_row:
            num_machines = len([x for x in second_row if x.strip()])
        else:
            num_machines = len([x for x in first_row if x.strip()])

        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter)
            if has_headers:
                next(reader)
            num_jobs = sum(1 for row in reader if any(cell.strip() for cell in row))

        return has_headers, num_jobs, num_machines

    except Exception as e:
        raise ValueError(f"Error analyzing CSV format: {str(e)}")


def read_csv_data(file_path: str) -> Tuple[List[List[float]], List[str]]:
    """
    Read CSV file and return processing times matrix and job names.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    try:
        has_headers, num_jobs, _ = detect_csv_format(file_path)

        df = pd.read_csv(file_path, header=0 if has_headers else None)

        if has_headers:
            job_names = [f"Job_{i+1}" for i in range(num_jobs)]
        else:
            job_names = [f"Job_{i+1}" for i in range(len(df))]

        processing_times: List[List[float]] = []
        for _, row in df.iterrows():
            times: List[float] = []
            for value in row:
                if pd.notna(value) and str(value).strip():
                    try:
                        times.append(float(value))
                    except (ValueError, TypeError):
                        continue
            if times:
                processing_times.append(times)

        if not processing_times:
            raise ValueError("No valid processing time data found in CSV")

        machine_counts = [len(job) for job in processing_times]
        if len(set(machine_counts)) > 1:
            raise ValueError(f"Inconsistent number of machines per job: {set(machine_counts)}")

        for i, job_times in enumerate(processing_times):
            for j, time in enumerate(job_times):
                if time < 0:
                    raise ValueError(f"Negative processing time found at Job {i+1}, Machine {j+1}: {time}")

        return processing_times, job_names[:len(processing_times)]

    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing CSV file: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error reading CSV data: {str(e)}")


def validate_processing_times(processing_times: List[List[float]]) -> bool:
    """
    Validate the processing times matrix for logical consistency.
    """
    if not processing_times:
        raise ValueError("Processing times matrix is empty")

    if not all(isinstance(job, list) for job in processing_times):
        raise ValueError("Processing times must be a list of lists")

    num_machines = len(processing_times[0])
    for i, job_times in enumerate(processing_times):
        if len(job_times) != num_machines:
            raise ValueError(f"Job {i+1} has {len(job_times)} machines, expected {num_machines}")

    for i, job_times in enumerate(processing_times):
        for j, time in enumerate(job_times):
            if not isinstance(time, (int, float)) or time < 0:
                raise ValueError(f"Invalid processing time at Job {i+1}, Machine {j+1}: {time}")

    return True


def print_data_summary(processing_times: List[List[float]], job_names: List[str]) -> None:
    """
    Print a summary of the loaded data.
    """
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if processing_times else 0

    print(f"\n=== Data Summary ===")
    print(f"Number of jobs: {num_jobs}")
    print(f"Number of machines: {num_machines}")
    print(f"Job names: {', '.join(job_names)}")

    all_times = [time for job in processing_times for time in job]
    if all_times:
        print(f"Processing time range: {min(all_times):.2f} - {max(all_times):.2f}")
        print(f"Average processing time: {sum(all_times)/len(all_times):.2f}")
    print("=" * 20)


def read_taillard_txt(file_path: str) -> Tuple[List[List[float]], List[str]]:
    """
    Read a Flow Shop instance in Taillard-style TXT/FSP format.
    
    Note: Taillard format stores data as MACHINES-AS-ROWS (JOBS-AS-COLUMNS).
    Each row in the file represents one machine, with values for all jobs.
    This function reads the file format and TRANSPOSES it to the expected
    jobs-as-rows format (each row = one job, each column = one machine).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"TXT/FSP file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    n = m = None
    look_for_counts_next = False
    for line in lines:
        l = line.strip().lower()
        if 'number of jobs' in l and 'number of machines' in l:
            look_for_counts_next = True
            continue
        if look_for_counts_next:
            ints = re.findall(r"-?\d+", line)
            if len(ints) >= 2:
                n = int(ints[0])  # number of jobs
                m = int(ints[1])  # number of machines
                break
    if n is None or m is None:
        raise ValueError("Could not parse number of jobs and machines from TXT header.")

    # Taillard format: file has M rows (machines) with N values each (jobs)
    # Read all tokens first, then organize as machines-as-rows, then transpose to jobs-as-rows
    proc_tokens: List[float] = []
    collecting = False
    for line in lines:
        if not collecting:
            if 'processing times' in line.strip().lower():
                collecting = True
            continue
        if collecting:
            ints = re.findall(r"-?\d+", line)
            proc_tokens.extend(float(x) for x in ints)
            if len(proc_tokens) >= n * m:
                break

    if len(proc_tokens) < n * m:
        raise ValueError(f"Expected {n*m} processing times, found {len(proc_tokens)}.")

    # Organize tokens as machines-as-rows (m rows, n columns)
    # Each row in file represents one machine with times for all jobs
    machines_data: List[List[float]] = []
    idx = 0
    for machine_idx in range(m):
        row = proc_tokens[idx: idx + n]
        if len(row) != n:
            raise ValueError(f"Machine {machine_idx} row incomplete: expected {n} values, found {len(row)}")
        machines_data.append(row)
        idx += n

    # Transpose: convert from machines-as-rows to jobs-as-rows
    # machines_data[i][j] = time for job j on machine i
    # processing_times[i][j] = time for job i on machine j (expected format)
    processing_times: List[List[float]] = []
    for job_idx in range(n):
        job_times = [machines_data[machine_idx][job_idx] for machine_idx in range(m)]
        processing_times.append(job_times)

    job_names = [f"Job_{i+1}" for i in range(n)]
    return processing_times, job_names


def read_instance(file_path: str) -> Tuple[List[List[float]], List[str]]:
    """
    Dispatch reader based on extension:
    - .csv via read_csv_data
    - .txt/.fsp via read_taillard_txt
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        return read_csv_data(file_path)
    if ext in ('.txt', '.fsp'):
        return read_taillard_txt(file_path)
    try:
        return read_csv_data(file_path)
    except Exception:
        return read_taillard_txt(file_path)