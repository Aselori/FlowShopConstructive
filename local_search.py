"""
Local Search module for Flow Shop Scheduling Problem.

This module implements a bottleneck-aware adjacent swap local search
to improve solutions found by the constructive heuristic.
"""

from typing import List, Tuple, Optional
import time
from heuristics import calculate_total_processing_time

def identify_bottleneck_machine(processing_times: List[List[float]]) -> int:
    """
    Identify the bottleneck machine (machine with highest total processing time).
    
    Args:
        processing_times: Matrix where processing_times[i][j] is the 
                         processing time of job i on machine j
    
    Returns:
        Index of the bottleneck machine (0-based)
    """
    if not processing_times or not processing_times[0]:
        return 0
    machine_totals = [sum(machine_times) for machine_times in zip(*processing_times)]
    return machine_totals.index(max(machine_totals))

def score_adjacent_pair(sequence: List[int], pos: int, 
                       processing_times: List[List[float]], 
                       bottleneck_machine: int,
                       job_totals: List[float],
                       n: int,
                       bn_proc: List[float],
                       bn_threshold: float) -> float:
    """
    Score an adjacent pair of jobs based on bottleneck machine difference and total load.
    
    Args:
        sequence: Current job sequence
        pos: Position of the first job in the pair
        processing_times: Processing times matrix
        bottleneck_machine: Index of the bottleneck machine
        
    Returns:
        Score for this pair (higher is better for swapping)
    """
    job1, job2 = sequence[pos], sequence[pos + 1]
    # Difference on bottleneck machine
    bottleneck_diff = abs(processing_times[job1][bottleneck_machine] - 
                         processing_times[job2][bottleneck_machine])
    # Difference in total processing time (reuse precomputed totals)
    total_diff = abs(job_totals[job1] - job_totals[job2])

    # Pendulum-aligned bias: heavier jobs closer to center, lighter jobs to ends
    center = (n - 1) / 2.0
    dist1_c_before = abs(pos - center)
    dist2_c_before = abs((pos + 1) - center)
    # Identify heavier/lighter on total load
    if job_totals[job1] >= job_totals[job2]:
        heavy_pos_before, light_pos_before = pos, pos + 1
        heavy_job, light_job = job1, job2
    else:
        heavy_pos_before, light_pos_before = pos + 1, pos
        heavy_job, light_job = job2, job1
    # After swap, positions invert for the two jobs in this pair
    heavy_pos_after = pos if heavy_pos_before == pos + 1 else pos + 1
    light_pos_after = pos if light_pos_before == pos + 1 else pos + 1
    # Distances to center and to ends
    dist_heavy_c_before = abs(heavy_pos_before - center)
    dist_heavy_c_after = abs(heavy_pos_after - center)
    end_dist_light_before = min(light_pos_before, (n - 1) - light_pos_before)
    end_dist_light_after = min(light_pos_after, (n - 1) - light_pos_after)
    # Gains if swap moves heavy toward center and light toward ends
    centrality_gain = max(0.0, dist_heavy_c_before - dist_heavy_c_after)
    end_bias_gain = max(0.0, end_dist_light_after - end_dist_light_before)
    # Modest weights so structural bias guides but doesn't dominate
    alpha, beta = 9.0, 4.0
    pendulum_bias = alpha * centrality_gain + beta * end_bias_gain

    # Neighborhood smoothness: prefer reducing local total-load roughness
    # Consider indices [pos-1, pos, pos+1, pos+2] where defined
    idxs_before = []
    for k in (pos-1, pos, pos+1):
        if 0 <= k < n-1:
            a, b = sequence[k], sequence[k+1]
            idxs_before.append(abs(job_totals[a] - job_totals[b]))
    rough_before = sum(idxs_before)

    # After swap, compute roughness on the same k windows impacted
    tmp_seq = sequence
    a1, a2 = tmp_seq[pos], tmp_seq[pos+1]
    swapped_pair = (a2, a1)
    # Helper to get element at position k after swap without copying entire seq
    def after(k: int) -> int:
        if k == pos:
            return swapped_pair[0]
        if k == pos+1:
            return swapped_pair[1]
        return tmp_seq[k]
    idxs_after = []
    for k in (pos-1, pos, pos+1):
        if 0 <= k < n-1:
            x, y = after(k), after(k+1)
            idxs_after.append(abs(job_totals[x] - job_totals[y]))
    rough_after = sum(idxs_after)
    smooth_gain = max(0.0, rough_before - rough_after)
    gamma = 1.5

    # Bottleneck criticality bonus: prioritize pairs involving jobs heavy on the bottleneck
    bonus = 0.0
    if bn_proc[job1] >= bn_threshold or bn_proc[job2] >= bn_threshold:
        bonus = 5.0

    return bottleneck_diff + total_diff + pendulum_bias + gamma * smooth_gain + bonus

