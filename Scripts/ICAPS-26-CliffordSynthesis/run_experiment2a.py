#!/usr/bin/env python3

# Experiment 2a: Random Clifford circuits (3-5 qubits)
# Planning-based costbased cx-count minimization (metric=cx-count_1q-count auto-derives costbased encoding).
# Planners: lama, scorpion, symk
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


def run_planning_costbased(circuit_path, planner):
    """Run planning-based clifford synthesis with costbased encoding (cx-count_1q-count metric)."""
    circuit = QuantumCircuit.from_qasm_file(circuit_path)
    start = time.perf_counter()
    result = clifford_synthesis(circuit=circuit, metric="cx-count_1q-count", postprocess_1q_gates=None,
                                model="planning", solver=planner, timeout=TIMEOUT, verbose=0)
    elapsed = time.perf_counter() - start
    if result.no_plan_found:
        print(f"no_plan_found")
    print(f"Execution time: {elapsed:.2f} seconds")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiment 2a: planning costbased cx-count_1q-count minimization.")
    parser.add_argument(
        "--three-qubit-only",
        action="store_true",
        help="Only run the 3-qubit benchmarks (for local correctness checking against the Zenodo data).",
    )
    args = parser.parse_args()

    instances = get_sorted_instances(benchmarks_dir)
    if args.three_qubit_only:
        instances = filter_three_qubit(instances)
    print(f"Experiment 2a: Random Clifford instances ({len(instances)} circuits)")
    print(f"Benchmarks: {benchmarks_dir}")
    print(f"Model: planning, Encoding: costbased (via metric=cx-count_1q-count)")
    print(f"Timeout: {TIMEOUT}s")
    print("=" * 80)

    # Planning costbased cx-count with various planners:
    for planner in ["lama", "scorpion", "symk"]:
        print(f"\n\n--- Planning model, encoding=costbased, metric=cx-count, planner={planner} ---")
        print("=" * 80)
        for circuit_path in instances:
            print(f"\nCircuit: {os.path.basename(circuit_path)}")
            run_planning_costbased(circuit_path, planner)
