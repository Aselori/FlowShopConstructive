"""
Constructive heuristics for Flow Shop Scheduling Problem.

This module implements various constructive heuristics, with the NEH 
(Nawaz-Enscore-Ham) algorithm as the primary method for generating 
initial solutions.
"""

from typing import List, Tuple
import copy
from makespan import calculate_makespan


def calculate_total_processing_time(processing_times: List[List[float]], job_idx: int) -> float:
    """
    Calculate the total processing time for a given job across all machines.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        job_idx (int): Index of the job
        
    Returns:
        float: Total processing time for the job
    """
    return sum(processing_times[job_idx])


def neh_heuristic(processing_times: List[List[float]]) -> List[int]:
    """
    Implement the NEH (Nawaz-Enscore-Ham) heuristic for flow shop scheduling.
    
    The NEH heuristic works in two phases:
    1. Sort jobs in decreasing order of total processing time
    2. Iteratively insert each job into the best position of the partial sequence
    
    Args:
        processing_times (List[List[float]]): Matrix where processing_times[i][j] 
                                            represents processing time of job i on machine j
        
    Returns:
        List[int]: Sequence of job indices that minimizes makespan
    """
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    
    # Phase 1: Sort jobs by decreasing total processing time
    job_totals = [(i, calculate_total_processing_time(processing_times, i)) 
                  for i in range(num_jobs)]
    job_totals.sort(key=lambda x: x[1], reverse=True)
    sorted_jobs = [job[0] for job in job_totals]
    
    # Phase 2: Build sequence by inserting jobs in best positions
    sequence = [sorted_jobs[0]]  # Start with the job with highest total time
    
    for job_idx in sorted_jobs[1:]:
        best_makespan = float('inf')
        best_position = 0
        
        # Try inserting the job at each possible position
        for pos in range(len(sequence) + 1):
            # Create temporary sequence with job inserted at position pos
            temp_sequence = sequence[:pos] + [job_idx] + sequence[pos:]
            
            # Calculate makespan for this sequence
            makespan = calculate_makespan(processing_times, temp_sequence)
            
            # Update best position if this is better
            if makespan < best_makespan:
                best_makespan = makespan
                best_position = pos
        
        # Insert job at best position
        sequence.insert(best_position, job_idx)
    
    return sequence


def shortest_processing_time_first(processing_times: List[List[float]]) -> List[int]:
    """
    Simple heuristic that sorts jobs by shortest total processing time first.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        List[int]: Sequence of job indices sorted by total processing time (ascending)
    """
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    job_totals = [(i, calculate_total_processing_time(processing_times, i)) 
                  for i in range(num_jobs)]
    job_totals.sort(key=lambda x: x[1])  # Sort ascending
    
    return [job[0] for job in job_totals]


def longest_processing_time_first(processing_times: List[List[float]]) -> List[int]:
    """
    Simple heuristic that sorts jobs by longest total processing time first.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        List[int]: Sequence of job indices sorted by total processing time (descending)
    """
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    job_totals = [(i, calculate_total_processing_time(processing_times, i)) 
                  for i in range(num_jobs)]
    job_totals.sort(key=lambda x: x[1], reverse=True)  # Sort descending
    
    return [job[0] for job in job_totals]


def palmer_heuristic(processing_times: List[List[float]]) -> List[int]:
    """
    Implement Palmer's heuristic based on slope index.
    
    The Palmer heuristic calculates a slope index for each job and sorts
    jobs in decreasing order of this index.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        List[int]: Sequence of job indices based on Palmer's slope index
    """
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0])
    
    # Calculate slope index for each job
    job_slopes = []
    for job_idx in range(num_jobs):
        slope_index = 0
        for machine in range(num_machines):
            # Weight decreases as machine index increases
            weight = -(2 * machine - num_machines + 1)
            slope_index += weight * processing_times[job_idx][machine]
        job_slopes.append((job_idx, slope_index))
    
    # Sort by slope index in decreasing order
    job_slopes.sort(key=lambda x: x[1], reverse=True)
    
    return [job[0] for job in job_slopes]


def cds_heuristic(processing_times: List[List[float]]) -> List[int]:
    """
    Implement Campbell, Dudek, and Smith (CDS) heuristic.
    
    The CDS heuristic generates multiple sequences by treating the problem
    as a series of 2-machine problems and selects the best one.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        List[int]: Best sequence found by CDS heuristic
    """
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0])
    
    if num_machines < 2:
        return list(range(num_jobs))
    
    best_sequence = None
    best_makespan = float('inf')
    
    # Generate sequences for each possible 2-machine grouping
    for k in range(1, num_machines):
        # Create artificial 2-machine problem
        machine1_times = []
        machine2_times = []
        
        for job_idx in range(num_jobs):
            # Machine 1: sum of first k machines
            m1_time = sum(processing_times[job_idx][:k])
            # Machine 2: sum of last k machines
            m2_time = sum(processing_times[job_idx][-k:])
            
            machine1_times.append(m1_time)
            machine2_times.append(m2_time)
        
        # Apply Johnson's rule for 2-machine problem
        sequence = johnsons_rule(machine1_times, machine2_times)
        
        # Evaluate this sequence on the original problem
        makespan = calculate_makespan(processing_times, sequence)
        
        if makespan < best_makespan:
            best_makespan = makespan
            best_sequence = sequence
    
    return best_sequence if best_sequence else list(range(num_jobs))


