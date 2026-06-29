from qiskit import QuantumCircuit

from Tests.test_utils import ECAI_DIR, count_swaps_cx, EXAMPLES_DIR, count_depth_cx_depth, \
    get_cx_depth_swaps_as_3cx, generate_random_cnot_circuit
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import count_cx_swaps_as_3_cx
from qsynth.api import check_equivalence, cnot_peephole_synthesis, cnot_synthesis, get_coupling_graph

strategies = ["forward", "k-step", "inc", "going-up", "going-down", "from-middle", "atmost", "binary", "maxsat"]
solver = "pysat-cd19"
verbose = -1
ecai24_coupling_graph = [[0, 1], [1,0], [1, 2], [2,1], [2, 3], [3,2]]


# -------------- CX-COUNT ON BENCHMARKS -------------------

def test_count_barenco_tof_3_on_melbourne_no_permutation():
    input_circuit = QuantumCircuit.from_qasm_file(f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    for strategy in strategies:
        result = cnot_peephole_synthesis(circuit=input_circuit, metric="cx-count", coupling_graph=coupling_graph,
                                         search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(input_circuit, result.circuit)

        swaps, cnots = count_swaps_cx(result.circuit)
        assert swaps == 3, f"Got wrong SWAP count for {strategy}"
        assert cnots == 30, f"Got wrong CNOT count for {strategy}"


def test_count_barenco_tof_3_no_platform_no_permutation():
    input_circuit = QuantumCircuit.from_qasm_file(f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm")

    for strategy in strategies:
        result = cnot_peephole_synthesis(circuit=input_circuit, metric="cx-count", search_strategy=strategy,
                                         solver=solver, verbose=verbose)
        check_equivalence(input_circuit, result.circuit)

        swaps, cnots = count_swaps_cx(result.circuit)
        assert swaps == 0, f"Got wrong SWAP count for {strategy}"
        assert cnots == 41, f"Got wrong CNOT count for {strategy}"


# @pytest.mark.skip()
def test_count_mod5_4_melbourne_no_permutation():
    input_circuit = QuantumCircuit.from_qasm_file(f"{ECAI_DIR}/permuted_mapped/mod5_4.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    for strategy in strategies:
        result = cnot_peephole_synthesis(circuit=input_circuit, metric="cx-count", coupling_graph=coupling_graph,
                                         search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(input_circuit, result.circuit)

        swaps, cnots = count_swaps_cx(result.circuit)
        assert swaps == 3, f"Got wrong SWAP count for {strategy}"
        assert cnots == 39, f"Got wrong CNOT count for {strategy}"


def test_count_mod5_4_no_platform_with_permutation():
    input_circuit = QuantumCircuit.from_qasm_file(f"{ECAI_DIR}/tpar-optimized/mod5_4.qasm")

    for strategy in strategies:
        result = cnot_peephole_synthesis(circuit=input_circuit, metric="cx-count", output_qubit_permute=True,
                                         search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(input_circuit, result.circuit, result.final_mapping)

        swaps, cnots = count_swaps_cx(result.circuit)
        assert swaps == 0, f"Got wrong SWAP count for {strategy}"
        assert cnots == 32, f"Got wrong CNOT count for {strategy}"


# ---------------- CX-COUNT INTERMEDIATE SOLUTION -----------------

def test_count_8_qubit_circuit_intermediate_solution():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/8_qubit_cnot_circuit.qasm")

    # NAIVE-BINARY should find optimal solution in about 2 seconds, but it takes a minute to terminate

    mapping_result = cnot_synthesis(circuit=circuit_in, metric="cx-count", search_strategy="binary", timeout=5)
    check_equivalence(circuit_in, mapping_result.circuit, mapping_result.final_mapping)

    assert mapping_result.timed_out

    swaps, cnots = count_swaps_cx(mapping_result.circuit)
    assert swaps == 0
    assert cnots == 11


# ----------------- CX-DEPTH ON BENCHMARKS -------------------


def test_depth_ecai24_no_platform_no_permutation():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", search_strategy=strategy, solver=solver,
                                verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        circuit_depth, cx_depth = count_depth_cx_depth(result.circuit)
        assert cx_depth == 3


def test_depth_ecai24_no_platform_with_permutation():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")

    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=True,
                                search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        circuit_depth, cx_depth = count_depth_cx_depth(result.circuit)
        assert cx_depth == 2


def test_depth_ecai24_platform_no_permutation():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    coupling_graph = get_coupling_graph("line-4")

    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", coupling_graph=coupling_graph,
                                search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)
        circuit_depth, cx_depth = count_depth_cx_depth(result.circuit)
        assert cx_depth == 7


def test_depth_ecai24_platform_with_permutation():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    coupling_graph = get_coupling_graph("line-4")

    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", coupling_graph=coupling_graph,
                                output_qubit_permute=True, search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)
        circuit_depth, cx_depth = count_depth_cx_depth(result.circuit)
        assert cx_depth == 4


def test_depth_rc_adder_6_slice_35_no_platform_no_permutation():
    circuit_in = QuantumCircuit.from_qasm_file(f"Benchmarks/CNOT-slices/rc_adder_6/rc_adder_6_slice_35.qasm")

    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", search_strategy=strategy, solver=solver,
                                verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)
        assert cx_depth == 5


# --------------- CX-DEPTH ON RANDOM 4 QUBIT CIRCUITS -----------------

def test_depth_random_4_qubit_cnot_circuit_no_platform_no_permutation():
    circuit_in = generate_random_cnot_circuit(number_of_qubits=4)

    optimal_cx_depth = None
    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", search_strategy=strategy, solver=solver,
                                verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        # Test that strategies agree - we do not know the optimal value
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)
        if optimal_cx_depth:
            assert cx_depth == optimal_cx_depth
        optimal_cx_depth = cx_depth


def test_depth_random_4_qubit_cnot_circuit_no_platform_with_permutation():
    circuit_in = generate_random_cnot_circuit(number_of_qubits=4)

    optimal_cx_depth = None
    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=True,
                                search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        # Test that strategies agree - we do not know the optimal value
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)
        if optimal_cx_depth:
            assert cx_depth == optimal_cx_depth
        optimal_cx_depth = cx_depth


def test_depth_random_4_qubit_cnot_circuit_line_4_no_permutation():
    circuit_in = generate_random_cnot_circuit(number_of_qubits=4, platform="line-4")
    coupling_graph = get_coupling_graph("line-4")

    optimal_cx_depth = None
    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", coupling_graph=coupling_graph,
                                search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        # Test that strategies agree - we do not know the optimal value
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)
        if optimal_cx_depth:
            assert cx_depth == optimal_cx_depth
        optimal_cx_depth = cx_depth


