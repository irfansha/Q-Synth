from pysat.card import CardEnc
from pysat.formula import CNFPlus
from qiskit import qpy

from qsynth.ReachabilitySolver.encodings.layout_synthesis.layout_reachability_utils import *
from qsynth.ReachabilitySolver.framework.reachability_encoding import ReachabilityEncoding
from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution
from qsynth.Utilities.result import MappingResult


class LayoutSynthesisReachabilityEncoding(ReachabilityEncoding):
    @classmethod
    def from_encoding_spec(cls, payload: dict):
        with open(payload["circuit_path"], "rb") as f:
            circuit = qpy.load(f)[0]
        return LayoutSynthesisReachabilityEncoding(
            circuit=circuit,
            coupling_graph=payload["coupling_graph"],
            num_pqubits=payload["num_pqubits"],
            allow_ancillas=payload["allow_ancillas"],
            upper_bound=payload["upper_bound"]
        )

    def __init__(self,
                 circuit: QuantumCircuit,
                 coupling_graph: list[list[int]],
                 num_pqubits: int,
                 allow_ancillas: bool,
                 upper_bound=None):
        super().__init__(upper_bound)
        self.circuit = circuit
        self.cnots = []

        # Map from CNOT gate index (considering only CNOT gates) to gate index (considering all gates in the circuit)
        # This is necessary for inserting back single qubit gates when decoding
        self.old_cnot_index = {}
        for i, gate in enumerate(circuit.data):
            if len(gate.qubits) == 2:
                assert gate.name == "cx", f"Can only handle binary CNOT gates, found {gate.name} gate"
                self.old_cnot_index[len(self.cnots)] = i
                ctrl, trg = [circuit.find_bit(q).index for q in gate.qubits]
                self.cnots.append((ctrl, trg))
            else:
                assert len(gate.qubits) == 1, f"Can only handle unary and binary gates"

        # Fix order for logical qubit pairs to break symmetry and reduce encoding size
        self.sorted_cnots = [(qi, qj) if qi < qj else (qj, qi) for qi, qj in self.cnots]
        self.logical_qubit_pairs = sorted(set(self.sorted_cnots))

        pre_dict, suc_dict = make_predecessor_and_successor_dictionaries(self.cnots)
        self.predecessors = pre_dict
        self.successors = suc_dict

        self.num_lqubits = circuit.num_qubits
        self.num_pqubits = num_pqubits

        self.allow_ancillas = allow_ancillas

        # We only need one of the directions in the coupling graph
        # Having pairs twice is redundant
        single_direction_cp = []
        for [p1, p2] in coupling_graph:
            if [p1, p2] not in single_direction_cp and [p2, p1] not in single_direction_cp:
                # Convention: p1 < p2
                single_direction_cp.append([p1, p2] if p1 < p2 else [p2, p1])
        self.coupling_graph = sorted(single_direction_cp)

    def get_initial_state_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        # In the initial state, no CNOT gates can be advanced (been applied in an earlier time step)
        for i in range(len(self.cnots)):
            cnf.append([-v_id(ac(i, t))])

        # At least one CNOT is mapped in the initial state
        cnf.append([v_id(mc(i, t)) for i in range(len(self.cnots))])

        # We enforce the invariants in the initial state and in every transition step
        cnf.extend(self._make_invariant_for_time(t))
        return cnf

    def get_goal_state_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        # In the goal state, no CNOT gates can be delayed (be applied at a later time step)
        for i in range(len(self.cnots)):
            cnf.append([-v_id(dc(i, t))])

        return cnf

    def get_transition_predicate_for_time(self, t):
        cnf = CNFPlus()

        cnf.extend(self._make_swap_constraints_for_time(t))
        cnf.extend(self._make_ancillary_swap_constraints_for_time(t))
        cnf.extend(self._make_cnot_propagation_constraints_for_time(t))

        # We enforce invariants for every time step by adding them to the initial state and to t+1 in every
        # transition from t to t+1.
        cnf.extend(self._make_invariant_for_time(t + 1))

        return cnf

    def get_state_variables_for_time(self, t):
        state_variables = []
        for l in range(self.num_lqubits):
            for p in range(self.num_pqubits):
                state_variables.append(m(l, p, t))

        for p in range(self.num_pqubits):
            state_variables.append(mp(p, t))
            state_variables.append(st(p, t))

        for i in range(len(self.cnots)):
            state_variables.append(ac(i, t))
            state_variables.append(dc(i, t))
            state_variables.append(mc(i, t))

        for ctrl, trg in self.logical_qubit_pairs:
            state_variables.append(lp(ctrl, trg, t))

        return state_variables

    def get_action_variables_for_time(self, t):
        action_variables = []

        # We only have swap variables as action variables. Although mc (mapped CNOT) vars also trigger state changes,
        # we need to have an extra copy of those for applying CNOTs in the last timestep.
        for p1, p2 in self.coupling_graph:
            action_variables.append(s(p1, p2, t))

        return action_variables

    def get_variable_names_for_solution_view(self):
        return ["s", "mc"]

    def _make_invariant_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        # Initial mapping constraints are asserted at every time step to reduce solving time
        for l in range(self.num_lqubits):
            # Each logical qubit maps to exactly one physical qubit
            exactly_one_physical_qubit = CardEnc.equals(lits=[v_id(m(l, p, t)) for p in range(self.num_pqubits)],
                                                        bound=1,
                                                        vpool=self.id_pool)
            cnf.extend(exactly_one_physical_qubit)

        for p in range(self.num_pqubits):
            # Each physical qubit maps to at most one logical qubit (as physical qubits may be ancillas)
            at_most_one_physical_qubit = CardEnc.atmost(lits=[v_id(m(l, p, t)) for l in range(self.num_lqubits)],
                                                        bound=1,
                                                        vpool=self.id_pool)
            cnf.extend(at_most_one_physical_qubit)

        # CNOT gates must be applied to logical qubit pairs (mapping to connected physical qubits)
        cnf.extend(self._make_cnot_connection_constraints_for_time(t))

        # CNOT dependency constraints (applying predecessors[i] before gate i and successors[i] after i)
        cnf.extend(self._make_cnot_dependency_constraints_for_time(t))

        return cnf

    def _make_swap_constraints_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        # Exactly one SWAP gate at each time step (as a SWAP gate defines the new mapping in the time step)
        exactly_one_swap = CardEnc.equals(lits=[v_id(s(p1, p2, t)) for p1, p2 in self.coupling_graph],
                                          bound=1,
                                          vpool=self.id_pool)
        cnf.extend(exactly_one_swap)

        # Exactly two physical qubits should be touched by a SWAP gate
        exactly_two_swap_touched = CardEnc.equals(lits=[v_id(st(p, t)) for p in range(self.num_pqubits)],
                                                  bound=2,
                                                  vpool=self.id_pool)
        cnf.extend(exactly_two_swap_touched)

        for p1, p2 in self.coupling_graph:
            # Handle st (swap touch) variables
            # This constraint is not bidirectional in the SAT24 paper
            # s_{p1,p2} <=> (st_p1 ∧ st_p2)
            cnf.append([-v_id(s(p1, p2, t)), v_id(st(p1, t))])
            cnf.append([-v_id(s(p1, p2, t)), v_id(st(p2, t))])
            cnf.append([-v_id(st(p1, t)), -v_id(st(p2, t)), v_id(s(p1, p2, t))])

            for l in range(self.num_lqubits):
                # Update the mapping according to the applied SWAP gate
                # NOTE: A SWAP at time t triggers a state change at time t+1
                # s_{p1,p2} => (m_{l,p1} = m'_{l,p2}) ∧ (m_{l,p2} = m'_{l,p1})
                cnf.append([-v_id(s(p1, p2, t)), v_id(m(l, p1, t)), -v_id(m(l, p2, t + 1))])
                cnf.append([-v_id(s(p1, p2, t)), -v_id(m(l, p1, t)), v_id(m(l, p2, t + 1))])
                cnf.append([-v_id(s(p1, p2, t)), v_id(m(l, p2, t)), -v_id(m(l, p1, t + 1))])
                cnf.append([-v_id(s(p1, p2, t)), -v_id(m(l, p2, t)), v_id(m(l, p1, t + 1))])

        for p in range(self.num_pqubits):
            for l in range(self.num_lqubits):
                # If a physical qubit is not touched by a SWAP gate, its mapping should propagate to time t+1
                # ¬st_p => (m_{l,p} = m'_{l,p})
                cnf.append([--v_id(st(p, t)), v_id(m(l, p, t)), -v_id(m(l, p, t + 1))])
                cnf.append([--v_id(st(p, t)), -v_id(m(l, p, t)), v_id(m(l, p, t + 1))])

        # THIS OPTIMIZATION IS NOT IN THE SAT24 PAPER
        # For unconnected physical qubit pairs p1, p2 we specify that they cannot both be touched by a SWAP gate
        # ¬(st_p1 ∧ st_p2)
        for p1 in range(self.num_pqubits):
            for p2 in range(p1 + 1, self.num_pqubits):
                if [p1, p2] not in self.coupling_graph:
                    cnf.append([-v_id(st(p1, t)), -v_id(st(p2, t))])

        return cnf

    def _make_ancillary_swap_constraints_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        for p in range(self.num_pqubits):
            # Let mp denote whether physical qubit p is mapped to some logical qubit
            # mp_p <=> (m_{1,p} v ... v m_{nl,p})
            cnf.append([-v_id(mp(p, t))] + [v_id(m(l, p, t)) for l in range(self.num_lqubits)])
            cnf.extend([[v_id(mp(p, t)), -v_id(m(l, p, t))] for l in range(self.num_lqubits)])

        for p1, p2 in self.coupling_graph:
            if self.allow_ancillas:
                # Only allow swaps where at least one of the two input qubits is mapped to a logical qubit
                # s_{p1,p2} => mp_p1 v mp_p2
                cnf.append([-v_id(s(p1, p2, t)), v_id(mp(p1, t)), v_id(mp(p2, t))])
            else:
                # No ancillas means that both physical qubits should be mapped to a logical qubit
                # s_{p1,p2} => mp_p1 ∧ mp_p2
                cnf.append([-v_id(s(p1, p2, t)), v_id(mp(p1, t))])
                cnf.append([-v_id(s(p1, p2, t)), v_id(mp(p2, t))])

        return cnf

    def _make_cnot_connection_constraints_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        for l1, l2 in self.logical_qubit_pairs:
            for p1 in range(self.num_pqubits):
                for p2 in range(p1 + 1, self.num_pqubits):
                    if [p1, p2] in self.coupling_graph:
                        # If (l1,l2) maps to connected pair (p1,p2) or (p2,p1) then (l1,l2) is a connected logical pair
                        # ((m_{l1,p1} ∧ m_{l2,p2}) v (m_{l2,p1} ∧ m_{l1,p2})) => lp_{l1,l2}
                        cnf.append([-v_id(m(l1, p1, t)), -v_id(m(l2, p2, t)), v_id(lp(l1, l2, t))])
                        cnf.append([-v_id(m(l2, p1, t)), -v_id(m(l1, p2, t)), v_id(lp(l1, l2, t))])
                    else:
                        # If (l1,l2) maps to unconnected pair (p1,p2) or (p2,p1), then (l1,l2) is an unconnected logical pair
                        # ((m_{l1,p1} ∧ m_{l2,p2}) v (m_{l2,p1} ∧ m_{l1,p2})) => ¬lp_{l1,l2}
                        cnf.append([-v_id(m(l1, p1, t)), -v_id(m(l2, p2, t)), -v_id(lp(l1, l2, t))])
                        cnf.append([-v_id(m(l2, p1, t)), -v_id(m(l1, p2, t)), -v_id(lp(l1, l2, t))])

        for i, (ctrl, trg) in enumerate(self.sorted_cnots):
            # If a gate is mapped then its control and target pair should be a connected logical qubit pair
            # mc_i => lp_{ctrl, trg}
            cnf.append([-v_id(mc(i, t)), v_id(lp(ctrl, trg, t))])

        return cnf

    def _make_cnot_dependency_constraints_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        for i in range(len(self.cnots)):
            # Every gate is either mapped (applied at this time step), delayed (applied at a later time step),
            # or advanced (applied at an earlier time step).
            mapped_delayed_or_advanced = CardEnc.equals(lits=[v_id(mc(i, t)), v_id(ac(i, t)), v_id(dc(i, t))],
                                                        bound=1,
                                                        vpool=self.id_pool)
            cnf.extend(mapped_delayed_or_advanced)

            for j in self.predecessors[i]:
                # If a gate is mapped, every predecessor should be mapped or advanced
                # mc_i => ac_j v mc_j
                cnf.append([-v_id(mc(i, t)), v_id(ac(j, t)), v_id(mc(j, t))])

            for j in self.successors[i]:
                # If a gate is mapped, every successor should be mapped or delayed
                # mc_i => dc_j v mc_j
                cnf.append([-v_id(mc(i, t)), v_id(dc(j, t)), v_id(mc(j, t))])

        for i in range(len(self.cnots)):
            for j in self.predecessors[i]:
                # If a gate is advanced, every predecessor should also be advanced
                # ac_i => ac_j
                cnf.append([-v_id(ac(i, t)), v_id(ac(j, t))])

            for j in self.successors[i]:
                # If a gate is delayed, every successor should also be delayed
                # dc_i => dc_j
                cnf.append([-v_id(dc(i, t)), v_id(dc(j, t))])

            # To limit the search space, a gate is only delayed if it cannot be applied (if its input qubits are not
            # connected or if some of its predecessors has not yet been applied).
            # dc_i => ¬lp_{D[i]} v V{dc_j for j in pre(i)}
            ctrl, trg = self.sorted_cnots[i]
            cnf.append([-v_id(dc(i, t)), -v_id(lp(ctrl, trg, t))] +
                       [v_id(dc(j, t)) for j in self.predecessors[i]])

            # Note to self: Irfanshas version of this formula is implemented as this equivalent formula:
            # dc_i ∧ {¬dc_j for j in pre(i)} => ¬lp_{D[i]}

        return cnf

    def _make_cnot_propagation_constraints_for_time(self, t):
        v_id = self.id_pool.id
        cnf = CNFPlus()

        # These constraints make sure that advanced/delayed variables propagate correctly between time steps
        # They are wrongly not bidirectional in the SAT24 paper
        for i in range(len(self.cnots)):
            # A gate is advanced if and only if it was advanced or mapped at the previous time step
            # ac'_i <=> (mc_i v ac_i)
            cnf.append([-v_id(ac(i, t + 1)), v_id(mc(i, t)), v_id(ac(i, t))])
            cnf.append([-v_id(mc(i, t)), v_id(ac(i, t + 1))])
            cnf.append([-v_id(ac(i, t)), v_id(ac(i, t + 1))])

            # A gate is delayed if and only if it is delayed or mapped at the next time step
            # dc_i <=> mc'_i v dc'_i
            cnf.append([-v_id(dc(i, t)), v_id(mc(i, t + 1)), v_id(dc(i, t + 1))])
            cnf.append([-v_id(mc(i, t + 1)), v_id(dc(i, t))])
            cnf.append([-v_id(dc(i, t + 1)), v_id(dc(i, t))])

        return cnf

    def decode_reachability_solution(self, reachability_solution: ReachabilitySolution):
        l_to_p_mapping, p_to_l_mapping = get_initial_mapping(
            reachability_solution.initial_state,
            self.num_lqubits,
            self.num_pqubits
        )
        initial_mapping = l_to_p_mapping.copy()
        # The CNOT sequence denotes for each time step which set of CNOT gates is applied
        # The SWAP sequence denotes for each time step which SWAP gate is applied
        cnot_sequence, swap_sequence = get_cnot_and_swap_sequence(reachability_solution.action_sequence)

        new_circuit = QuantumCircuit(self.num_pqubits)
        predecessors = make_predecessor_dict_for_all_gates(self.circuit)
        applied_gates = set()

        for t in range(len(cnot_sequence)):
            # Apply all CNOTs for this time step in sorted order (this preserves dependencies)
            for i in sorted(cnot_sequence[t]):
                ctrl, trg = self.cnots[i]

                # Be sure to apply all necessary single qubit gates first
                # We know that all unapplied predecessors are single qubit gates
                for gate_index in predecessors[self.old_cnot_index[i]]:
                    if gate_index not in applied_gates:
                        self._map_and_apply_single_qubit_gate_to_circuit(gate_index, l_to_p_mapping, new_circuit)
                        applied_gates.add(gate_index)

                # Apply CNOT gate according to the mapping from logical to physical qubits
                new_circuit.cx(l_to_p_mapping[ctrl], l_to_p_mapping[trg])
                applied_gates.add(self.old_cnot_index[i])

            # No SWAP is applied at the last time step
            if t == len(cnot_sequence) - 1:
                continue
            # Apply swap to new circuit
            p1, p2 = swap_sequence[t]
            new_circuit.swap(p1, p2)
            # Update mappings accordingly
            swap_mapping(p1, p2, l_to_p_mapping, p_to_l_mapping)

        # Apply remaining single qubit gates
        for gate_index in range(len(self.circuit.data)):
            if gate_index not in applied_gates:
                self._map_and_apply_single_qubit_gate_to_circuit(gate_index, l_to_p_mapping, new_circuit)

        # Count number of swaps
        no_swaps = new_circuit.count_ops().get("swap", 0)

        return MappingResult(circuit=new_circuit,
                             initial_mapping=initial_mapping,
                             final_mapping=l_to_p_mapping)

    def _map_and_apply_single_qubit_gate_to_circuit(self, gate_index, qubit_mapping: dict[int, int],
                                                    new_circuit: QuantumCircuit):
        """
        Look up the single qubit gate with index gate_index and append the gate to new_circuit while updating the
        qubit index according to qubit_mapping.
        Args:
            gate_index: The index of the gate in the original circuit.
            qubit_mapping: Python dict mapping old qubit indices to new qubit indices.
            new_circuit: The new circuit to append the gate to.
        """
        gate = self.circuit.data[gate_index]
        assert len(gate.qubits) == 1
        old_qubit_index = self.circuit.find_bit(gate.qubits[0]).index
        new_qubit_index = qubit_mapping[old_qubit_index]
        new_circuit.append(gate.operation, [new_qubit_index], gate.clbits)


