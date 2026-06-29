# Required imports
from qsynth import get_coupling_graph
from Tests.test_utils import CIRCUITS_DIR, count_swaps_cx
from qiskit import QuantumCircuit

from qsynth.api import check_equivalence, layout_synthesis


def test_melbourne_sat_vbe_adder_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/vbe_adder_3.qasm"
    )
    coupling_graph = get_coupling_graph("melbourne")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph)

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 8
    assert cx == 50


def test_sycamore_sat_mod5mils_65():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm"
    )
    coupling_graph = get_coupling_graph("sycamore")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, allow_bridges=True)

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 1
    assert cx == 25


def test_sycamore_sat_mod5mils_65_relaxed():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm"
    )
    coupling_graph = get_coupling_graph("sycamore")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, relaxed_dependencies=True)


    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 4
    assert cx == 16


# Perform some planning tests
def test_melbourne_global_adder():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0, model="global",
                              solver="fd-bjolp")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 0


def test_tenerife_global_adder():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0, model="global",
                              solver="fd-ms")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 1


def test_melbourne_local_qaoa5():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0, model="local",
                              solver="fd-bjolp")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 0


def test_tenerife_lifted_4gt13_92():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/4gt13_92.qasm")
    coupling_graph = get_coupling_graph("tenerife")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0, model="lifted",
                              solver="fd-bjolp")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 0


def test_star_lifted_madagascar_or():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/or.qasm")
    coupling_graph = get_coupling_graph("star-4")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0, model="lifted",
                              solver="madagascar")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 2


def test_cycle_local_relaxed_madagascar_or():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/or.qasm")
    coupling_graph = get_coupling_graph("cycle-4")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=-1,
                              relaxed_dependencies=True, model="local", solver="madagascar")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 1


def test_OCQ_or_madagascar():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/or.qasm")
    coupling_graph = get_coupling_graph("OCQ-tokyo")

    # Compute circuit and opt_val
    result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0, model="local",
                              solver="madagascar")

    circuit = result.circuit
    # Asserts
    check_equivalence(circuit_in, circuit, result.final_mapping, result.initial_mapping)
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 2