def test_depth_random_4_qubit_cnot_circuit_line_4_with_permutation():
    circuit_in = generate_random_cnot_circuit(number_of_qubits=4, platform="line-4")
    coupling_graph = get_coupling_graph("line-4")

    optimal_cx_depth = None
    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", coupling_graph=coupling_graph,
                                output_qubit_permute=True, search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        # Test that strategies agree - we do not know the optimal value
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)
        if optimal_cx_depth:
            assert cx_depth == optimal_cx_depth
        optimal_cx_depth = cx_depth



# ------------------- MULTIPLE METRICS --------------------------

def test_bounded_depth_local_count_on_vbe_adder_slice():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/CNOT-slices/vbe_adder_3/vbe_adder_3_slice_6.qasm")

    original_cx_depth = get_cx_depth_swaps_as_3cx(circuit_in)

    for strategy in ["backward", "goingdown"]:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-count", bound_metric="cx-depth",
                                search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        cx_count = count_cx_swaps_as_3_cx(result.circuit)
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)

        assert cx_depth <= original_cx_depth
        assert cx_count == 8, f"Failed for strategy {strategy}"


def test_bounded_depth_local_count_on_melbourne():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/ECAI-24/permuted_mapped/barenco_tof_3.qasm")
    coupling_graph = get_coupling_graph("melbourne")

    original_cx_depth = get_cx_depth_swaps_as_3cx(circuit_in)

    for strategy in ["backward", "goingdown"]:
        result = cnot_peephole_synthesis(circuit=circuit_in, metric="cx-count", bound_metric="cx-depth",
                                         coupling_graph=coupling_graph, search_strategy=strategy, solver=solver,
                                         verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        cx_count = count_cx_swaps_as_3_cx(result.circuit)
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)

        assert cx_depth <= original_cx_depth
        assert cx_count == 39, f"Failed for strategy {strategy}"


