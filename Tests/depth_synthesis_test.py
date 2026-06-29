# Required imports
from qsynth import get_coupling_graph, layout_synthesis
from Tests.test_utils import (
    CIRCUITS_DIR,
    get_depth_swaps_as_3cx, get_cx_depth_swaps_as_3cx, get_swap_count,
)
from qiskit import QuantumCircuit

from qsynth.api import check_equivalence


def test_tenerife_sat_adder_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth")


    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    assert depth == 15


def test_melbourne_sat_adder_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    assert depth == 11


def test_melbourne_sat_qaoa5_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    assert depth == 14


def test_tokyo_sat_qaoa5_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    coupling_graph = get_coupling_graph("tokyo")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    assert depth == 14


def test_tenerife_sat_adder_cx_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="cx-depth")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    cx_depth = get_cx_depth_swaps_as_3cx(circuit)
    assert cx_depth == 10


def test_tenerife_sat_adder_depth_cx_count():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth",
                              secondary_metric="cx-count")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    swaps = get_swap_count(circuit)
    assert depth == 15
    assert swaps == 1


def test_tenerife_sat_adder_cx_depth_cx_count():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="cx-depth",
                              secondary_metric="cx-count")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    cx_depth = get_cx_depth_swaps_as_3cx(circuit)
    swaps = get_swap_count(circuit)
    assert cx_depth == 10
    assert swaps == 1


def test_tenerife_plan_cost_opt_depth_adder():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth", model="cost_opt",
                              solver="fd-bjolp")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    assert depth == 15


def test_tenerife_plan_cond_cost_opt_depth_adder():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth", num_ancillary_qubits=0,
                              model="cond_cost_opt", solver="fd-ms")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    assert depth == 15


def test_tenerife_plan_lc_incr_depth_or():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/or.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric="depth", num_ancillary_qubits=0,
                              model="lc_incr", solver="fd-bjolp")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    depth = get_depth_swaps_as_3cx(circuit)
    assert depth == 8
