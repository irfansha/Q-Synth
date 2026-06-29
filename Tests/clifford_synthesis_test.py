# Required imports
from qsynth import get_coupling_graph
from qsynth.api import clifford_synthesis, clifford_peephole_synthesis
from Tests.test_utils import (
    EXAMPLES_DIR,
    ECAI_DIR,
    count_swaps_cx,
    count_depth_cx_depth,
    get_cx_depth_swaps_as_3cx, get_1_qubit_gate_count, get_h_s_sx_count,
)
from qiskit import QuantumCircuit, circuit


RANDOM_CLIFFORD_PATH = "Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates"

# simpleaux tests:


def test_sat_gates_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = clifford_synthesis(circuit=circuit_in, metric="cx-count", output_qubit_permute=False).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_sat_depth_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = clifford_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=False).circuit

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    assert cx_depth == 3


def test_sat_gates_permute_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-count", output_qubit_permute=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 25


def test_sat_depth_permute_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=True)

    # Asserts
    _, cx_depth = count_depth_cx_depth(result.circuit)
    assert cx_depth == 21


# simple aux with gate ordering + simple paths :


def test_sat_gates_gate_ordering_simple_paths_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-count", simple_path_restrictions=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 3


def test_sat_depth_gate_ordering_simple_paths_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=False,
                                         simple_path_restrictions=True)

    # Asserts
    _, cx_depth = count_depth_cx_depth(result.circuit)
    assert cx_depth == 3


def test_sat_gates_permute_gate_ordering_simple_paths_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-count", output_qubit_permute=True,
                                         simple_path_restrictions=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 25


def test_sat_depth_permute_gate_ordering_simple_paths_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=True,
                                         simple_path_restrictions=True)

    # Asserts
    _, cx_depth = count_depth_cx_depth(result.circuit)
    assert cx_depth == 21


# simple aux with gate ordering + simple paths + disabled qubits :


def test_sat_gates_permute_gate_ordering_simple_paths_disable_unused_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-count", output_qubit_permute=True,
                                         disable_unused_qubits=False)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 25


def test_sat_depth_permute_gate_ordering_simple_paths_disable_unused_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=True,
                                         disable_unused_qubits=False)

    # Asserts
    _, cx_depth = count_depth_cx_depth(result.circuit)
    assert cx_depth == 21


def test_sat_gates_disable_unused_barenco_tof_3_melbourne():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm"
    )
    coupling_graph = get_coupling_graph("melbourne")

    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-count", coupling_graph=coupling_graph)

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 2
    assert cx == 31


def test_sat_depth_disable_unused_barenco_tof_3_melbourne():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm"
    )
    coupling_graph = get_coupling_graph("melbourne")

    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-depth", coupling_graph=coupling_graph)

    # Asserts
    cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)
    assert cx_depth == 32


def test_sat_qubits_gates_ecai_24_SR_linear():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    coupling_graph = get_coupling_graph("line-4")

    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-count", coupling_graph=coupling_graph)

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 7


def test_sat_qubits_gates_backward_ecai_24_SR_linear():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    coupling_graph = get_coupling_graph("line-4")

    result = clifford_peephole_synthesis(circuit=circuit_in, metric="cx-count", coupling_graph=coupling_graph,
                                         gate_ordering=False, search_strategy="backward")

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 7



# -------------- PLANNING TESTS ---------------------

def test_planning_cnot_optimal_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    result = clifford_synthesis(circuit=circuit_in, metric="cx-count", model="planning")

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 3


def test_planning_cnot_03q55125_lama():
    circuit_in = QuantumCircuit.from_qasm_file(f"{RANDOM_CLIFFORD_PATH}/03q_55125.qasm")

    result = clifford_synthesis(circuit=circuit_in, metric="cx-count", postprocess_1q_gates=None, model="planning")

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    one_q_count = get_h_s_sx_count(result.circuit)
    assert swaps == 0
    assert cx == 3
    assert one_q_count == 14


def test_planning_cnot_fd_ms_03q05306():
    circuit_in = QuantumCircuit.from_qasm_file(f"{RANDOM_CLIFFORD_PATH}/03q_05306.qasm")

    result = clifford_synthesis(circuit=circuit_in, metric="cx-count", postprocess_1q_gates=None, model="planning",
                                solver="fd-ms")

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    one_q_count = get_h_s_sx_count(result.circuit)
    assert swaps == 0
    assert cx == 4
    assert one_q_count == 16


def test_planning_cnot_1q_fd_ms_03q55125():
    circuit_in = QuantumCircuit.from_qasm_file(f"{RANDOM_CLIFFORD_PATH}/03q_55125.qasm")

    result = clifford_synthesis(circuit=circuit_in, metric="cx-count_1q-count", postprocess_1q_gates=None,
                                model="planning", solver="fd-ms")

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    one_q_count = get_h_s_sx_count(result.circuit)
    assert swaps == 0
    assert cx == 3
    assert one_q_count == 6


def test_planning_cnot_1q_lama_03q33936():
    circuit_in = QuantumCircuit.from_qasm_file(f"{RANDOM_CLIFFORD_PATH}/03q_33936.qasm")

    result = clifford_synthesis(circuit=circuit_in, metric="cx-count_1q-count", postprocess_1q_gates=None,
                                model="planning")

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    one_q_count = get_h_s_sx_count(result.circuit)
    assert swaps == 0
    assert cx == 3
    assert one_q_count == 4


def test_sat_1q_rigid_lama_1q_03q_99346():
    circuit_in = QuantumCircuit.from_qasm_file(f"{RANDOM_CLIFFORD_PATH}/03q_99346.qasm")

    result = clifford_synthesis(circuit=circuit_in, metric="cx-count", postprocess_1q_gates="rigid", model="sat")

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    one_q_count = get_h_s_sx_count(result.circuit)
    assert swaps == 0
    assert cx == 4
    assert one_q_count == 9


def test_sat_1q_rigid_lama_1q_04q99346():
    circuit_in = QuantumCircuit.from_qasm_file(f"{RANDOM_CLIFFORD_PATH}/04q_99346.qasm")

    result = clifford_synthesis(circuit=circuit_in, metric="cx-count", postprocess_1q_gates="rigid", model="sat")

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    one_q_count = get_h_s_sx_count(result.circuit)
    assert swaps == 0
    assert cx == 5
    assert one_q_count == 13