def test_bounded_depth_local_count_with_permutations():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/ECAI-24/tpar-optimized/tof_5.qasm")

    depth_optimal_result = cnot_peephole_synthesis(circuit=circuit_in, metric="cx-depth", output_qubit_permute=True,
                                                   search_strategy="inc", solver=solver, verbose=verbose)
    depth_optimal_circuit_in = depth_optimal_result.circuit

    optimal_cx_depth = get_cx_depth_swaps_as_3cx(depth_optimal_circuit_in)

    for strategy in ["forward", "maxsat"]:
        result = cnot_peephole_synthesis(circuit=depth_optimal_circuit_in, metric="cx-count", bound_metric="cx-depth",
                                         output_qubit_permute=True, search_strategy=strategy, solver=solver,
                                         verbose=verbose)

        combined_final_mapping = {i: result.final_mapping[depth_optimal_result.final_mapping[i]] for i in result.final_mapping}
        check_equivalence(circuit_in, result.circuit, combined_final_mapping)
        circuit = result.circuit

        cx_count = count_cx_swaps_as_3_cx(circuit)
        cx_depth = get_cx_depth_swaps_as_3cx(circuit)

        assert cx_depth <= optimal_cx_depth
        assert cx_count == 52, f"Failed for strategy {strategy}"


def test_vbe_slice_bounded_depth_local_count():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/CNOT-slices/vbe_adder_3/vbe_adder_3_slice_4.qasm")

    original_cx_depth = get_cx_depth_swaps_as_3cx(circuit_in)

    for strategy in ["forward", "goingdown"]:
        mapping_result = cnot_synthesis(circuit=circuit_in, metric="cx-count", bound_metric="cx-depth",
                                        output_qubit_permute=True, search_strategy=strategy, solver=solver,
                                        verbose=verbose)
        check_equivalence(circuit_in, mapping_result.circuit, mapping_result.final_mapping)
        circuit = mapping_result.circuit

        cx_count = count_cx_swaps_as_3_cx(circuit)
        cx_depth = get_cx_depth_swaps_as_3cx(circuit)

        assert cx_depth <= original_cx_depth
        assert cx_count == 5, f"Failed for strategy {strategy}"


def test_bounded_count_local_depth_on_qft_4_slice():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/CNOT-slices/qft_4/qft_4_slice_25.qasm")

    original_cx_count = count_cx_swaps_as_3_cx(circuit_in)

    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", bound_metric="cx-count",
                                search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        cx_count = count_cx_swaps_as_3_cx(result.circuit)
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)

        assert cx_count <= original_cx_count, f"Failed for strategy {strategy}"
        assert cx_depth == 6, f"Failed for strategy {strategy}"


def test_bounded_count_local_depth_with_permutations():
    circuit_in = QuantumCircuit.from_qasm_file("Benchmarks/CNOT-slices/mod_mult_55/mod_mult_55_slice_6.qasm")

    original_cx_count = count_cx_swaps_as_3_cx(circuit_in)

    for strategy in strategies:
        result = cnot_synthesis(circuit=circuit_in, metric="cx-depth", bound_metric="cx-count",
                                search_strategy=strategy, solver=solver, verbose=verbose)
        check_equivalence(circuit_in, result.circuit, result.final_mapping)

        cx_count = count_cx_swaps_as_3_cx(result.circuit)
        cx_depth = get_cx_depth_swaps_as_3cx(result.circuit)

        assert cx_count <= original_cx_count
        assert cx_depth == 4, f"Failed for strategy {strategy}"
