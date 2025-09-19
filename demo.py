"""
Demonstration script for Flow Shop Scheduling Problem solver.

This script showcases various features and capabilities of the system.
"""

import os
from main import solve_flow_shop, create_sample_data
from io_utils import read_csv_data
from heuristics import compare_heuristics


def demo_basic_functionality():
    """Demonstrate basic functionality with a simple example."""
    print("=" * 60)
    print("DEMO 1: BASIC FUNCTIONALITY")
    print("=" * 60)
    
    # Create a simple test case
    create_sample_data("demo_basic.csv", 4, 3)
    
    # Solve with basic settings
    results = solve_flow_shop("demo_basic.csv", verbose=False)
    
    print(f"Problem: 4 jobs, 3 machines")
    print(f"Pendulum Result: {results['pendulum_makespan']:.2f}")
    print(f"Best Result: {results['best_makespan']:.2f}")
    
    # Clean up
    os.remove("demo_basic.csv")


def demo_heuristic_comparison():
    """Demonstrate comparison of different heuristics."""
    print("\n" + "=" * 60)
    print("DEMO 2: HEURISTIC COMPARISON")
    print("=" * 60)
    
    # Create test data
    create_sample_data("demo_heuristics.csv", 6, 4)
    processing_times, job_names = read_csv_data("demo_heuristics.csv")
    
    # Compare all heuristics
    results = compare_heuristics(processing_times)
    
    print(f"Problem: 6 jobs, 4 machines")
    print(f"{'Heuristic':<12} {'Makespan':<10} {'Rank'}")
    print("-" * 35)
    
    for i, (name, sequence, makespan) in enumerate(results):
        print(f"{name:<12} {makespan:<10.2f} {i+1}")
    
    best_heuristic = results[0]
    worst_heuristic = results[-1]
    improvement = ((worst_heuristic[2] - best_heuristic[2]) / worst_heuristic[2] * 100)
    print(f"\nBest heuristic ({best_heuristic[0]}) is {improvement:.1f}% better than worst ({worst_heuristic[0]})")
    
    # Clean up
    os.remove("demo_heuristics.csv")




def demo_scalability():
    """Demonstrate system performance with different problem sizes."""
    print("\n" + "=" * 60)
    print("DEMO 3: SCALABILITY TEST")
    print("=" * 60)
    
    problem_sizes = [
        (5, 3, "Small"),
        (10, 5, "Medium"),
        (15, 6, "Large"),
        (20, 8, "X-Large")
    ]
    
    print(f"{'Size':<10} {'Jobs':<5} {'Machines':<9} {'Pendulum Time':<13} {'Makespan'}")
    print("-" * 53)
    
    import time
    
    for jobs, machines, size_name in problem_sizes:
        filename = f"demo_scale_{size_name.lower()}.csv"
        create_sample_data(filename, jobs, machines)
        
        start_time = time.time()
        results = solve_flow_shop(filename, verbose=False)
        end_time = time.time()
        
        duration = end_time - start_time
        makespan = results['pendulum_makespan']
        
        print(f"{size_name:<10} {jobs:<5} {machines:<9} {duration:<9.3f}s {makespan:.2f}")
        
        # Clean up
        os.remove(filename)


def main():
    """Run all demonstrations."""
    print("FLOW SHOP SCHEDULING SYSTEM DEMONSTRATION")
    print("This demo showcases the capabilities and performance of the system.\n")
    
    try:
        demo_basic_functionality()
        demo_heuristic_comparison()
        demo_scalability()
        
        print("\n" + "=" * 60)
        print("DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("The Flow Shop Scheduling system successfully demonstrated:")
        print("✓ Flexible CSV input handling")
        print("✓ Multiple heuristic algorithms (including custom Pendulum)")
        print("✓ Scalability across problem sizes")
        print("✓ Comprehensive analysis and reporting")
        
    except Exception as e:
        print(f"Demo error: {e}")


if __name__ == "__main__":
    main()
