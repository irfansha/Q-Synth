from qiskit import QuantumCircuit

from Tests.test_utils import EXAMPLES_DIR, count_swaps_cx, get_cx_count
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import \
    check_circuit_equivalence_of_cnot_circuits
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_synthesis_reachability import \
    optimize_cnot_circuit_with_reachability_encoding
from qsynth.api import check_equivalence, handle_zero_cost_swaps

ecai24_circuit = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
ecai24_SR_variant = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")

strategies = ["k-step", "inc", "going-up", "going-down", "from-middle", "atmost", "binary", "maxsat"]
metric = "cx-count"


def test_ecai24_S_variant():
    # Given circuit ecai24
    circuit = ecai24_circuit

    # When encoding and solving using S variant
    for strategy in strategies:
        optimized_circuit = optimize_cnot_circuit_with_reachability_encoding(circuit, False, None, metric, strategy,
                                                                             None, "intermediate_files").circuit

        # Then the solution should be correct
        swaps, cnots = count_swaps_cx(optimized_circuit)
        assert swaps == 0
        assert cnots == 3



def test_ecai24_with_permutation():
    # Given circuit ecai24
    circuit = ecai24_circuit

    # When encoding and solving using W variant
    for strategy in strategies:
        result = optimize_cnot_circuit_with_reachability_encoding(circuit, True, None, metric, strategy,
                                                                             None, "intermediate_files")
        optimized_circuit = result.circuit

        check_equivalence(circuit, optimized_circuit, result.final_mapping)

        # Then the solution should be correct
        cnots = get_cx_count(optimized_circuit)
        assert cnots == 2



def test_ecai24_with_restrictions():
    # Given circuit ecai24 with coupling graph connecting qubit neighbours
    circuit = ecai24_SR_variant

    coupling_graph = [[0, 1], [1, 2], [2, 3]]
    coupling_graph += [[j, i] for i, j in coupling_graph]

    # When encoding and solving using S+R variant
    for strategy in strategies:
        result = optimize_cnot_circuit_with_reachability_encoding(circuit, False, coupling_graph, metric,
                                                                             strategy, None,
                                                                             "intermediate_files")
        check_equivalence(circuit, result.circuit, result.final_mapping)

        # Then the solution should be correct
        swaps, cnots = count_swaps_cx(result.circuit)
        assert swaps == 0
        assert cnots == 8



def test_ecai24_with_permutations_and_restrictions():
    # Given circuit ecai24 with coupling graph connecting qubit neighbours
    circuit = ecai24_SR_variant

    coupling_graph = [[0, 1], [1, 2], [2, 3]]
    coupling_graph += [[j, i] for i, j in coupling_graph]

    # When encoding and solving using W+R variant
    for strategy in strategies:
        result = optimize_cnot_circuit_with_reachability_encoding(circuit, True, coupling_graph, metric,
                                                                             strategy, None,
                                                                             "intermediate_files")
        check_equivalence(circuit, result.circuit, result.final_mapping)

        # Then the solution should be correct
        cnots = get_cx_count(result.circuit)
        assert cnots == 5

