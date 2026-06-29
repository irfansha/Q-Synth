import os
from typing import Optional

from qiskit import QuantumCircuit, qpy

from qsynth.ReachabilitySolver.api.encoding_spec import EncodingSpec
from qsynth.ReachabilitySolver.api.solver_runner import run_reachability_solver_with_timeout
from qsynth.ReachabilitySolver.encodings.cnot_rz_synthesis.cnot_rz_reachability_encoding import \
    CnotRzReachabilityEncoding
from qsynth.ReachabilitySolver.encodings.cnot_rz_synthesis.cnot_rz_utils import get_circuit_converted_to_cnot_rz, \
    check_equivalence_of_cnot_rz_circuits, get_cnot_rz_circuit_converted_to_z_t_tdg_s_sdg
from qsynth.ReachabilitySolver.solvers.solver_extraction import get_solver_for_strategy


def optimize_cnot_rz_circuit_with_reachability_encoding(
        circuit: QuantumCircuit,
        qubit_permutation: bool = False,
        coupling_graph: Optional[list[tuple[int,int]]] = None,
        metric: str = "cx-count",
        strategy: str = "inc",
        check: bool = False,
        timeout: Optional[float] = None,
        intermediate_files_path = "intermediate_files",
):
    """
    CNOT (count or depth) optimal synthesis of circuits of gate set { CNOT, SWAP, Rz, Z, T, S, Tdg, Sdg }.
    Args:
        circuit: the circuit to be optimized
        qubit_permutation: whether to allow qubit permutation of the output
        coupling_graph: optionally, the synthesis can respect layout restrictions
        metric: the metric to optimize ('cx-count' or 'cx-depth', defaults to 'cx-count')
        strategy: the search strategy to use
        check: whether to check for equivalence of input circuit and output circuit
        timeout: optional timeout in seconds (search is unbounded per default)
        intermediate_files_path: path to intermediate files (defaults to 'intermediate_files')
    """
    cnot_rz_circuit = get_circuit_converted_to_cnot_rz(circuit)

    # Circuit should be CNOT+Rz circuit
    for gate in cnot_rz_circuit.data:
        assert gate.name in ["cx", "swap", "rz"]

    minimize = "action_vars" if metric == "bounded_cx-depth_local_cx-count" else "time_steps"

    # We run the synthesis with timeout if timeout parameter is set and there are >4 used qubits in the circuit
    if timeout is not None and circuit.num_qubits > 4:
        encoding_spec = make_encoding_spec(
            cnot_rz_circuit,
            qubit_permutation,
            coupling_graph,
            metric,
            intermediate_files_path
        )
        mapping_result = run_reachability_solver_with_timeout(circuit, encoding_spec, strategy, timeout, intermediate_files_path, minimize)
        return mapping_result

    encoding = CnotRzReachabilityEncoding(cnot_rz_circuit,
                                        qubit_permutation,
                                        coupling_graph,
                                        metric)
    solver = get_solver_for_strategy(strategy, minimize=minimize)
    solution = solver.solve(encoding)
    mapping_result = encoding.decode_reachability_solution(solution)

    if check:
        check_equivalence_of_cnot_rz_circuits(cnot_rz_circuit, mapping_result.circuit)

    return mapping_result



def make_encoding_spec(circuit, qubit_permutation, coupling_graph, metric, intermediate_files_path):
    # Make sure the intermediate directory exists so the solver can write files there
    os.makedirs(intermediate_files_path, exist_ok=True)
    circuit_qpy_path = f"{intermediate_files_path}/circuit.qpy"
    with open(circuit_qpy_path, "wb") as f:
        qpy.dump(circuit, f)

    payload = {
        "circuit_path": f"{intermediate_files_path}/circuit.qpy",
        "qubit_permutation": qubit_permutation,
        "coupling_graph": coupling_graph,
        "metric": metric,
    }

    return EncodingSpec(encoding_type="cnot_rz", payload=payload)
