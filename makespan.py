"""
Makespan calculation and analysis for Flow Shop Scheduling Problem.

This module provides functions to calculate and analyze the makespan (total completion time)
for a given sequence of jobs in a flow shop environment.
"""

from typing import List, Tuple, Dict, Any


def calculate_makespan(processing_times: List[List[float]], sequence: List[int]) -> float:
    """
    Calculate the makespan for a given job sequence in a flow shop.
    
    The makespan is the total time required to complete all jobs, which is
    determined by the completion time of the last job on the last machine.
    
    Args:
        processing_times: Matrix where processing_times[i][j] represents
                         the processing time of job i on machine j
        sequence: Sequence of job indices (0-based)
        
    Returns:
        The makespan (total completion time)
        
    Raises:
        ValueError: If sequence contains invalid job indices
    """
    if not processing_times or not sequence:
        return 0.0
        
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if num_jobs > 0 else 0
    
    # Validate sequence
    for job_idx in sequence:
        if job_idx < 0 or job_idx >= num_jobs:
            raise ValueError(f"Invalid job index {job_idx}. Must be between 0 and {num_jobs-1}")
    
    # Initialize completion time matrix
    completion_times = [[0.0 for _ in range(num_machines)] for _ in range(len(sequence))]
    
    # Calculate completion times for each job in the sequence
    for seq_pos, job_idx in enumerate(sequence):
        for machine in range(num_machines):
            proc_time = processing_times[job_idx][machine]
            
            if seq_pos == 0 and machine == 0:
                completion_times[seq_pos][machine] = proc_time
            elif seq_pos == 0:
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos][machine - 1] + proc_time
                )
            elif machine == 0:
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos - 1][machine] + proc_time
                )
            else:
                completion_times[seq_pos][machine] = (
                    max(completion_times[seq_pos - 1][machine],
                        completion_times[seq_pos][machine - 1]) + proc_time
                )
    
    # Makespan is the completion time of the last job on the last machine
    return completion_times[-1][-1] if completion_times else 0.0


def calculate_completion_times(processing_times: List[List[float]],
                               sequence: List[int]) -> List[List[float]]:
    """
    Compute and return the full completion time matrix for a given sequence.
    This mirrors the recurrence used in calculate_makespan.
    """
    if not processing_times or not sequence:
        return []
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if num_jobs > 0 else 0
    completion_times = [[0.0 for _ in range(num_machines)] for _ in range(len(sequence))]
    for seq_pos, job_idx in enumerate(sequence):
        for machine in range(num_machines):
            proc_time = processing_times[job_idx][machine]
            if seq_pos == 0 and machine == 0:
                completion_times[seq_pos][machine] = proc_time
            elif seq_pos == 0:
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos][machine - 1] + proc_time
                )
            elif machine == 0:
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos - 1][machine] + proc_time
                )
            else:
                completion_times[seq_pos][machine] = (
                    max(completion_times[seq_pos - 1][machine],
                        completion_times[seq_pos][machine - 1]) + proc_time
                )
    return completion_times


def calculate_makespan_delta(processing_times: List[List[float]],
                             sequence: List[int],
                             swap_pos: int,
                             completion_times: List[List[float]]) -> Tuple[float, List[List[float]]]:
    """
    Fast makespan recomputation for swapping adjacent jobs at swap_pos and swap_pos+1.
    Recomputes completion times from swap_pos onward using the standard recurrence.

    Returns the new makespan and the updated completion time matrix.
    """
    n = len(sequence)
    if n == 0:
        return 0.0, []
    if swap_pos < 0 or swap_pos >= n - 1:
        raise ValueError("swap_pos out of range")

    num_machines = len(processing_times[0]) if processing_times else 0

    # Apply the swap to a copy of the sequence
    new_seq = sequence.copy()
    new_seq[swap_pos], new_seq[swap_pos + 1] = new_seq[swap_pos + 1], new_seq[swap_pos]

    # Prepare a new completion matrix; copy rows before swap_pos as-is
    new_ct = (
        [row[:] for row in completion_times]
        if completion_times
        else [[0.0 for _ in range(num_machines)] for _ in range(n)]
    )

    start_row = max(0, swap_pos)
    for seq_pos in range(start_row, n):
        job_idx = new_seq[seq_pos]
        for machine in range(num_machines):
            proc_time = processing_times[job_idx][machine]
            if seq_pos == 0 and machine == 0:
                new_ct[seq_pos][machine] = proc_time
            elif seq_pos == 0:
                new_ct[seq_pos][machine] = new_ct[seq_pos][machine - 1] + proc_time
            elif machine == 0:
                new_ct[seq_pos][machine] = new_ct[seq_pos - 1][machine] + proc_time
            else:
                new_ct[seq_pos][machine] = max(new_ct[seq_pos - 1][machine], new_ct[seq_pos][machine - 1]) + proc_time

    return (new_ct[-1][-1] if new_ct else 0.0), new_ct


def calculate_idle_times(processing_times: List[List[float]], 
                        sequence: List[int]) -> Tuple[List[float], float]:
    """
    Calculate machine idle times for a given sequence.
    
    Args:
        processing_times: Matrix of processing times
        sequence: Sequence of job indices
        
    Returns:
        Tuple of (idle_times_per_machine, total_idle_time)
    """
    if not processing_times or not sequence:
        return [], 0.0
        
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if num_jobs > 0 else 0
    
    # Initialize completion time matrix
    completion_times = [[0.0 for _ in range(num_machines)] for _ in range(len(sequence))]
    
    # Calculate completion times
    for seq_pos, job_idx in enumerate(sequence):
        for machine in range(num_machines):
            proc_time = processing_times[job_idx][machine]
            
            if seq_pos == 0 and machine == 0:
                completion_times[seq_pos][machine] = proc_time
            elif seq_pos == 0:
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos][machine - 1] + proc_time
                )
            elif machine == 0:
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos - 1][machine] + proc_time
                )
            else:
                completion_times[seq_pos][machine] = (
                    max(completion_times[seq_pos - 1][machine],
                        completion_times[seq_pos][machine - 1]) + proc_time
                )
    
    # Calculate idle times
    idle_times = [0.0] * num_machines
    total_idle = 0.0
    
    for machine in range(num_machines):
        for job_pos in range(1, len(sequence)):
            # Idle time is the time the machine waits for the previous job to complete
            idle = max(0, completion_times[job_pos - 1][machine] - 
                       (completion_times[job_pos][machine - 1] if machine > 0 else 0))
            idle_times[machine] += idle
            total_idle += idle
    
    return idle_times, total_idle


def print_sequence_analysis(processing_times: List[List[float]], 
                          sequence: List[int], 
                          job_names: List[str] = None) -> None:
    """
    Print analysis of a job sequence.
    
    Args:
        processing_times: Matrix of processing times
        sequence: Sequence of job indices
        job_names: Optional list of job names for display
    """
    if not processing_times or not sequence:
        print("No sequence to analyze")
        return
        
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if num_jobs > 0 else 0
    
    if job_names is None:
        job_names = [f"Job_{i+1}" for i in range(num_jobs)]
    
    # Calculate metrics
    makespan = calculate_makespan(processing_times, sequence)
    
    # Print analysis
    print(f"\nSequence: {' -> '.join([job_names[i] for i in sequence])}")
    print(f"Makespan: {makespan:.2f}")
