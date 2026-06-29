# Required imports
from qsynth import api, get_coupling_graph
from Tests.test_utils import (
    CIRCUITS_DIR,
    count_swaps_cx,
    get_swap_count, get_depth, get_cx_depth_swaps_as_3cx,
)
from qiskit import QuantumCircuit


def test_sycamore_sat_4gt13_92():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/4gt13_92.qasm")
    coupling_graph = get_coupling_graph("sycamore")

    result = api.layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="cx-count",
                                  num_ancillary_qubits=2)

    circuit = result.circuit
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 10
    assert cx == 30


def test_tokyo_sat_mod5mils_65():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm"
    )
    coupling_graph = get_coupling_graph("tokyo")

    result = api.layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="cx-count",
                                  num_ancillary_qubits=2, search_strategy="backward", swap_upper_bound=2)

    circuit = result.circuit
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 16


def test_eagle_sat_vqe_8_4_5_100():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/VQE/vqe_8_1_5_100.qasm")
    coupling_graph = get_coupling_graph("eagle")

    result = api.layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="cx-count",
                                  subarchitecture=True, num_ancillary_qubits=0)

    circuit = result.circuit
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 3
    assert cx == 18


# Perform some tests with depth as well
def test_tokyo_sat_qaoa5_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    coupling_graph = get_coupling_graph("tokyo")

    result = api.layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth",
                                  num_ancillary_qubits=2)

    circuit = result.circuit
    # Asserts
    depth = get_depth(circuit)
    assert depth == 14


def test_tenerife_sat_adder_cx_depth_cx_count():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = api.layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="cx-depth",
                                  secondary_metric="cx-count", num_ancillary_qubits=1)

    circuit = result.circuit
    # Asserts
    cx_depth = get_cx_depth_swaps_as_3cx(circuit)
    swaps = get_swap_count(circuit)
    assert cx_depth == 10
    assert swaps == 1


def test_tokyo_sat_qaoa5_cx_depth_cx_count():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    coupling_graph = get_coupling_graph("tokyo")

    result = api.layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="cx-depth",
                                  secondary_metric="cx-count", num_ancillary_qubits=2)

    circuit = result.circuit
    # Asserts
    cx_depth = get_cx_depth_swaps_as_3cx(circuit)
    swaps = get_swap_count(circuit)
    assert cx_depth == 8
    assert swaps == 0

