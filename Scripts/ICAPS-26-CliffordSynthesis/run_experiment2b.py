#!/usr/bin/env python3

# Experiment 2b: Random Clifford circuits (3-5 qubits) - SAT-synthesized versions
# Planning-based rigidcnot gate-count minimization.
# Input: circuits from Experiment 1 that were first optimized by SAT (cx-count).
# Planners: lama, scorpion, symk
# Timeout: 1800 seconds per instance
#
# NOTE: The input benchmarks for this experiment are the SAT-optimized outputs from Experiment 1.
#       Place them in: Benchmarks/Random-Clifford/sat_synthesized/
#       Or adjust the benchmarks_dir variable below.

import os
import sys
import time
import glob
import re
import argparse

from qiskit import QuantumCircuit, qasm2
from qsynth.CliffordSynthesis.clifford_synthesis_planning import clifford_optimization as clifford_optimization_planning

# Path to benchmarks (SAT-synthesized from Experiment 1):
script_dir = os.path.dirname(os.path.abspath(__file__))
benchmarks_dir = os.path.join(script_dir, "..", "..", "Benchmarks", "Random-Clifford", "sat_synthesized")

TIMEOUT = 1800


def get_sorted_instances(directory):
    """Get all .qasm files from directory, sorted naturally."""
    files = glob.glob(os.path.join(directory, "*.qasm"))
    files.sort(key=lambda f: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', f)])
    return files


def filter_three_qubit(instances):
    """Keep only the 3-qubit benchmarks (named 03q_*.qasm)."""
    return [f for f in instances if os.path.basename(f).startswith("03q")]


def run_planning_rigidcnot(circuit_path, planner):
    """Run planning-based clifford synthesis with rigidcnot encoding, gate-count metric."""
    circuit = QuantumCircuit.from_qasm_file(circuit_path)
    start = time.perf_counter()
    result = clifford_optimization_planning(
        circuit=circuit,
        encoding="rigidcnot",
        planner=planner,
        metric="gate-count",
        time=TIMEOUT,
        verbose=0,
    )
    elapsed = time.perf_counter() - start
    if result.no_plan_found:
        print(f"no_plan_found")
    print(f"Execution time: {elapsed:.2f} seconds")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiment 2b: planning rigidcnot gate-count minimization on SAT-synthesized circuits.")
    parser.add_argument(
        "--three-qubit-only",
        action="store_true",
        help="Only run the 3-qubit benchmarks (for local correctness checking against the Zenodo data).",
    )
    args = parser.parse_args()

    if not os.path.isdir(benchmarks_dir):
        print(f"ERROR: Benchmarks directory not found: {benchmarks_dir}")
        print(f"This experiment requires SAT-synthesized circuits from Experiment 1.")
        print(f"Run Experiment 1 first, then place the optimized circuits in the above directory.")
        sys.exit(1)

    instances = get_sorted_instances(benchmarks_dir)
    if args.three_qubit_only:
        instances = filter_three_qubit(instances)
    print(f"Experiment 2b: Random Clifford SAT-synthesized instances ({len(instances)} circuits)")
    print(f"Benchmarks: {benchmarks_dir}")
    print(f"Model: planning, Encoding: rigidcnot, Metric: gate-count")
    print(f"Timeout: {TIMEOUT}s")
    print("=" * 80)

    # Planning rigidcnot gate-count with various planners:
    for planner in ["lama", "scorpion", "symk"]:
        print(f"\n\n--- Planning model, encoding=rigidcnot, metric=gate-count, planner={planner} ---")
        print("=" * 80)
        for circuit_path in instances:
            print(f"\nCircuit: {os.path.basename(circuit_path)}")
            run_planning_rigidcnot(circuit_path, planner)