def swap_adjacent(sequence: List[int], pos: int) -> List[int]:
    """
    Create a new sequence with jobs at pos and pos+1 swapped.
    
    Args:
        sequence: Current job sequence
        pos: Position to perform the swap (0-based)
        
    Returns:
        New sequence with the swap applied
    """
    if pos < 0 or pos >= len(sequence) - 1:
        raise ValueError(f"Invalid swap position {pos} for sequence of length {len(sequence)}")
    new_sequence = sequence.copy()
    new_sequence[pos], new_sequence[pos + 1] = new_sequence[pos + 1], new_sequence[pos]
    return new_sequence

def evaluate_insertion_delta(processing_times: List[List[float]],
                             sequence: List[int],
                             from_pos: int,
                             to_pos: int,
                             completion_times: List[List[float]]) -> Tuple[List[int], float, List[List[float]]]:
    """
    Move job at from_pos to to_pos via a sequence of adjacent swaps, using
    calculate_makespan_delta at each micro-step to keep evaluation fast.

    Returns (new_sequence, new_makespan, new_completion_times).
    """
    n = len(sequence)
    if from_pos == to_pos or n <= 1:
        return sequence.copy(), (completion_times[-1][-1] if completion_times else calculate_makespan(processing_times, sequence)), [row[:] for row in completion_times]

    seq = sequence.copy()
    ct = [row[:] for row in completion_times]
    current_mk = ct[-1][-1] if ct else calculate_makespan(processing_times, seq)

    # Determine direction and perform adjacent micro-swaps
    step = 1 if to_pos > from_pos else -1
    pos = from_pos
    while pos != to_pos:
        swap_pos = pos if step == 1 else pos - 1
        new_mk, new_ct = calculate_makespan_delta(processing_times, seq, swap_pos, ct)
        # Apply the swap to the sequence deterministically
        seq[swap_pos], seq[swap_pos + 1] = seq[swap_pos + 1], seq[swap_pos]
        ct = new_ct
        current_mk = new_mk
        pos += step
    return seq, current_mk, ct

