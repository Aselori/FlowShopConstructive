"""
Makespan calculation utilities for Flow Shop Scheduling Problem.

This module provides functions to calculate the makespan (total completion time)
for a given sequence of jobs in a flow shop environment.
"""

from typing import List, Tuple
import copy


def calculate_makespan(processing_times: List[List[float]], sequence: List[int]) -> float:
    """
    Calculate the makespan for a given job sequence in a flow shop.
    
    The makespan is the total time required to complete all jobs, which is
    determined by the completion time of the last job on the last machine.
    
    Args:
        processing_times (List[List[float]]): Matrix where processing_times[i][j] 
                                            represents the processing time of job i on machine j
        sequence (List[int]): Sequence of job indices (0-based)
        
    Returns:
        float: The makespan (total completion time)
        
    Raises:
        ValueError: If sequence contains invalid job indices
    """
    if not processing_times or not sequence:
        return 0.0
        
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0])
    
    # Validate sequence
    for job_idx in sequence:
        if job_idx < 0 or job_idx >= num_jobs:
            raise ValueError(f"Invalid job index {job_idx}. Must be between 0 and {num_jobs-1}")
    
    # Initialize completion time matrix
    # completion_times[i][j] = completion time of job i on machine j
    completion_times = [[0.0 for _ in range(num_machines)] for _ in range(len(sequence))]
    
    # Calculate completion times for each job in the sequence
    for seq_pos, job_idx in enumerate(sequence):
        for machine in range(num_machines):
            # Processing time for current job on current machine
            proc_time = processing_times[job_idx][machine]
            
            if seq_pos == 0 and machine == 0:
                # First job on first machine
                completion_times[seq_pos][machine] = proc_time
            elif seq_pos == 0:
                # First job on subsequent machines
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos][machine - 1] + proc_time
                )
            elif machine == 0:
                # Subsequent jobs on first machine
                completion_times[seq_pos][machine] = (
                    completion_times[seq_pos - 1][machine] + proc_time
                )
            else:
                # Subsequent jobs on subsequent machines
                completion_times[seq_pos][machine] = (
                    max(completion_times[seq_pos - 1][machine],
                        completion_times[seq_pos][machine - 1]) + proc_time
                )
    
    # Makespan is the completion time of the last job on the last machine
    return completion_times[-1][-1]


def calculate_completion_matrix(processing_times: List[List[float]], 
                              sequence: List[int]) -> List[List[float]]:
    """
    Calculate the full completion time matrix for a given sequence.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        sequence (List[int]): Sequence of job indices
        
    Returns:
        List[List[float]]: Completion time matrix where element [i][j] represents
                          the completion time of the i-th job in sequence on machine j
    """
    if not processing_times or not sequence:
        return []
        
    num_machines = len(processing_times[0])
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


def calculate_idle_times(processing_times: List[List[float]], 
                        sequence: List[int]) -> Tuple[List[float], float]:
    """
    Calculate machine idle times for a given sequence.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        sequence (List[int]): Sequence of job indices
        
    Returns:
        Tuple[List[float], float]: (idle_times_per_machine, total_idle_time)
    """
    if not processing_times or not sequence:
        return [], 0.0
        
    completion_matrix = calculate_completion_matrix(processing_times, sequence)
    num_machines = len(processing_times[0])
    makespan = completion_matrix[-1][-1]
    
    # Calculate total processing time per machine
    machine_processing_times = [0.0] * num_machines
    for job_idx in sequence:
        for machine in range(num_machines):
            machine_processing_times[machine] += processing_times[job_idx][machine]
    
    # Calculate idle times
    idle_times = []
    total_idle = 0.0
    
    for machine in range(num_machines):
        idle_time = makespan - machine_processing_times[machine]
        idle_times.append(idle_time)
        total_idle += idle_time
    
    return idle_times, total_idle


def evaluate_sequence_quality(processing_times: List[List[float]], 
                            sequence: List[int]) -> dict:
    """
    Evaluate the quality of a job sequence using multiple metrics.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        sequence (List[int]): Sequence of job indices
        
    Returns:
        dict: Dictionary containing various quality metrics
    """
    if not processing_times or not sequence:
        return {}
    
    makespan = calculate_makespan(processing_times, sequence)
    idle_times, total_idle = calculate_idle_times(processing_times, sequence)
    
    # Calculate utilization
    total_processing_time = sum(sum(job) for job in processing_times)
    num_machines = len(processing_times[0])
    utilization = total_processing_time / (makespan * num_machines) if makespan > 0 else 0
    
    return {
        'makespan': makespan,
        'total_idle_time': total_idle,
        'machine_idle_times': idle_times,
        'utilization': utilization,
        'efficiency': 1 - (total_idle / (makespan * num_machines)) if makespan > 0 else 0
    }


def compare_sequences(processing_times: List[List[float]], 
                     sequences: List[List[int]]) -> List[Tuple[List[int], float]]:
    """
    Compare multiple sequences and return them sorted by makespan.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        sequences (List[List[int]]): List of job sequences to compare
        
    Returns:
        List[Tuple[List[int], float]]: List of (sequence, makespan) tuples sorted by makespan
    """
    results = []
    
    for sequence in sequences:
        try:
            makespan = calculate_makespan(processing_times, sequence)
            results.append((sequence.copy(), makespan))
        except ValueError as e:
            print(f"Warning: Invalid sequence {sequence}: {e}")
            continue
    
    # Sort by makespan (ascending)
    results.sort(key=lambda x: x[1])
    return results


def print_sequence_analysis(processing_times: List[List[float]], 
                          sequence: List[int], 
                          job_names: List[str] = None) -> None:
    """
    Print detailed analysis of a job sequence.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        sequence (List[int]): Sequence of job indices
        job_names (List[str], optional): Names of jobs for display
    """
    if job_names is None:
        job_names = [f"Job_{i+1}" for i in range(len(processing_times))]
    
    metrics = evaluate_sequence_quality(processing_times, sequence)
    
    print(f"\n=== Sequence Analysis ===")
    print(f"Job sequence: {' -> '.join([job_names[i] for i in sequence])}")
    print(f"Makespan: {metrics['makespan']:.2f}")
    print(f"Total idle time: {metrics['total_idle_time']:.2f}")
    print(f"Machine utilization: {metrics['utilization']:.2%}")
    print(f"Overall efficiency: {metrics['efficiency']:.2%}")
    
    print(f"\nMachine idle times:")
    for i, idle_time in enumerate(metrics['machine_idle_times']):
        print(f"  Machine {i+1}: {idle_time:.2f}")
    print("=" * 25)
