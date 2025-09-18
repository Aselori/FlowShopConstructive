"""
Input/Output utilities for Flow Shop Scheduling Problem.

This module provides functions for reading and validating CSV files
with automatic header detection and data validation.
"""

import csv
import os
from typing import List, Tuple, Union
import pandas as pd


def detect_csv_format(file_path: str) -> Tuple[bool, int, int]:
    """
    Detect if CSV has headers and determine dimensions.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        Tuple[bool, int, int]: (has_headers, num_jobs, num_machines)
    """
    try:
        # Read first few rows to analyze structure
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            sample = file.read(1024)
            
        # Use csv.Sniffer to detect format
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
        
        # Read the first two rows
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
            
        # Check if first row contains non-numeric data (likely headers)
        has_headers = False
        try:
            # Try to convert first row to float
            [float(x.strip()) for x in first_row if x.strip()]
        except (ValueError, TypeError):
            has_headers = True
            
        # Count dimensions
        if has_headers and second_row:
            num_machines = len([x for x in second_row if x.strip()])
        else:
            num_machines = len([x for x in first_row if x.strip()])
            
        # Count total rows to determine number of jobs
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=delimiter)
            if has_headers:
                next(reader)  # Skip header
            num_jobs = sum(1 for row in reader if any(cell.strip() for cell in row))
            
        return has_headers, num_jobs, num_machines
        
    except Exception as e:
        raise ValueError(f"Error analyzing CSV format: {str(e)}")


def read_csv_data(file_path: str) -> Tuple[List[List[float]], List[str]]:
    """
    Read CSV file and return processing times matrix and job names.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        Tuple[List[List[float]], List[str]]: (processing_times, job_names)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If data format is invalid
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
        
    try:
        has_headers, num_jobs, num_machines = detect_csv_format(file_path)
        
        # Read the CSV file
        df = pd.read_csv(file_path, header=0 if has_headers else None)
        
        # Generate job names
        if has_headers:
            job_names = [f"Job_{i+1}" for i in range(num_jobs)]
        else:
            job_names = [f"Job_{i+1}" for i in range(len(df))]
            
        # Extract processing times
        processing_times = []
        for _, row in df.iterrows():
            # Convert row to list of floats, filtering out empty values
            times = []
            for value in row:
                if pd.notna(value) and str(value).strip():
                    try:
                        times.append(float(value))
                    except (ValueError, TypeError):
                        continue
            if times:  # Only add non-empty rows
                processing_times.append(times)
                
        # Validate data consistency
        if not processing_times:
            raise ValueError("No valid processing time data found in CSV")
            
        # Check that all jobs have the same number of machines
        machine_counts = [len(job) for job in processing_times]
        if len(set(machine_counts)) > 1:
            raise ValueError(f"Inconsistent number of machines per job: {set(machine_counts)}")
            
        # Ensure non-negative processing times
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
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        bool: True if valid, raises ValueError if invalid
        
    Raises:
        ValueError: If data is logically inconsistent
    """
    if not processing_times:
        raise ValueError("Processing times matrix is empty")
        
    if not all(isinstance(job, list) for job in processing_times):
        raise ValueError("Processing times must be a list of lists")
        
    # Check dimensions consistency
    num_machines = len(processing_times[0])
    for i, job_times in enumerate(processing_times):
        if len(job_times) != num_machines:
            raise ValueError(f"Job {i+1} has {len(job_times)} machines, expected {num_machines}")
            
    # Check for non-negative values
    for i, job_times in enumerate(processing_times):
        for j, time in enumerate(job_times):
            if not isinstance(time, (int, float)) or time < 0:
                raise ValueError(f"Invalid processing time at Job {i+1}, Machine {j+1}: {time}")
                
    return True


def print_data_summary(processing_times: List[List[float]], job_names: List[str]) -> None:
    """
    Print a summary of the loaded data.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        job_names (List[str]): List of job names
    """
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if processing_times else 0
    
    print(f"\n=== Data Summary ===")
    print(f"Number of jobs: {num_jobs}")
    print(f"Number of machines: {num_machines}")
    print(f"Job names: {', '.join(job_names)}")
    
    # Calculate some basic statistics
    all_times = [time for job in processing_times for time in job]
    if all_times:
        print(f"Processing time range: {min(all_times):.2f} - {max(all_times):.2f}")
        print(f"Average processing time: {sum(all_times)/len(all_times):.2f}")
    print("=" * 20)
