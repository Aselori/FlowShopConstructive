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
    Print detailed analysis of a job sequence.
    
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
    idle_times, total_idle = calculate_idle_times(processing_times, sequence)
    
    # Calculate machine utilization
    total_processing = sum(sum(job) for job in processing_times)
    utilization = (total_processing / (makespan * num_machines)) * 100 if makespan > 0 else 0
    
    # Print analysis
    print("\nDETAILED ANALYSIS")
    print("=" * 60)
    print(f"Sequence: {' -> '.join([job_names[i] for i in sequence])}")
    print(f"\nMakespan: {makespan:.2f}")
    
    # Print machine idle times
    print("\nMachine Idle Times:")
    for machine in range(num_machines):
        print(f"  Machine {machine + 1}: {idle_times[machine]:.2f}")
    
    print(f"\nTotal Idle Time: {total_idle:.2f}")
    print(f"Machine Utilization: {utilization:.1f}%")
    print("=" * 60)
