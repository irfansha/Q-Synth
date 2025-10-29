from qiskit import QuantumCircuit
from qsynth.CliffordSynthesis.circuit_utils import (
    compute_cnot_cost,
    compute_cnot_without_swaps_cost,
    compute_cnot_depth,
    compute_cnotdepth_swaps_as_3cx,
)


def print_stats(circuit: QuantumCircuit, opt_circuit: QuantumCircuit) -> None:
    print(
        f"cx-depth        : {compute_cnot_depth(circuit)} -> {compute_cnot_depth(opt_circuit)}"
    )
    print(
        f"cx-count        : {compute_cnot_without_swaps_cost(circuit)} -> {compute_cnot_without_swaps_cost(opt_circuit)}"
    )
    print(
        f"cx-depth (s=3cx): {compute_cnotdepth_swaps_as_3cx(circuit)} -> {compute_cnotdepth_swaps_as_3cx(opt_circuit)}"
    )
    print(
        f"cx-count (s=3cx): {compute_cnot_cost(circuit)} -> {compute_cnot_cost(opt_circuit)}"
    )
