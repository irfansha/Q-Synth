import numpy as np
from pysat.formula import CNFPlus
from qiskit import qpy, QuantumCircuit

from qsynth.ReachabilitySolver.encodings.cnot_rz_synthesis.cnot_rz_utils import remove_gates_by_name, e, ar, \
    get_goal_matrix_and_phase_polynomial_from_cnot_rz_circuit, get_rz_sequence_from_action_sequence, \
    get_cnot_rz_circuit_converted_to_z_t_tdg_s_sdg
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_encoding import CnotReachabilityEncoding
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import m, \
    get_initial_state_matrix_from_variables, add_trailing_swaps, get_cx_sequence_from_action_sequence, \
    count_cx_swaps_as_3_cx
from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution
from qsynth.ReachabilitySolver.framework.variable import Variable
from qsynth.Utilities.result import MappingResult


class CnotRzReachabilityEncoding(CnotReachabilityEncoding):
    @classmethod
    def from_encoding_spec(cls, payload: dict):
        with open(payload["circuit_path"], "rb") as f:
            circuit = qpy.load(f)[0]
        return CnotRzReachabilityEncoding(
            circuit=circuit,
            qubit_permutation=payload["qubit_permutation"],
            coupling_graph=payload["coupling_graph"],
            metric=payload["metric"],
        )

    def __init__(self,
                 circuit: QuantumCircuit,
                 qubit_permutation=False,
                 coupling_graph=None,
                 metric="cx-count",
                 ):
        cnot_circuit = remove_gates_by_name(circuit, "rz")
        super().__init__(
            circuit=cnot_circuit,
            qubit_permutation=qubit_permutation,
            coupling_graph=coupling_graph,
            metric=metric,
        )
        if metric == "cx-count":
            # Avoid n(n-1) upper bound from CNOT encoding as it may be too low
            self.upper_bound = count_cx_swaps_as_3_cx(circuit)
        # Same for action variable bound
        if metric in [ "bounded_cx-depth_local_cx-count", "bounded_cx-count_local_cx-depth"]:
            self.action_variable_bound = count_cx_swaps_as_3_cx(circuit)

        _, state_to_phase = get_goal_matrix_and_phase_polynomial_from_cnot_rz_circuit(circuit)
        self.rz_gates = []
        for state, theta in state_to_phase.items():
            self.rz_gates.append((theta, state))

    def get_initial_state_for_time(self, t) -> CNFPlus:
        cnf = super().get_initial_state_for_time(t)
        v_id = self.id_pool.id

        for r in range(len(self.rz_gates)):
            cnf.append([v_id(e(r, t))])

        return cnf

    def get_goal_state_for_time(self, t) -> CNFPlus:
        cnf = super().get_goal_state_for_time(t)
        v_id = self.id_pool.id
        n = self.circuit.num_qubits

        for r in range(len(self.rz_gates)):
            cnf.append([-v_id(e(r, t))] + [v_id(ar(r, q, t)) for q in range(n)])

        cnf.extend(self._get_applied_rotation_constraints_for_time(t))

        return cnf

    def get_transition_predicate_for_time(self, t) -> CNFPlus:
        cnf = super().get_transition_predicate_for_time(t)
        v_id = self.id_pool.id
        n = self.circuit.num_qubits

        # Extend disjunction of ar (applied rotation) variables
        # Each rotation should happen on some qubit at some time step
        for r in range(len(self.rz_gates)):
            cnf.append([-v_id(e(r, t))] + [v_id(ar(r, q, t)) for q in range(n)] + [v_id(e(r, t + 1))])

        cnf.extend(self._get_applied_rotation_constraints_for_time(t))

        return cnf

    def _get_applied_rotation_constraints_for_time(self, t):
        cnf = CNFPlus()
        v_id = self.id_pool.id
        n = self.circuit.num_qubits

        # ar_{r,q} <=> the state on qubit q matches rotation r
        for r, rz_gate_tuple in enumerate(self.rz_gates):
            theta, state = rz_gate_tuple
            for q in range(n):
                # ar_{r,q} => AND(m_{i,q} if state[i] else -m_{i,q} for 0 ≤ i < n)
                for i in range(n):
                    if state[i]:
                        cnf.append([ -v_id(ar(r, q, t)), v_id(m(i, q, t))])
                    else:
                        cnf.append([ -v_id(ar(r, q, t)), -v_id(m(i, q, t))])
                # ar_{r,q} <= AND(m_{i,q} if state[i] else -m_{i,q} for 0 ≤ i < n)
                cnf.append([ v_id(ar(r, q, t)) ] + [ -v_id(m(i, q, t)) if state[i]
                                                     else --v_id(m(i, q, t)) for i in range(n)])
        return cnf


    def get_state_variables_for_time(self, t) -> list[Variable]:
        state_vars = super().get_state_variables_for_time(t)
        for r in range(len(self.rz_gates)):
            state_vars.append(e(r, t))
            for q in range(self.circuit.num_qubits):
                state_vars.append(ar(r, q, t))
        return state_vars

    def get_action_variables_for_time(self, t) -> list[Variable]:
        action_vars = super().get_action_variables_for_time(t)
        return action_vars

    def get_variable_names_for_solution_view(self) -> list[str]:
        var_names = super().get_variable_names_for_solution_view()
        return var_names + ["ar"]

    def decode_reachability_solution(self, reachability_solution: ReachabilitySolution):
        num_qubits = self.circuit.num_qubits
        circuit = QuantumCircuit(num_qubits)

        cx_sequence = get_cx_sequence_from_action_sequence(reachability_solution.action_sequence, self.metric)
        rz_sequence = get_rz_sequence_from_action_sequence(reachability_solution.action_sequence)

        initial_state_matrix = get_initial_state_matrix_from_variables(num_qubits, reachability_solution)
        permutation = np.argwhere(initial_state_matrix == 1)
        mapping = {}

        for qi, qj in permutation:
            # If entry (i,j) is 1 in initial state matrix then qubit j will map to qubit i
            mapping[qj] = qi

        for timestep, rz_gates in enumerate(rz_sequence):
            # Apply rotations before CNOT gates
            for rz_index, qubit in rz_gates:
                theta, _ = self.rz_gates[rz_index]
                circuit.rz(theta, mapping[qubit])
            if timestep == len(cx_sequence):
                # Rz sequence may be a time step longer than CNOT sequence
                break
            for ctrl, trg in cx_sequence[timestep]:
                circuit.cx(mapping[ctrl], mapping[trg])

        for var in reachability_solution.goal_state:
            # Go through all variables in goal state to find permutation variables p_{j,k,t}
            if var.name != "p": continue
            j, k = var.params
            mapping[k] = j

        # Add mapping for unpermuted qubits
        for qi in range(num_qubits):
            if qi not in mapping:
                mapping[qi] = qi

        add_trailing_swaps(circuit, mapping)
        circuit = get_cnot_rz_circuit_converted_to_z_t_tdg_s_sdg(circuit)
        initial_mapping = {i: i for i in range(circuit.num_qubits)}
        return MappingResult(circuit, initial_mapping=initial_mapping)
