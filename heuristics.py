"""
Pendulum Heuristic for Flow Shop Scheduling Problem.

This module implements the Pendulum heuristic for the Flow Shop Scheduling Problem.
The Pendulum heuristic places jobs with smaller total processing times at the
extremes and larger total times in the center, similar to a pendulum's weight distribution.
"""

from typing import List, Optional, Union
from makespan import calculate_makespan
import random
import numpy as np


def calculate_total_processing_time(processing_times: List[List[float]], job_idx: int) -> float:
    """
    Calculate the total processing time for a given job across all machines.
    
    Args:
        processing_times: Matrix of processing times
        job_idx: Index of the job
        
    Returns:
        Total processing time for the job
    """
    return sum(processing_times[job_idx])


def pendulum_heuristic(processing_times: List[List[float]]) -> List[int]:
    """
    Pendulum heuristic: place jobs with smaller total times at extremes,
    larger total times in the center (like a pendulum weight distribution).
    
    The heuristic works as follows:
    1. Choose the job with the minimum processing time on the first machine as the first job
    2. Sort remaining jobs by total processing time (ascending)
    3. Place jobs alternately at the end and beginning of the sequence
    
    Args:
        processing_times: Matrix where processing_times[i][j] represents 
                         processing time of job i on machine j
        
    Returns:
        Sequence of job indices following the pendulum pattern
    """
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if num_jobs > 0 else 0

    # Precompute totals and machine-1 times for tie-breaking
    totals = [calculate_total_processing_time(processing_times, i) for i in range(num_jobs)]
    m1_times = [processing_times[i][0] if num_machines > 0 else 0 for i in range(num_jobs)]

    # Step A: choose first job (min machine-1 time; tie-break by total, then job index)
    first_job = min(range(num_jobs), key=lambda j: (m1_times[j], totals[j], j))

    # Step B: place the first job at position 0
    sequence = [-1] * num_jobs
    sequence[0] = first_job

    # Step C: sort remaining jobs by (total asc, machine1 asc, job index asc)
    remaining = [j for j in range(num_jobs) if j != first_job]
    remaining.sort(key=lambda j: (totals[j], m1_times[j], j))

    # Step D: pendulum fill for the rest, starting from right then left and alternating
    left = 1
    right = num_jobs - 1
    for k, job_idx in enumerate(remaining):
        if k % 2 == 0:
            # First remaining goes to the far right, then alternate
            sequence[right] = job_idx
            right -= 1
        else:
            sequence[left] = job_idx
            left += 1

    return sequence


def randomized_constructive_heuristic(processing_times: List[List[float]], 
                                    method: str = 'alpha', 
                                    param: Union[float, int] = None,
                                    seed: Optional[int] = None) -> List[int]:
    """
    Randomized constructive heuristic with either alpha or k-best randomization.
    
    Args:
        processing_times: Matrix where processing_times[i][j] represents 
                         processing time of job i on machine j
        method: 'alpha' for alpha-randomization OR 'kbest' for k-best selection
        param: alpha value (0-1) for 'alpha' OR k value (integer) for 'kbest'
        seed: Random seed for reproducibility
        
    Returns:
        List of job indices representing the constructed sequence
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    if not processing_times:
        return []
    
    num_jobs = len(processing_times)
    unscheduled = set(range(num_jobs))
    sequence = []
    
    # Calculate job characteristics
    job_totals = [calculate_total_processing_time(processing_times, j) for j in range(num_jobs)]
    first_machine = [processing_times[j][0] for j in range(num_jobs)]
    
    # Start with the job that has minimum processing time on first machine
    if unscheduled:
        first_job = min(unscheduled, key=lambda j: first_machine[j])
        sequence.append(first_job)
        unscheduled.remove(first_job)
    
    while unscheduled:
        candidates = list(unscheduled)
        
        if method == 'alpha':
            # Alpha-randomized greedy
            if param is None or not (0 < param < 1):
                raise ValueError("alpha param must be between 0 and 1")
                
            scores = [job_totals[j] for j in candidates]
            
            # Normalize scores (lower is better)
            min_score, max_score = min(scores), max(scores)
            if max_score > min_score:
                normalized = [(s - min_score) / (max_score - min_score) for s in scores]
            else:
                normalized = [0.5] * len(scores)
            
            # Calculate probabilities using exponential bias
            probs = [np.exp(-param * s) for s in normalized]
            probs = [p/sum(probs) for p in probs]
            
            # Select candidate
            selected = np.random.choice(candidates, p=probs)
            
        elif method == 'kbest':
            # k-best greedy
            if param is None or param < 1:
                raise ValueError("k param must be >= 1")
                
            k = min(int(param), len(unscheduled))
            
            # Get top k candidates by total processing time
            candidates_sorted = sorted(candidates, key=lambda j: job_totals[j])
            selected = random.choice(candidates_sorted[:k])
            
        else:
            raise ValueError("method must be either 'alpha' or 'kbest'")
        
        sequence.append(selected)
        unscheduled.remove(selected)
        
        # Pendulum effect: alternate between front and back
        if len(sequence) > 1:
            if len(sequence) % 2 == 0:
                sequence = [sequence[-1]] + sequence[:-1]
    
    return sequence
