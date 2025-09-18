"""
Main entry point for Flow Shop Scheduling Problem solver.

This module orchestrates the execution of the Flow Shop Scheduling system,
reading CSV input, applying heuristics, improving solutions, and displaying results.
"""

import sys
import os
import argparse
from typing import List, Optional

# Import our modules
from io_utils import read_csv_data, validate_processing_times, print_data_summary
from makespan import calculate_makespan, print_sequence_analysis
from heuristics import neh_heuristic, compare_heuristics, print_heuristic_comparison
from improvements import apply_improvements, print_improvement_results


def solve_flow_shop(csv_file_path: str, 
                   use_improvements: bool = True,
                   improvement_methods: List[str] = None,
                   verbose: bool = True) -> dict:
    """
    Main function to solve Flow Shop Scheduling Problem.
    
    Args:
        csv_file_path (str): Path to CSV file containing processing times
        use_improvements (bool): Whether to apply improvement algorithms
        improvement_methods (List[str], optional): List of improvement methods to use
        verbose (bool): Whether to print detailed output
        
    Returns:
        dict: Results containing best sequence, makespan, and other metrics
    """
    try:
        # Step 1: Read and validate input data
        if verbose:
            print("=" * 60)
            print("FLOW SHOP SCHEDULING PROBLEM SOLVER")
            print("=" * 60)
            print(f"Reading data from: {csv_file_path}")
        
        processing_times, job_names = read_csv_data(csv_file_path)
        validate_processing_times(processing_times)
        
        if verbose:
            print_data_summary(processing_times, job_names)
        
        # Step 2: Apply NEH heuristic for initial solution
        if verbose:
            print("\nApplying NEH heuristic for initial solution...")
        
        neh_sequence = neh_heuristic(processing_times)
        neh_makespan = calculate_makespan(processing_times, neh_sequence)
        
        if verbose:
            print(f"NEH Heuristic Result:")
            print(f"  Sequence: {' -> '.join([job_names[i] for i in neh_sequence])}")
            print(f"  Makespan: {neh_makespan:.2f}")
        
        # Step 3: Compare different heuristics (optional detailed analysis)
        if verbose:
            print_heuristic_comparison(processing_times, job_names)
        
        # Step 4: Apply improvement algorithms
        best_sequence = neh_sequence
        best_makespan = neh_makespan
        improvement_results = None
        
        if use_improvements:
            if verbose:
                print("\nApplying improvement algorithms...")
            
            if improvement_methods is None:
                improvement_methods = ['2opt', 'insert', 'vns']  # Skip genetic for speed
            
            best_sequence, best_makespan, improvement_results = apply_improvements(
                processing_times, neh_sequence, improvement_methods
            )
            
            if verbose:
                print_improvement_results(improvement_results, job_names)
        
        # Step 5: Final results
        if verbose:
            print("\n" + "=" * 60)
            print("FINAL RESULTS")
            print("=" * 60)
            print(f"Best sequence: {' -> '.join([job_names[i] for i in best_sequence])}")
            print(f"Best makespan: {best_makespan:.2f}")
            
            if use_improvements and improvement_results:
                initial_makespan = improvement_results['initial'][1]
                improvement_pct = ((initial_makespan - best_makespan) / initial_makespan * 100)
                print(f"Improvement over NEH: {improvement_pct:.1f}%")
            
            print("=" * 60)
            
            # Detailed analysis of best sequence
            print_sequence_analysis(processing_times, best_sequence, job_names)
        
        # Return results for programmatic use
        return {
            'best_sequence': best_sequence,
            'best_makespan': best_makespan,
            'job_names': job_names,
            'processing_times': processing_times,
            'neh_sequence': neh_sequence,
            'neh_makespan': neh_makespan,
            'improvement_results': improvement_results
        }
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except ValueError as e:
        print(f"Data validation error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def create_sample_data(file_path: str, num_jobs: int = 5, num_machines: int = 3) -> None:
    """
    Create a sample CSV file for testing.
    
    Args:
        file_path (str): Path where to save the sample file
        num_jobs (int): Number of jobs
        num_machines (int): Number of machines
    """
    import random
    
    # Generate random processing times between 1 and 20
    random.seed(42)  # For reproducible results
    
    with open(file_path, 'w', newline='') as file:
        # Write header
        file.write(','.join([f'Machine_{i+1}' for i in range(num_machines)]) + '\n')
        
        # Write job data
        for job in range(num_jobs):
            times = [str(random.randint(1, 20)) for _ in range(num_machines)]
            file.write(','.join(times) + '\n')
    
    print(f"Sample data created at: {file_path}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Flow Shop Scheduling Problem Solver using NEH heuristic and improvements"
    )
    
    parser.add_argument(
        'csv_file', 
        nargs='?',
        help='Path to CSV file containing processing times'
    )
    
    parser.add_argument(
        '--no-improvements', 
        action='store_true',
        help='Skip improvement algorithms (use only NEH heuristic)'
    )
    
    parser.add_argument(
        '--methods', 
        nargs='+',
        choices=['2opt', 'insert', 'vns', 'genetic'],
        default=['2opt', 'insert', 'vns'],
        help='Improvement methods to use'
    )
    
    parser.add_argument(
        '--quiet', 
        action='store_true',
        help='Minimal output (only final results)'
    )
    
    parser.add_argument(
        '--create-sample', 
        metavar='FILENAME',
        help='Create a sample CSV file for testing'
    )
    
    parser.add_argument(
        '--sample-jobs', 
        type=int, 
        default=5,
        help='Number of jobs in sample data (default: 5)'
    )
    
    parser.add_argument(
        '--sample-machines', 
        type=int, 
        default=3,
        help='Number of machines in sample data (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Handle sample data creation
    if args.create_sample:
        create_sample_data(args.create_sample, args.sample_jobs, args.sample_machines)
        return
    
    # Check if CSV file is provided
    if not args.csv_file:
        # Create and use default sample if no file provided
        sample_path = "sample_flow_shop_data.csv"
        print("No CSV file provided. Creating sample data...")
        create_sample_data(sample_path)
        csv_file = sample_path
    else:
        csv_file = args.csv_file
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        print("Use --create-sample to generate sample data.")
        sys.exit(1)
    
    # Solve the problem
    results = solve_flow_shop(
        csv_file_path=csv_file,
        use_improvements=not args.no_improvements,
        improvement_methods=args.methods,
        verbose=not args.quiet
    )
    
    if results is None:
        sys.exit(1)
    
    # Simple output for quiet mode
    if args.quiet:
        sequence_names = [results['job_names'][i] for i in results['best_sequence']]
        print(f"Best sequence: {' -> '.join(sequence_names)}")
        print(f"Makespan: {results['best_makespan']:.2f}")


if __name__ == "__main__":
    main()
