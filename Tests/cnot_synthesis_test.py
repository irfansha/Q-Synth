# Required imports
from qsynth import get_coupling_graph
from qsynth.api import cnot_peephole_synthesis, cnot_synthesis
from Tests.test_utils import (
    EXAMPLES_DIR,
    ECAI_DIR,
    count_swaps_cx,
    count_depth_cx_depth,
)
from qiskit import QuantumCircuit


def test_sat_gates_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    result = cnot_synthesis(circuit=circuit_in, metric="cx-count", check=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 3


def test_planning_gates_fd_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    result = cnot_synthesis(circuit=circuit_in, metric="cx-count", model="planning", solver="fd-ms", check=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 3


def test_planning_gates_madagascar_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    result = cnot_synthesis(circuit=circuit_in, metric="cx-count", model="planning", solver="madagascar", check=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 3


def test_sat_depth_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", check=True)

    # Asserts
    depth, cx_depth = count_depth_cx_depth(result.circuit)
    assert depth == 3
    assert cx_depth == 3


def test_sat_gates_qubits_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )

    result = cnot_peephole_synthesis(circuit=circuit_in, metric="cx-count", output_qubit_permute=True, check=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 26


def test_sat_gates_barenco_tof_3_melbourne():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm"
    )
    coupling_graph = get_coupling_graph("melbourne")

    result = cnot_peephole_synthesis(circuit=circuit_in, metric="cx-count", coupling_graph=coupling_graph, check=True)

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 3
    assert cx == 30


def test_sat_gates_ecai_24_line_4_without_permutation():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    coupling_graph = get_coupling_graph("line-4")

    result = cnot_synthesis(circuit=circuit_in, metric="cx-count", coupling_graph=coupling_graph, check=True)

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 8


def test_sat_gates_ecai_24_line_4_with_permutation():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    coupling_graph = get_coupling_graph("line-4")

    result = cnot_synthesis(circuit=circuit_in, metric="cx-count", coupling_graph=coupling_graph,
                            output_qubit_permute=True, check=True)

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 5


def test_qbf_gates_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )

    result = cnot_peephole_synthesis(circuit=circuit_in, metric="cx-count", model="qbf", check=True)

    # Asserts
    swaps, cx = count_swaps_cx(result.circuit)
    assert swaps == 0
    assert cx == 41


def test_qbf_depth_qft_4():
    circuit_in = QuantumCircuit.from_qasm_file(f"{ECAI_DIR}/tpar-optimized/qft_4.qasm")

    result = cnot_peephole_synthesis(circuit=circuit_in, metric="cx-depth", model="qbf", check=True)

    # Asserts (cx-depth is the optimization target; total depth is an incidental secondary measure)
    depth, cx_depth = count_depth_cx_depth(result.circuit)
    assert cx_depth == 77
    assert depth == 171
