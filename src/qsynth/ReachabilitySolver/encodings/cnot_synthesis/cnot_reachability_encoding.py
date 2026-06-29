from pysat.card import CardEnc
from pysat.formula import CNFPlus
from qiskit import qpy

from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import *

from qsynth.ReachabilitySolver.framework.reachability_encoding import ReachabilityEncoding

from qsynth.Utilities.result import MappingResult


class CnotReachabilityEncoding(ReachabilityEncoding):
    @classmethod
    def from_encoding_spec(cls, payload: dict):
        with open(payload["circuit_path"], "rb") as f:
            circuit = qpy.load(f)[0]
        return CnotReachabilityEncoding(
            circuit=circuit,
            qubit_permutation=payload["qubit_permutation"],
            coupling_graph=payload["coupling_graph"],
            metric=payload["metric"],
        )

    def __init__(self, circuit: QuantumCircuit,
                 qubit_permutation=False,
                 coupling_graph=None,
                 metric="cx-count",
                 ):
        upper_bound = compute_upper_bound(circuit, metric, has_coupling_graph=coupling_graph is not None)
        if metric in [ "bounded_cx-depth_local_cx-count", "bounded_cx-count_local_cx-depth"]:
            action_variable_bound = compute_upper_bound(circuit, "cx-count")
        else:
            action_variable_bound = None
        super().__init__(upper_bound, action_variable_bound)
        self.circuit = circuit
        if not qubit_permutation:
            self.variant = "S" if coupling_graph is None else "S+R"
        else:
            self.variant = "W" if coupling_graph is None else "W+R"
        if coupling_graph is None:
            # Let coupling graph include all qubit pairs
            self.coupling_graph = [[qi, qj] for qi in range(circuit.num_qubits)
                              for qj in range(circuit.num_qubits) if qi != qj]
        else:
            self.coupling_graph = coupling_graph
        self.metric = metric
        self.goal_matrix = get_goal_matrix_from_cnot_circuit(self.circuit)

    def get_initial_state_for_time(self, t):
        v_id = self.id_pool.id
        number_of_qubits = self.circuit.num_qubits
        cnf = CNFPlus()
        if self.variant == "W":
            # Initial state should be a permutation of the identity matrix
            for r in range(number_of_qubits):
                # Exactly one 1 in each row
                exactly_one_in_row = CardEnc.equals(lits=[v_id(m(r, c, t)) for c in range(number_of_qubits)], bound=1,
                                                    vpool=self.id_pool)
                cnf.extend(exactly_one_in_row)
            for c in range(number_of_qubits):
                # Exactly one 1 in each column
                exactly_one_in_column = CardEnc.equals(lits=[v_id(m(r, c, t)) for r in range(number_of_qubits)], bound=1,
                                                       vpool=self.id_pool)
                cnf.extend(exactly_one_in_column)
        else:
            # Variant is S so initial state should be identity matrix
            for r in range(number_of_qubits):
                # Exactly one 1 in each row
                exactly_one = CardEnc.equals(lits=[v_id(m(r, c, t)) for c in range(number_of_qubits)], bound=1, vpool=self.id_pool)
                cnf.extend(exactly_one)

            # 1's in the diagonal
            for q in range(number_of_qubits):
                cnf.append([v_id(m(q, q, t))])

        return cnf


    def get_goal_state_for_time(self, t):
        v_id = self.id_pool.id
        number_of_qubits = self.circuit.num_qubits
        cnf = CNFPlus()

        if self.variant in ["S", "S+R", "W"]:
            # Simple goal state for variants S, W and S+R: The state matrix should correspond to the goal matrix
            for i in range(number_of_qubits):
                for j in range(number_of_qubits):
                    if self.goal_matrix[i][j] == 1:
                        cnf.append([v_id(m(i, j, t))])
                    else:
                        cnf.append([-v_id(m(i, j, t))])
            return cnf

        # Variant is W+R so we need to handle permutation of the goal matrix.
        # The permutation is a 1:1 mapping between columns j in the state matrix and columns k in the goal matrix
        for j in range(number_of_qubits):
            for k in range(number_of_qubits):
                for i in range(number_of_qubits):
                    if self.goal_matrix[i, k] == 1:
                        # If entry (i,k) is true in the goal matrix and column j in the state matrix maps
                        # to column k in the goal matrix, then (i,j) should be true in the state matrix.
                        cnf.append([-v_id(p(j, k, t)), v_id(m(i, j, t))])
                    else:
                        # Vice versa
                        cnf.append([-v_id(p(j, k, t)), -v_id(m(i, j, t))])

        for j in range(number_of_qubits):
            # Each column in the state matrix maps to exactly one column in the goal matrix
            exactly_one_column_in_goal_matrix = CardEnc.equals(
                lits=[v_id(p(j, k, t)) for k in range(number_of_qubits)],
                bound=1,
                vpool=self.id_pool)
            cnf.extend(exactly_one_column_in_goal_matrix)

        for k in range(number_of_qubits):
            # Each column in the goal matrix maps to exactly one column in the state matrix
            exactly_one_column_in_state_matrix = CardEnc.equals(
                lits=[v_id(p(j, k, t)) for j in range(number_of_qubits)],
                bound=1,
                vpool=self.id_pool)
            cnf.extend(exactly_one_column_in_state_matrix)

        return cnf


    def get_transition_predicate_for_time(self, t):
        if self.metric == "cx-count":
            return self._get_count_optimal_transition_predicate_for_time(t)
        else:
            return self._get_depth_optimal_transition_predicate_for_time(t)


    def _get_count_optimal_transition_predicate_for_time(self, t):
        v_id = self.id_pool.id
        n = self.circuit.num_qubits
        cnf = CNFPlus()
        # Exactly one ctrl and trg
        cnf.extend(CardEnc.equals(lits=[v_id(ctrl(i, t)) for i in range(n)], bound=1, vpool=self.id_pool))
        cnf.extend(CardEnc.equals(lits=[v_id(trg(i, t)) for i in range(n)], bound=1, vpool=self.id_pool))

        # Only CNOT on connected qubit pairs
        for i in range(n):
            for j in range(n):
                if [i, j] not in self.coupling_graph:
                    cnf.append([-v_id(ctrl(i, t)), -v_id(trg(j, t))])

        # Do column addition
        for i, j in self.coupling_graph:
            for r in range(n):
                # (ctrl_i ∧ trg_j ∧ m_r,i) => (m_r,j ≠ m'_r,j)
                cnf.append([-v_id(ctrl(i, t)), -v_id(trg(j, t)), v_id(m(r, i, t)),
                            v_id(m(r, j, t)), -v_id(m(r, j, t + 1))])
                cnf.append([-v_id(ctrl(i, t)), -v_id(trg(j, t)), v_id(m(r, i, t)),
                            -v_id(m(r, j, t)), v_id(m(r, j, t + 1))])

                # (ctrl_i ∧ trg_j ∧ ¬m_r,i) => (m_r,j = m'_r,j)
                cnf.append([-v_id(ctrl(i, t)), -v_id(trg(j, t)), -v_id(m(r, i, t)),
                            -v_id(m(r, j, t)), -v_id(m(r, j, t + 1))])
                cnf.append([-v_id(ctrl(i, t)), -v_id(trg(j, t)), -v_id(m(r, i, t)),
                            v_id(m(r, j, t)), v_id(m(r, j, t + 1))])

        # Propagate all columns ≠ trg
        cnf.extend(self._make_column_propagation_constraint_for_time(t))

        return cnf


    def _get_depth_optimal_transition_predicate_for_time(self, t):
        v_id = self.id_pool.id
        n = self.circuit.num_qubits
        cnf = CNFPlus()

        # No CNOT gates on unconnected qubit pairs
        for i in range(n):
            for j in range(n):
                if [i, j] not in self.coupling_graph:
                    cnf.append([-v_id(cnot(i, j, t))])

        # At most one CNOT gate per qubit
        for q in range(n):
            cnot_gates_including_q = [v_id(cnot(i, j, t)) for i,j in self.coupling_graph if i == q or j == q]
            at_most_one_cnot = CardEnc.atmost(lits=cnot_gates_including_q, bound=1, vpool=self.id_pool)
            cnf.extend(at_most_one_cnot)

        # At least one CNOT gate per time step (for efficiency)
        at_least_one_cnot_gate = [ v_id(cnot(i, j, t)) for i,j in self.coupling_graph ]
        cnf.append(at_least_one_cnot_gate)

        # trg_j is true <=> some cnot_{i,j} is true
        for j in range(n):
            # trg_j => (cnot_{0,j} ∨ ... ∨ cnot_{n-1,j})
            cnf.append([ -v_id(trg(j, t)) ] + [ v_id(cnot(i, j, t)) for i in range(n) ])
            # (cnot_{0,j} ∨ ... ∨ cnot_{n-1,j}) => trg_j
            # (¬cnot_{0,j} ∧ ... ∧ ¬cnot_{n-1,j}) ∨ trg_j
            for i in range(n):
                cnf.append([ -v_id(cnot(i, j, t)), v_id(trg(j, t)) ])

        # Do column addition
        for i, j in self.coupling_graph:
            for r in range(n):
                # (cnot_{i,j} ∧ m_r,i) => (m_r,j ≠ m'_r,j)
                cnf.append([-v_id(cnot(i, j, t)), v_id(m(r, i, t)),
                            v_id(m(r, j, t)), -v_id(m(r, j, t + 1))])
                cnf.append([-v_id(cnot(i, j, t)), v_id(m(r, i, t)),
                            -v_id(m(r, j, t)), v_id(m(r, j, t + 1))])

                # (cnot_{i,j} ∧ ¬m_r,i) => (m_r,j = m'_r,j)
                cnf.append([-v_id(cnot(i, j, t)), -v_id(m(r, i, t)),
                            -v_id(m(r, j, t)), -v_id(m(r, j, t + 1))])
                cnf.append([-v_id(cnot(i, j, t)), -v_id(m(r, i, t)),
                            v_id(m(r, j, t)), v_id(m(r, j, t + 1))])

        # Propagate all columns ≠ trg
        cnf.extend(self._make_column_propagation_constraint_for_time(t))

        return cnf


    def _make_column_propagation_constraint_for_time(self, t):
        v_id = self.id_pool.id
        n = self.circuit.num_qubits
        cnf = CNFPlus()

        # Propagate all columns ≠ trg
        for i in range(n):
            for r in range(n):
                # ¬trg_i => (m_r,i = m'_r,i)
                cnf.append([v_id(trg(i, t)), v_id(m(r, i, t)), -v_id(m(r, i, t + 1))])
                cnf.append([v_id(trg(i, t)), -v_id(m(r, i, t)), v_id(m(r, i, t + 1))])

        return cnf

    def get_state_variables_for_time(self, t):
        state_variables = []
        n = self.circuit.num_qubits
        for i in range(n):
            for j in range(n):
                state_variables.append(m(i, j, t))
                if self.variant == "W+R":
                    state_variables.append(p(i, j, t))
        if self.metric != "cx-count":
            for i in range(n):
                state_variables.append(trg(i, t))
        return state_variables


    def get_action_variables_for_time(self, t):
        action_variables = []
        n = self.circuit.num_qubits
        for i in range(n):
            if self.metric == "cx-count":
                action_variables.append(ctrl(i, t))
                action_variables.append(trg(i, t))
            else:
                for j in range(n):
                    if i == j: continue
                    action_variables.append(cnot(i, j, t))
        return action_variables


    def get_variable_names_for_solution_view(self):
        if self.metric == "cx-count":
            return [ "ctrl", "trg" ]
        else:
            return [ "cnot", "trg" ]


    def decode_reachability_solution(self, reachability_solution):
        cx_sequence = get_cx_sequence_from_action_sequence(reachability_solution.action_sequence, self.metric)
        num_qubits = self.circuit.num_qubits
        circuit = QuantumCircuit(num_qubits)

        # S variant
        if self.variant in [ "S", "S+R" ]:
            # Apply all CNOT gates
            for cnots in cx_sequence:
                for control, target in cnots:
                    circuit.cx(control, target)
            return MappingResult(circuit)

        # Variant is W or W+R

        initial_state_matrix = get_initial_state_matrix_from_variables(num_qubits, reachability_solution)
        mapping = {}

        if self.variant == "W":
            # Get permutation of initial matrix as pairs of qubits
            # E.g. [ (0,4), (4,0) ] means that column 0 refers to qubit 4 and vice versa
            permutation = np.argwhere(initial_state_matrix == 1)

            for qi, qj in permutation:
                # If entry (i,j) is 1 in initial state matrix then qubit j will map to qubit i
                mapping[qj] = qi

            for cnots in cx_sequence:
                for control, target in cnots:
                    # Apply all CNOT gates while considering the mapping of the initial state
                    circuit.cx(mapping[control], mapping[target])

        else: # W+R
            for cnots in cx_sequence:
                for control, target in cnots:
                    # Apply all CNOT gates
                    circuit.cx(control, target)

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
        initial_mapping = {i: i for i in range(circuit.num_qubits)}
        return MappingResult(circuit, initial_mapping=initial_mapping)


