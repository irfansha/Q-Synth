import numpy as np
from qiskit import QuantumCircuit

from Tests.test_utils import get_cx_count, get_rz_count, EXAMPLES_DIR, get_cx_depth, get_cx_count_swaps_as_3_cx
from qsynth import get_coupling_graph
from qsynth.api import check_equivalence, cnot_rz_synthesis, cnot_rz_peephole_synthesis

strategies = ["k-step", "inc", "going-up", "going-down", "from-middle", "atmost", "binary", "maxsat"]
ecai24_coupling_graph = [[0, 1], [1,0], [1, 2], [2,1], [2, 3], [3,2]]


def test_simple_cnot_t_circuit():
    circuit = QuantumCircuit(3)
    circuit.cx(0, 1)
    circuit.rz(np.pi/4, 1) # T
    circuit.cx(1, 2)
    circuit.rz(7 * np.pi/4, 2) # Tdg

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Already optimal
        assert rz_count == 2
        assert cx_count == 2


def test_rz_merge():
    circuit = QuantumCircuit(1)
    circuit.rz(np.pi/4, 0)
    circuit.rz(np.pi/4, 0)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Expect a single Rz(pi/2)
        assert rz_count == 1
        assert cx_count == 0


def test_rz_cancellation():
    circuit = QuantumCircuit(1)
    circuit.rz(np.pi/4, 0)
    circuit.rz(-np.pi/4, 0)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Rz gates should cancel out each other
        assert rz_count == 0
        assert cx_count == 0


def test_rz_modulo_2pi():
    circuit = QuantumCircuit(1)
    circuit.rz(-np.pi/2, 0)
    circuit.rz(5 * np.pi/2, 0)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Rz gates should cancel out each other
        assert rz_count == 0
        assert cx_count == 0


def test_rz_commutes_through_cnot_control_qubit():
    circuit = QuantumCircuit(2)
    circuit.cx(0, 1)
    circuit.rz(np.pi/4, 0)  # control
    circuit.cx(0, 1)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should reduce to a single Rz on qubit 1
        assert rz_count == 1
        assert cx_count == 0


def test_two_qubit_phase_gadget():
    circuit = QuantumCircuit(2)
    circuit.cx(0, 1)
    circuit.rz(np.pi/3, 1)
    circuit.cx(0, 1)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should already be optimal
        assert rz_count == 1
        assert cx_count == 2


def test_merge_identical_phase_gadgets():
    circuit = QuantumCircuit(2)

    # First gadget
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(0, 1)

    # Second gadget (same parity)
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(0, 1)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should merge into a single gadget with one Rz gate
        assert rz_count == 1
        assert cx_count == 2


def test_3_qubit_phase_gadget():
    circuit = QuantumCircuit(3)
    circuit.cx(0, 1)
    circuit.cx(1,2)
    circuit.rz(np.pi, 2) # Rz(π) on x0 ⨁ x1 ⨁ x2
    circuit.cx(2,1)
    circuit.cx(1,0)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should already be optimal
        assert rz_count == 1
        assert cx_count == 4


def test_gate_conversions():
    circuit = QuantumCircuit(2)
    circuit.cx(1, 0)
    circuit.z(0)
    circuit.s(0)
    circuit.t(0)
    circuit.sdg(0)
    circuit.tdg(0)
    circuit.cx(1, 0)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should merge into a single gadget with one Rz gate
        assert rz_count == 1
        assert cx_count == 2


# --------------------------- ECAI-24 CIRCUIT TESTS -------------------------------


def test_ecai24_qubit_permutation():
    circuit = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    circuit.rz(np.pi, 1)

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", output_qubit_permute=True,
                                   search_strategy=strategy)

        check_equivalence(circuit, result.circuit, result.final_mapping)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should be CNOT count optimal as Rz gate is on output qubit states
        assert rz_count == 1
        assert cx_count == 2


def test_ecai24_no_permutation_with_restrictions():
    circuit = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    circuit.rz(np.pi, 2) # x2
    circuit.rz(np.pi/4, 3) # x1

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", coupling_graph=ecai24_coupling_graph,
                                   search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should be CNOT count optimal as Rz gates are on output qubit states
        assert rz_count == 2
        assert cx_count == 8


def test_ecai24_with_permutation_and_restrictions():
    circuit = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    circuit.rz(np.pi, 2) # x2
    circuit.rz(np.pi/4, 3) # x1

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-count", coupling_graph=ecai24_coupling_graph,
                                   output_qubit_permute=True, search_strategy=strategy)

        check_equivalence(circuit, result.circuit, result.final_mapping)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should be CNOT count optimal as Rz gates are on output qubit states
        assert rz_count == 2
        assert cx_count == 5


