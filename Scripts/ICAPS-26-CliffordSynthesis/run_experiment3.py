#!/usr/bin/env python3

# Experiment 3: QEC (Quantum Error Correction) circuits
# Part A: SAT-based cx-count_cx-depth and cx-depth_cx-count optimization on original QEC circuits.
# Part B: Planning-based rigidcnot gate-count optimization on SAT-optimized QEC circuits.
# Planners: symk, scorpion, lama
# Timeout: 10800 seconds (3 hours) per instance
#
# NOTE: Part B requires SAT-optimized QEC circuits from Part A.
#       Place them in: Benchmarks/QECC/sat_optimized/
#       Or adjust the sat_optimized_dir variable below.

import os
import sys
import time
import glob
import re

from qiskit import QuantumCircuit, qasm2
from qsynth import clifford_synthesis
from qsynth.CliffordSynthesis.clifford_synthesis_planning import clifford_optimization as clifford_optimization_planning

# Path to benchmarks:
script_dir = os.path.dirname(os.path.abspath(__file__))
qec_original_dir = os.path.join(script_dir, "..", "..", "Benchmarks", "QECC")
qec_sat_optimized_dir = os.path.join(script_dir, "..", "..", "Benchmarks", "QECC", "sat_optimized")

TIMEOUT = 10800

# QEC original instances:
qec_original_instances = [
    "steancode.qasm",
    "9-bit-shorcode.qasm",
]


def get_sorted_instances(directory):
    """Get all .qasm files from directory, sorted naturally."""
    files = glob.glob(os.path.join(directory, "*.qasm"))
    files.sort(key=lambda f: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', f)])
    return files


def run_sat_bounded(circuit_path, metric):
    """Run SAT-based clifford synthesis with bounded metric (cx-count_cx-depth or cx-depth_cx-count)."""
    circuit = QuantumCircuit.from_qasm_file(circuit_path)
    start = time.perf_counter()
    result = clifford_synthesis(circuit=circuit, metric=metric, postprocess_1q_gates=None, model="sat", timeout=TIMEOUT,
                                verbose=0)
    elapsed = time.perf_counter() - start
    if result.no_plan_found:
        print(f"no_plan_found")
    print(f"Execution time: {elapsed:.2f} seconds")
    return result


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
    print(f"Experiment 3: QEC circuits")
    print(f"Timeout: {TIMEOUT}s")
    print("=" * 80)

    # Part A: SAT-based bounded optimization on original QEC circuits:
    print("\n\n--- Part A: SAT model, metric=cx-count_cx-depth ---")
    print("=" * 80)
    for filename in qec_original_instances:
        circuit_path = os.path.join(qec_original_dir, filename)
        if not os.path.exists(circuit_path):
            print(f"\nCircuit: {filename} - SKIPPED (not found)")
            continue
        print(f"\nCircuit: {filename}")
        run_sat_bounded(circuit_path, "cx-count_cx-depth")

    print("\n\n--- Part A: SAT model, metric=cx-depth_cx-count ---")
    print("=" * 80)
    for filename in qec_original_instances:
        circuit_path = os.path.join(qec_original_dir, filename)
        if not os.path.exists(circuit_path):
            print(f"\nCircuit: {filename} - SKIPPED (not found)")
            continue
        print(f"\nCircuit: {filename}")
        run_sat_bounded(circuit_path, "cx-depth_cx-count")

    # Part B: Planning rigidcnot gate-count on SAT-optimized QEC circuits:
    if not os.path.isdir(qec_sat_optimized_dir):
        print(f"\nWARNING: SAT-optimized QEC directory not found: {qec_sat_optimized_dir}")
        print(f"Skipping Part B. Run Part A first, then place optimized circuits in the above directory.")
    else:
        instances = get_sorted_instances(qec_sat_optimized_dir)
        for planner in ["symk", "scorpion", "lama"]:
            print(f"\n\n--- Part B: Planning model, encoding=rigidcnot, metric=gate-count, planner={planner} ---")
            print("=" * 80)
            for circuit_path in instances:
                print(f"\nCircuit: {os.path.basename(circuit_path)}")
                run_planning_rigidcnot(circuit_path, planner)
