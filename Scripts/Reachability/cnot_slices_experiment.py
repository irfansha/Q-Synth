from pathlib import Path
import csv
import time

from qiskit import QuantumCircuit

from qsynth.CnotSynthesis.cnot_synthesis_sat_qbf import cnot_optimization
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import count_cx_swaps_as_3_cx


def run_cnot_slices_experiment(metric):
    slices_path = "../../Benchmarks/CNOT-slices"
    benchmarks = ["barenco_tof_3", "barenco_tof_4", "barenco_tof_5", "mod5_4", "mod_mult_55", "qft_4", "rc_adder_6",
                  "tof_3", "tof_4", "tof_5", "vbe_adder_3"]
    strategies = ["forward", "backward", "k-step", "inc", "going-up", "going-down", "from-middle", "atmost", "binary",
                  "maxsat"]
    strategy_stats = {}

    for strategy in strategies:
        old_cnot_count = 0
        total_solving_time = 0
        optimized_cnot_count = 0
        for benchmark in benchmarks:
            # Go through all the benchmark's slices sorted by slice number
            for file in sorted((Path(slices_path) / benchmark).iterdir(),
                               key=lambda x: int(x.name[:-5].split("_")[-1])):
                circuit_in = QuantumCircuit.from_qasm_file(str(file))
                old_cnot_count += count_cx_swaps_as_3_cx(circuit_in)
                print(f"Optimizing {file.name}")
                start_time = time.perf_counter()
                result = cnot_optimization(
                    circuit_in,
                    solver="pysat-cd19",
                    time=60,
                    minimization=metric,
                    verbose=-1,
                    search_strategy=strategy,
                    qubit_permute = False,
                    check=True
                )
                total_solving_time += time.perf_counter() - start_time
                if result.timed_out:
                    print(f"Timed out with strategy {strategy} on slice {file.name}")
                    optimized_cnot_count += count_cx_swaps_as_3_cx(circuit_in)
                    continue
                optimized_cnot_count += count_cx_swaps_as_3_cx(result.circuit)
        strategy_stats[strategy] = (old_cnot_count, optimized_cnot_count, total_solving_time)

    with open(f"intermediate_files/strategy_stats_{metric}.csv", "w", newline="") as f:
        writer = csv.writer(f)

        # header
        writer.writerow(["strategy", f"old {metric}", f"new {metric}", "solving time"])

        # rows
        for strategy, (old_stat, new_stat, total_solving_time) in strategy_stats.items():
            writer.writerow([strategy, old_stat, new_stat, total_solving_time])


if __name__ == "__main__":
    run_cnot_slices_experiment(metric="cx-count")
    run_cnot_slices_experiment(metric="cx-depth")