def johnsons_rule(machine1_times: List[float], machine2_times: List[float]) -> List[int]:
    """
    Apply Johnson's rule for 2-machine flow shop scheduling.
    
    Args:
        machine1_times (List[float]): Processing times on machine 1
        machine2_times (List[float]): Processing times on machine 2
        
    Returns:
        List[int]: Optimal sequence for 2-machine problem
    """
    num_jobs = len(machine1_times)
    jobs = list(range(num_jobs))
    
    # Separate jobs into two groups
    group1 = []  # Jobs where machine1_time <= machine2_time
    group2 = []  # Jobs where machine1_time > machine2_time
    
    for job_idx in jobs:
        if machine1_times[job_idx] <= machine2_times[job_idx]:
            group1.append((job_idx, machine1_times[job_idx]))
        else:
            group2.append((job_idx, machine2_times[job_idx]))
    
    # Sort group1 by machine1 time (ascending)
    group1.sort(key=lambda x: x[1])
    
    # Sort group2 by machine2 time (descending)
    group2.sort(key=lambda x: x[1], reverse=True)
    
    # Combine groups: group1 first, then group2
    sequence = [job[0] for job in group1] + [job[0] for job in group2]
    
    return sequence


def pendulum_heuristic(processing_times: List[List[float]]) -> List[int]:
    """
    Pendulum heuristic: place jobs with smaller total times at extremes,
    larger total times in the center (like a pendulum weight distribution).
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        List[int]: Sequence following pendulum pattern
    """
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    
    # Calculate total processing time for each job and sort ascending
    job_totals = [(i, calculate_total_processing_time(processing_times, i)) 
                  for i in range(num_jobs)]
    job_totals.sort(key=lambda x: x[1])  # Sort by total time (ascending)
    sorted_jobs = [job[0] for job in job_totals]
    
    # Build pendulum sequence: small jobs at ends, big jobs in center
    sequence = [0] * num_jobs
    left = 0
    right = num_jobs - 1
    
    # Place jobs alternating from extremes toward center
    for i, job_idx in enumerate(sorted_jobs):
        if i % 2 == 0:  # Even indices: place at left extreme, move inward
            sequence[left] = job_idx
            left += 1
        else:  # Odd indices: place at right extreme, move inward
            sequence[right] = job_idx
            right -= 1
    
    return sequence


def random_sequence(processing_times: List[List[float]]) -> List[int]:
    """
    Generate a random job sequence.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        List[int]: Random sequence of job indices
    """
    import random
    
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    sequence = list(range(num_jobs))
    random.shuffle(sequence)
    
    return sequence


def compare_heuristics(processing_times: List[List[float]]) -> List[Tuple[str, List[int], float]]:
    """
    Compare multiple heuristics and return results sorted by makespan.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        
    Returns:
        List[Tuple[str, List[int], float]]: List of (heuristic_name, sequence, makespan)
    """
    heuristics = {
        'NEH': neh_heuristic,
        'SPT': shortest_processing_time_first,
        'LPT': longest_processing_time_first,
        'Palmer': palmer_heuristic,
        'CDS': cds_heuristic,
        'Pendulum': pendulum_heuristic
    }
    
    results = []
    
    for name, heuristic_func in heuristics.items():
        try:
            sequence = heuristic_func(processing_times)
            makespan = calculate_makespan(processing_times, sequence)
            results.append((name, sequence, makespan))
        except Exception as e:
            print(f"Warning: Error in {name} heuristic: {e}")
            continue
    
    # Sort by makespan
    results.sort(key=lambda x: x[2])
    
    return results


def print_heuristic_comparison(processing_times: List[List[float]], 
                             job_names: List[str] = None) -> None:
    """
    Print comparison of different heuristics.
    
    Args:
        processing_times (List[List[float]]): Matrix of processing times
        job_names (List[str], optional): Names of jobs for display
    """
    if job_names is None:
        job_names = [f"Job_{i+1}" for i in range(len(processing_times))]
    
    results = compare_heuristics(processing_times)
    
    print(f"\n=== Heuristic Comparison ===")
    print(f"{'Heuristic':<10} {'Makespan':<10} {'Sequence'}")
    print("-" * 50)
    
    for name, sequence, makespan in results:
        sequence_str = ' -> '.join([job_names[i] for i in sequence])
        print(f"{name:<10} {makespan:<10.2f} {sequence_str}")
    
    print("=" * 50)