def local_search_main(initial_sequence: List[int], 
                     processing_times: List[List[float]],
                     max_iterations: int = 400,
                     top_k: Optional[int] = None,
                     verbose: bool = False,
                     search_mode: str = "best",
                     recompute_bottleneck: bool = True,
                     time_budget_seconds: Optional[float] = 30.0) -> Tuple[List[int], float, int, float]:
    """
    Perform local search using bottleneck-aware adjacent swaps (deterministic first-improvement).
    
    Args:
        initial_sequence: Initial sequence from constructive heuristic
        processing_times: Processing times matrix
        max_iterations: Maximum number of iterations (increased to 50)
        top_k: Number of top pairs to consider in each iteration
        verbose: Whether to print progress
        
    Returns:
        Tuple of (best_sequence, best_makespan, iterations_used, search_time)
    """
    # Input validation
    if not initial_sequence or not processing_times:
        return initial_sequence, 0.0, 0, 0.0
    
    num_jobs = len(processing_times)
    num_machines = len(processing_times[0]) if num_jobs > 0 else 0
    
    if len(initial_sequence) != num_jobs:
        raise ValueError("Sequence length must match number of jobs")
    
    if num_jobs <= 1:
        makespan = calculate_makespan(processing_times, initial_sequence)
        return initial_sequence, makespan, 0, 0.0
    
    # Initialize
    current_sequence = initial_sequence.copy()
    current_makespan = calculate_makespan(processing_times, current_sequence)
    best_sequence = current_sequence.copy()
    best_makespan = current_makespan
    # Cache completion times to enable fast delta evaluations
    completion_times = calculate_completion_times(processing_times, current_sequence)
    bottleneck_machine = identify_bottleneck_machine(processing_times)

    # Precompute total processing time per job using existing helper
    job_totals = [calculate_total_processing_time(processing_times, j) for j in range(num_jobs)]

    # Precompute bottleneck processing times and criticality threshold (80th percentile)
    bn_proc = [processing_times[j][bottleneck_machine] for j in range(num_jobs)]
    sorted_bn = sorted(bn_proc)
    q_index = max(0, min(len(sorted_bn) - 1, int(0.8 * (len(sorted_bn) - 1))))
    bn_threshold = sorted_bn[q_index]

    # By default, consider all adjacent pairs for stronger improvement (still O(n))
    if top_k is None:
        top_k = len(current_sequence) - 1
    else:
        top_k = min(top_k, len(current_sequence) - 1)

    iterations_used = 0
    start_time = time.perf_counter()
    no_improvement_streak = 0
    
    # Main local search loop (deterministic best-improvement with intensification)
    while iterations_used < max_iterations:
        if time_budget_seconds is not None and (time.perf_counter() - start_time) >= time_budget_seconds:
            if verbose:
                print("Time budget reached; stopping.")
            break
        improvement_found = False
        iterations_used += 1

        if verbose:
            print(f"\n--- Iteration {iterations_used} ---")
            print(f"Current makespan: {current_makespan}")

        # Score all adjacent pairs (bottleneck + total load + pendulum bias)
        scores = []
        for pos in range(len(current_sequence) - 1):
            score = score_adjacent_pair(current_sequence, pos, processing_times, bottleneck_machine, job_totals, len(current_sequence), bn_proc, bn_threshold)
            scores.append((pos, score))

        # Sort by score descending; tie-break by position to keep determinism
        scores.sort(key=lambda x: (-x[1], x[0]))
        top_pairs = [pos for pos, _ in scores[:top_k]]

        # Intensification: keep applying best-improvement swaps within this iteration
        while True:
            # Re-evaluate time budget
            if time_budget_seconds is not None and (time.perf_counter() - start_time) >= time_budget_seconds:
                break
            best_pos = None
            best_new_makespan = current_makespan
            best_new_ct = None
            if search_mode == "first":
                for pos in top_pairs:
                    new_makespan, new_ct = calculate_makespan_delta(
                        processing_times, current_sequence, pos, completion_times
                    )
                    if new_makespan < current_makespan:
                        best_pos = pos
                        best_new_makespan = new_makespan
                        best_new_ct = new_ct
                        break
            else:
                for pos in top_pairs:
                    new_makespan, new_ct = calculate_makespan_delta(
                        processing_times, current_sequence, pos, completion_times
                    )
                    if new_makespan < best_new_makespan:
                        best_new_makespan = new_makespan
                        best_pos = pos
                        best_new_ct = new_ct
            if best_pos is not None and best_new_makespan < current_makespan:
                new_sequence = swap_adjacent(current_sequence, best_pos)
                if verbose:
                    print(f"Improved: {current_makespan} -> {best_new_makespan} by swapping {best_pos} and {best_pos+1}")
                current_sequence = new_sequence
                current_makespan = best_new_makespan
                if current_makespan < best_makespan:
                    best_makespan = current_makespan
                    best_sequence = current_sequence.copy()
                completion_times = best_new_ct if best_new_ct is not None else calculate_completion_times(processing_times, current_sequence)
                improvement_found = True
                if recompute_bottleneck:
                    bottleneck_machine = identify_bottleneck_machine(processing_times)
                # Optionally recompute bottleneck stats when it changes
                if recompute_bottleneck:
                    bn_proc = [processing_times[j][bottleneck_machine] for j in range(num_jobs)]
                    sorted_bn = sorted(bn_proc)
                    q_index = max(0, min(len(sorted_bn) - 1, int(0.8 * (len(sorted_bn) - 1))))
                    bn_threshold = sorted_bn[q_index]
                # Rescore neighbors since sequence changed
                scores = []
                for pos in range(len(current_sequence) - 1):
                    score = score_adjacent_pair(current_sequence, pos, processing_times, bottleneck_machine, job_totals, len(current_sequence), bn_proc, bn_threshold)
                    scores.append((pos, score))
                scores.sort(key=lambda x: (-x[1], x[0]))
                top_pairs = [pos for pos, _ in scores[:top_k]]
                continue
            break

        if not improvement_found:
            no_improvement_streak += 1
            # Last-resort guided perturbation: apply the single best-scored swap even if non-improving
            if no_improvement_streak >= 2:
                best_pos = scores[0][0] if scores else None
                if best_pos is not None:
                    # Apply guided perturbation with delta update
                    pert_mk, pert_ct = calculate_makespan_delta(
                        processing_times, current_sequence, best_pos, completion_times
                    )
                    # Guardrail: do not allow large degradation (>0.2%)
                    max_worsen = 0.002 * current_makespan
                    if pert_mk <= current_makespan + max_worsen:
                        pert_seq = swap_adjacent(current_sequence, best_pos)
                        if verbose:
                            print(f"Guided perturbation at pos {best_pos}: {current_makespan} -> {pert_mk}")
                        current_sequence = pert_seq
                        current_makespan = pert_mk
                        completion_times = pert_ct
                        no_improvement_streak = 0
                        # Track best if accidentally improved
                        if current_makespan < best_makespan:
                            best_makespan = current_makespan
                            best_sequence = current_sequence.copy()
                    else:
                        if verbose:
                            print("Skip perturbation: degradation too large.")
                else:
                    if verbose:
                        print("No candidates for perturbation; stopping.")
                    break
            else:
                if verbose:
                    print("No improvement; continuing.")
        else:
            no_improvement_streak = 0

        # Limited-range insertion phase (delta-based, larger but still adjacent-derived moves)
        if not improvement_found and no_improvement_streak >= 2:
            insertion_improvement = False
            n = len(current_sequence)
            # Consider only top few positions to bound work
            candidate_positions = top_pairs[:min(10, len(top_pairs))]
            # For each candidate, try moving within a window of size W
            W = 14
            for pos in candidate_positions:
                left = max(0, pos - W)
                right = min(n - 1, pos + W)
                # Try moving job at pos to targets within [left, right]
                for insert_pos in list(range(left, pos)) + list(range(pos + 1, right + 1)):
                    new_seq, new_mk, new_ct = evaluate_insertion_delta(
                        processing_times, current_sequence, pos, insert_pos, completion_times
                    )
                    if new_mk < current_makespan:
                        if verbose:
                            print(f"Improved: {current_makespan} -> {new_mk} by inserting job {pos} at {insert_pos}")
                        current_sequence = new_seq
                        current_makespan = new_mk
                        completion_times = new_ct
                        if current_makespan < best_makespan:
                            best_makespan = current_makespan
                            best_sequence = current_sequence.copy()
                        insertion_improvement = True
                        break
                if insertion_improvement:
                    break
            if insertion_improvement:
                improvement_found = True
                no_improvement_streak = 0

        # Windowed re-optimization around the most critical region
        if improvement_found:
            # Re-score and focus on top-1 region
            scores = []
            for pos in range(len(current_sequence) - 1):
                score = score_adjacent_pair(current_sequence, pos, processing_times, bottleneck_machine, job_totals, len(current_sequence), bn_proc, bn_threshold)
                scores.append((pos, score))
            scores.sort(key=lambda x: (-x[1], x[0]))
            focus_pos = scores[0][0]
            n = len(current_sequence)
            W = 18
            L = max(0, focus_pos - W)
            R = min(n - 2, focus_pos + W)
            # Intensify within [L, R]
            while True:
                improved_window = False
                for pos in range(L, R + 1):
                    new_mk, new_ct = calculate_makespan_delta(processing_times, current_sequence, pos, completion_times)
                    if new_mk < current_makespan:
                        current_sequence = swap_adjacent(current_sequence, pos)
                        current_makespan = new_mk
                        completion_times = new_ct
                        improved_window = True
                        if current_makespan < best_makespan:
                            best_makespan = current_makespan
                            best_sequence = current_sequence.copy()
                        if recompute_bottleneck:
                            bottleneck_machine = identify_bottleneck_machine(processing_times)
                if not improved_window:
                    break

    # Calculate total search time
    search_time = time.perf_counter() - start_time
    
    # Always return the best solution found (robust to non-improving perturbations)
    return best_sequence, best_makespan, iterations_used, search_time

# Add this at the end to avoid circular imports
from makespan import calculate_makespan, calculate_completion_times, calculate_makespan_delta