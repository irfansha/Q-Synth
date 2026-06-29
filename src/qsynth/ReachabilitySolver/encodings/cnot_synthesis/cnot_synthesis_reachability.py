import os
from typing import Optional

from qiskit import QuantumCircuit, qpy

from qsynth.ReachabilitySolver.api.encoding_spec import EncodingSpec
from qsynth.ReachabilitySolver.api.solver_runner import run_reachability_solver_with_timeout
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_encoding import CnotReachabilityEncoding
from qsynth.ReachabilitySolver.solvers.solver_extraction import get_solver_for_strategy


def optimize_cnot_circuit_with_reachability_encoding(
        circuit: QuantumCircuit,
        qubit_permutation: bool,
        coupling_graph: Optional[list[tuple[int, int]]],
        metric: str,
        strategy: str,
        timeout: Optional[float],
        intermediate_files_path,
):
    # Circuit should be CNOT circuit
    for gate in circuit.data:
        assert gate.name in ["cx", "swap"]

    minimize = "action_vars" if metric == "bounded_cx-depth_local_cx-count" else "time_steps"

    # We run the synthesis with timeout if timeout parameter is set and there are >4 used qubits in the circuit
    if timeout is not None and circuit.num_qubits > 4:
        encoding_spec = make_encoding_spec(
            circuit,
            qubit_permutation,
            coupling_graph,
            metric,
            intermediate_files_path
        )
        mapping_result = run_reachability_solver_with_timeout(circuit, encoding_spec, strategy, timeout, intermediate_files_path, minimize)
        return mapping_result

    # Else run synthesis without timeout
    encoding = CnotReachabilityEncoding(circuit,
                                        qubit_permutation,
                                        coupling_graph,
                                        metric)
    solver = get_solver_for_strategy(strategy, minimize=minimize)
    solution = solver.solve(encoding)
    mapping_result = encoding.decode_reachability_solution(solution)

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

    return EncodingSpec(encoding_type="cnot", payload=payload)
