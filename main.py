"""
Flow Shop Scheduling Problem Solver using Pendulum Heuristic

This program solves the Flow Shop Scheduling Problem (FSSP) using the Pendulum heuristic.
It supports both CSV and Taillard-style TXT/FSP input formats.

Usage:
    python main.py <input_file>

Where <input_file> can be a .csv file or a Taillard .txt/.fsp file.
"""

import sys
import os
from typing import List, Optional, Dict, Any

# Import our modules
from io_utils import read_instance, validate_processing_times, print_data_summary
from makespan import calculate_makespan, print_sequence_analysis
from heuristics import pendulum_heuristic


def solve_flow_shop(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Solve the Flow Shop Scheduling Problem using the Pendulum heuristic.
    
    Args:
        file_path: Path to input file (.csv or Taillard .txt/.fsp)
        
    Returns:
        Dictionary with solution details or None if an error occurred
    """
    try:
        # Read and validate input data
        print("=" * 60)
        print("FLOW SHOP SCHEDULING SOLVER (Pendulum Heuristic)")
        print("=" * 60)
        print(f"Reading data from: {file_path}")
        
        processing_times, job_names = read_instance(file_path)
        validate_processing_times(processing_times)
        
        # Print data summary
        print_data_summary(processing_times, job_names)
        
        # Apply Pendulum heuristic
        print("\nApplying Pendulum heuristic...")
        sequence = pendulum_heuristic(processing_times)
        makespan = calculate_makespan(processing_times, sequence)
        
        # Print results
        print("\n" + "=" * 60)
        print("SOLUTION")
        print("=" * 60)
        print(f"Best sequence: {' -> '.join([job_names[i] for i in sequence])}")
        print(f"Makespan: {makespan:.2f}")
        print("=" * 60)
        
        # Detailed analysis
        print_sequence_analysis(processing_times, sequence, job_names)
        
        return {
            'sequence': sequence,
            'makespan': makespan,
            'job_names': job_names,
            'processing_times': processing_times
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


def main():
    """Handle command-line interface."""
    # Check if file path is provided
    if len(sys.argv) != 2:
        print("Usage: python main.py <input_file>")
        print("\nSupported file formats:")
        print("  - CSV files (.csv)")
        print("  - Taillard format (.txt, .fsp)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    # Solve the problem
    result = solve_flow_shop(file_path)
    
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()
