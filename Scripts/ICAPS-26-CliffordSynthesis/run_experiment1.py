#!/usr/bin/env python3

# Experiment 1: Random Clifford circuits (3-5 qubits)
# SAT-based cx-count minimization vs Planning-based normalform cx-count minimization.
# Planners: madagascar, lama, scorpion, symk
# Timeout: 1800 seconds per instance

import os
import sys
import time
import glob
import re
import argparse

from qiskit import QuantumCircuit, qasm2
from qsynth import clifford_synthesis

# Path to benchmarks:
script_dir = os.path.dirname(os.path.abspath(__file__))
benchmarks_dir = os.path.join(script_dir, "..", "..", "Benchmarks", "Random-Clifford", "tket_optimized_without_swaps_no_u3_gates")

TIMEOUT = 1800


def get_sorted_instances(directory):
    """Get all .qasm files from directory, sorted naturally."""
    files = glob.glob(os.path.join(directory, "*.qasm"))
    files.sort(key=lambda f: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', f)])
    return files


def filter_three_qubit(instances):
    """Keep only the 3-qubit benchmarks (named 03q_*.qasm)."""
    return [f for f in instances if os.path.basename(f).startswith("03q")]


def run_sat(circuit_path):
    """Run SAT-based clifford synthesis with cx-count minimization."""
    circuit = QuantumCircuit.from_qasm_file(circuit_path)
    start = time.perf_counter()
    result = clifford_synthesis(circuit=circuit, metric="cx-count", postprocess_1q_gates=None, model="sat",
                                timeout=TIMEOUT, verbose=0)
    elapsed = time.perf_counter() - start
    if result.no_plan_found:
        print(f"no_plan_found")
    print(f"Execution time: {elapsed:.2f} seconds")
    return result


def run_planning(circuit_path, planner):
    """Run planning-based clifford synthesis with normalform encoding, cx-count metric."""
    circuit = QuantumCircuit.from_qasm_file(circuit_path)
    start = time.perf_counter()
    result = clifford_synthesis(circuit=circuit, metric="cx-count", postprocess_1q_gates=None, model="planning",
                                solver=planner, timeout=TIMEOUT, verbose=0)
    elapsed = time.perf_counter() - start
    if result.no_plan_found:
        print(f"no_plan_found")
    print(f"Execution time: {elapsed:.2f} seconds")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiment 1: SAT vs planning normalform cx-count minimization.")
    parser.add_argument(
        "--three-qubit-only",
        action="store_true",
        help="Only run the 3-qubit benchmarks (for local correctness checking against the Zenodo data).",
    )
    args = parser.parse_args()

    instances = get_sorted_instances(benchmarks_dir)
    if args.three_qubit_only:
        instances = filter_three_qubit(instances)
    print(f"Experiment 1: Random Clifford instances ({len(instances)} circuits)")
    print(f"Benchmarks: {benchmarks_dir}")
    print(f"Timeout: {TIMEOUT}s")
    print("=" * 80)

    # SAT-based cx-count:
    print("\n\n--- SAT model, metric=cx-count ---")
    print("=" * 80)
    for circuit_path in instances:
        print(f"\nCircuit: {os.path.basename(circuit_path)}")
        run_sat(circuit_path)

    # Planning normalform cx-count with various planners:
    for planner in ["madagascar", "lama", "scorpion", "symk"]:
        print(f"\n\n--- Planning model, encoding=normalform, metric=cx-count, planner={planner} ---")
        print("=" * 80)
        for circuit_path in instances:
            print(f"\nCircuit: {os.path.basename(circuit_path)}")
            run_planning(circuit_path, planner)
