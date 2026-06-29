import pytest
from qiskit import QuantumCircuit

from Tests.test_utils import EXAMPLES_DIR, get_swap_count, get_cx_count, CIRCUITS_DIR, count_swaps_cx
from qsynth import get_coupling_graph
from qsynth.ReachabilitySolver.encodings.layout_synthesis.layout_reachability_utils import fast_upper_bound_on_swaps
from qsynth.api import check_equivalence, layout_synthesis

strategies = ["k-step", "inc", "going-up", "going-down", "from-middle", "atmost", "binary", "maxsat"]


timeout = 10


def test_sat24_circuit():
    circuit = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/sat24.qasm")

    coupling_graph = [ [0,1], [1,0], [1,2], [2,1] ]
    upper_bound = fast_upper_bound_on_swaps(circuit, coupling_graph)

    for strategy in strategies:
        result = layout_synthesis(circuit=circuit, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)
        check_equivalence(circuit, result.circuit, result.final_mapping, result.initial_mapping)
        assert get_swap_count(result.circuit) == 2


def test_star_or():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/or.qasm")
    coupling_graph = get_coupling_graph("star-4")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph)

    for strategy in strategies:
        # No ancillas
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)

        # Asserts
        swaps, cx = count_swaps_cx(result.circuit)
        assert swaps == 2


def test_melbourne_vbe_adder_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/vbe_adder_3.qasm"
    )
    coupling_graph = get_coupling_graph("melbourne")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph)

    for strategy in ["inc", "binary"]:
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)

        circuit = result.circuit
        # Asserts
        swaps, cx = count_swaps_cx(circuit)
        assert swaps == 8, f"Failed for strategy {strategy}"
        assert cx == 50


def test_melbourne_global_adder():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("melbourne")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph)

    for strategy in strategies:
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)


        circuit = result.circuit
        # Asserts
        swaps, cx = count_swaps_cx(circuit)
        assert swaps == 0
        assert cx == get_cx_count(circuit_in)


def test_tenerife_global_adder():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    coupling_graph = get_coupling_graph("tenerife")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph)

    for strategy in strategies:
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)

        circuit = result.circuit
        # Asserts
        swaps, cx = count_swaps_cx(circuit)
        assert swaps == 1
        assert cx == get_cx_count(circuit_in)


def test_melbourne_qaoa5():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    coupling_graph = get_coupling_graph("melbourne")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph)

    for strategy in strategies:
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)

        circuit = result.circuit
        # Asserts
        swaps, cx = count_swaps_cx(circuit)
        assert swaps == 0
        assert cx == get_cx_count(circuit_in)


def test_tenerife_4gt13_92():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/4gt13_92.qasm")
    coupling_graph = get_coupling_graph("tenerife")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph)

    for strategy in strategies:
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)

        circuit = result.circuit
        # Asserts
        swaps, cx = count_swaps_cx(circuit)
        assert swaps == 0
        assert cx == get_cx_count(circuit_in)


def test_4_cnot_cycle_on_cycle_5_without_ancillas():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/date24-sub.qasm")
    coupling_graph = get_coupling_graph("cycle-5")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph, allow_ancillas=False)

    for strategy in strategies:
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, num_ancillary_qubits=0,
                                  search_strategy=strategy, swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)

        circuit = result.circuit
        # Asserts
        swaps, cx = count_swaps_cx(circuit)
        assert swaps == 2
        assert cx == get_cx_count(circuit_in)


def test_4_cnot_cycle_on_cycle_5_with_ancillas():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/date24-sub.qasm")
    coupling_graph = get_coupling_graph("cycle-5")
    upper_bound = fast_upper_bound_on_swaps(circuit_in, coupling_graph)

    for strategy in strategies:
        result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, search_strategy=strategy,
                                  swap_upper_bound=upper_bound, timeout=timeout)

        check_equivalence(circuit_in, result.circuit, result.final_mapping, result.initial_mapping)

        circuit = result.circuit
        # Asserts
        swaps, cx = count_swaps_cx(circuit)
        assert swaps == 1
        assert cx == get_cx_count(circuit_in)


def debug(encoding):
    print("Initial state:")
    print_cnf(encoding.get_initial_state_for_time(0), encoding.id_pool)

    print("Transition predicate:")
    print_cnf(encoding.get_transition_predicate_for_time(0), encoding.id_pool)

    print("Goal state:")
    print_cnf(encoding.get_goal_state_for_time(1), encoding.id_pool)


def print_cnf(cnf, id_pool):
    for clause in cnf.clauses:
        print(" v ".join([ f"{'¬' if lit < 0 else ''}({id_pool.obj(abs(lit))})" for lit in clause ]))