def test_ecai24_depth_with_permutation_and_restrictions():
    circuit = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    circuit.rz(np.pi, 2) # x2
    circuit.rz(np.pi/4, 3) # x1

    for strategy in strategies:
        result = cnot_rz_synthesis(circuit=circuit, metric="cx-depth", coupling_graph=ecai24_coupling_graph,
                                   search_strategy=strategy)

        check_equivalence(circuit, result.circuit, result.final_mapping)
        cx_depth = get_cx_depth(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # Should be CNOT depth optimal as Rz gates are on output qubit states
        assert rz_count == 2
        assert cx_depth == 7



# --------------- PEEPHOLE SYNTHESIS TESTS ----------------------

def test_hadamard_gate_separating_gadgets_already_optimal():
    circuit = QuantumCircuit(2)

    # First gadget
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(0, 1)

    # Separate gadgets by a Hadamard gate
    circuit.h(0)

    # Second gadget (same parity)
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(0, 1)

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # The H gate should split the circuit into two slices, so it is already optimal
        assert rz_count == 2
        assert cx_count == 4


def test_hadamard_gate_separating_gadgets_one_slice_optimal():
    circuit = QuantumCircuit(2)

    # First gadget
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(0, 1)

    # Separate gadgets by a Hadamard gate
    circuit.h(0)

    # Second gadget (same parity)
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(0, 1)

    # Third gadget
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(0, 1)

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        # The H gate should split the circuit into two slices, so only the two last gadgets can merge
        assert rz_count == 2
        assert cx_count == 4


def test_slicing_with_permutation():
    circuit = QuantumCircuit(2)

    # SWAP gate, but the intermediate Rz gate makes the optimal number of gates 2 with permutation
    circuit.cx(0, 1)
    circuit.rz(np.pi / 4, 1)
    circuit.cx(1, 0)
    circuit.cx(0, 1)

    # Split slices
    # As H gate is on q1 between the swaps, it should end up on q0
    circuit.h(1)

    # SWAP gate, should disappear as it only changes the final mapping
    circuit.cx(0, 1)
    circuit.cx(1, 0)
    circuit.cx(0, 1)

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-count", output_qubit_permute=True,
                                            search_strategy=strategy)

        check_equivalence(circuit, result.circuit, result.final_mapping)
        cx_count = get_cx_count(result.circuit)
        rz_count = get_rz_count(result.circuit)
        assert rz_count == 1
        assert cx_count == 2


def test_random_clifford_circuit_no_permutation():
    circuit_path = "Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates/04q_33936.qasm"
    circuit = QuantumCircuit.from_qasm_file(circuit_path)

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-count", search_strategy=strategy)

        check_equivalence(circuit, result.circuit)
        cx_count = get_cx_count(result.circuit)
        # CNOT+Rz synthesis should not improve upon optimal result from Clifford synthesis
        assert cx_count >= 6



def test_random_clifford_circuit_with_permutation():
    circuit_path = "Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates/04q_50494.qasm"
    circuit = QuantumCircuit.from_qasm_file(circuit_path)

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-count", output_qubit_permute=True,
                                            search_strategy=strategy)

        check_equivalence(circuit, result.circuit, result.final_mapping)
        cx_count = get_cx_count(result.circuit)
        # CNOT+Rz synthesis should not improve upon optimal result from Clifford synthesis
        assert cx_count >= 4



def test_mod5_4_no_permutation_on_sycamore():
    circuit_path = "Benchmarks/Feynman/mapped/sycamore-54/mod5_4.qasm"
    circuit = QuantumCircuit.from_qasm_file(circuit_path)
    sycamore_coupling_graph = get_coupling_graph("sycamore")

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-count", coupling_graph=sycamore_coupling_graph,
                                            search_strategy=strategy)

        check_equivalence(circuit, result.circuit)


def test_depth_random_clifford_circuit_no_permutation():
    circuit_path = "Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates/04q_99346.qasm"
    circuit = QuantumCircuit.from_qasm_file(circuit_path)

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-depth", search_strategy=strategy)
        check_equivalence(circuit, result.circuit)
        cx_depth = get_cx_depth(result.circuit)
        # CNOT+Rz synthesis should not improve upon optimal result from Clifford synthesis
        assert cx_depth >= 3


def test_depth_random_clifford_circuit_with_permutation():
    circuit_path = "Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates/04q_50494.qasm"
    circuit = QuantumCircuit.from_qasm_file(circuit_path)

    for strategy in strategies:
        result = cnot_rz_peephole_synthesis(circuit=circuit, metric="cx-depth", search_strategy=strategy)

        check_equivalence(circuit, result.circuit, result.final_mapping)
        cx_depth = get_cx_depth(result.circuit)

        # CNOT+Rz synthesis should not improve upon optimal result from Clifford synthesis
        assert cx_depth >= 3


def test_bounded_depth_local_count_on_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/ECAI-24/tpar-optimized/tof_3.qasm")

    depth_optimal_circuit = cnot_rz_peephole_synthesis(circuit=circuit_in, metric="cx-depth", search_strategy="binary").circuit
    depth_optimal_cx_count = get_cx_count(depth_optimal_circuit)
    last_cx_count = None

    for strategy in ["forward", "backward", "maxsat"]:
        final_optimized_circuit = cnot_rz_peephole_synthesis(circuit=circuit_in, metric="cx-count",
                                                             bound_metric="cx-depth", search_strategy=strategy).circuit
        check_equivalence(circuit_in, final_optimized_circuit)

        cx_count = get_cx_count(final_optimized_circuit)
        assert cx_count <= depth_optimal_cx_count
        if last_cx_count is not None:
            assert cx_count == last_cx_count


def test_bounded_count_local_depth_on_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/ECAI-24/permuted_mapped/barenco_tof_3.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    original_cx_count = get_cx_count_swaps_as_3_cx(circuit_in)

    for strategy in strategies:
        optimized_circuit = cnot_rz_peephole_synthesis(
            circuit=circuit_in,
            coupling_graph=coupling_graph,
            metric="cx-depth",
            bound_metric="cx-count",
            search_strategy=strategy).circuit

        check_equivalence(circuit_in, optimized_circuit)

        cx_count = get_cx_count_swaps_as_3_cx(optimized_circuit)
        # Slicing can change so cx_count may be lowered even more
        assert cx_count <= original_cx_count
