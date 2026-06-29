import os
from typing import Optional

from qiskit import QuantumCircuit, qpy

import qsynth.LayoutSynthesis.architecture
from qsynth.ReachabilitySolver.encodings.layout_synthesis.layout_reachability_encoding import LayoutSynthesisReachabilityEncoding
from qsynth.ReachabilitySolver.api.encoding_spec import EncodingSpec
from qsynth.ReachabilitySolver.api.solver_runner import run_reachability_solver_with_timeout
from qsynth.ReachabilitySolver.solvers.solver_extraction import get_solver_for_strategy
from qsynth.ReachabilitySolver.encodings.layout_synthesis.layout_reachability_utils import fast_upper_bound_on_swaps
from qsynth.Utilities.result import MappingResult


def layout_synthesis_using_reachability(circuit: QuantumCircuit,
                                        upper_bound=None,
                                        platform=None,
                                        coupling_graph=None,
                                        strategy="kstep",
                                        allow_ancillas=True,
                                        intermediate_files_path="intermediate_files",
                                        timeout=None
                                        ) -> MappingResult:
    """
    Does layout synthesis on the input circuit by making a LayoutReachabilityEncoding instance and solving it with a
    ReachabilitySolver according to the chosen strategy.
    Assumptions: Two way encoding with ancillas, without bridges, and with bidirectional coupling.
    Returns:
        None if no solution was found. Else:
        A MappingResult containing the optimal mapped circuit and opt_val set to the number of swaps.
    """
    # Get the coupling graph and number of physical qubits
    if coupling_graph is None:
        if platform is None:
            raise TypeError("You must specify either a platform or a coupling graph.")
        coupling_graph, num_physical_qubits = get_coupling_graph_from_platform(platform)
    else:
        num_physical_qubits = max([max(p, q) for p, q in coupling_graph]) + 1

    # If no upper bound is given, we compute one using SABRE
    if upper_bound is None:
        upper_bound = fast_upper_bound_on_swaps(circuit, coupling_graph)
        print(f"Found heuristic upper bound of {upper_bound} using SABRE.")

    # If timeout is set, we run the layout synthesis in a subprocess with timeout
    if timeout is not None:
        encoding_spec = make_encoding_spec(circuit, coupling_graph, num_physical_qubits, allow_ancillas, upper_bound,
                                           intermediate_files_path)
        mapping_result = run_reachability_solver_with_timeout(circuit, encoding_spec, strategy, timeout, intermediate_files_path)
        if mapping_result.circuit is None:
            # Ensure same behavior as Q-Synth:
            # No result found is indicated by returning None
            return None
        return mapping_result

    # Else we run normally
    encoding = LayoutSynthesisReachabilityEncoding(circuit, coupling_graph, num_physical_qubits, allow_ancillas,
                                                   upper_bound)
    solver = get_solver_for_strategy(strategy)
    solution = solver.solve(encoding)
    if solution is None:
        return None

    return encoding.decode_reachability_solution(solution)


def make_encoding_spec(circuit,
                       coupling_graph,
                       num_pqubits,
                       allow_ancillas,
                       upper_bound,
                       intermediate_files_path):
    # Make sure the intermediate directory exists so the solver can write files there
    os.makedirs(intermediate_files_path, exist_ok=True)
    circuit_qpy_path = f"{intermediate_files_path}/circuit.qpy"
    with open(circuit_qpy_path, "wb") as f:
        qpy.dump(circuit, f)

    payload = {
        "circuit_path": f"{intermediate_files_path}/circuit.qpy",
        "coupling_graph": coupling_graph,
        "num_pqubits": num_pqubits,
        "allow_ancillas": allow_ancillas,
        "upper_bound": upper_bound
    }

    return EncodingSpec(encoding_type="layout", payload=payload)


def get_coupling_graph_from_platform(platform):
    (coupling_map,
     bi_coupling_map,
     bridge_bicoupling_map,
     bridge_middle_pqubit_dict,
     reverse_swap_distance_dict,
     num_physical_qubits) = qsynth.LayoutSynthesis.architecture.platform(
        platform, 1, None
    )
    return bi_coupling_map, num_physical_qubits
