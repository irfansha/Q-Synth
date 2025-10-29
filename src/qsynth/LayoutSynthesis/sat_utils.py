# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from qsynth.LayoutSynthesis.circuit_utils import (
    strict_dependencies,
    relaxed_dependencies,
    cancel_cnots,
    all_cx_gates,
    gate_get_qubit,
)
from qsynth.LayoutSynthesis.architecture import platform

from pysat.card import *
import time

########################################################################################
# Helper functions:
########################################################################################


def AtmostOne_constraints(self, vars):
    cnf = CardEnc.atmost(
        lits=vars, top_id=self.new_vars.next_var - 1, encoding=self.args.cardinality
    )
    if cnf.nv + 1 > self.new_vars.next_var:
        self.new_vars.set_next_var(cnf.nv + 1)
    if self.args.verbose > 2:
        print("Atmost One for ", vars)
    self.clause_list.extend(cnf.clauses)


def AtleastOne_constraints(self, vars):
    cnf = CardEnc.atleast(
        lits=vars, top_id=self.new_vars.next_var - 1, encoding=self.args.cardinality
    )
    if cnf.nv + 1 > self.new_vars.next_var:
        self.new_vars.set_next_var(cnf.nv + 1)
    if self.args.verbose > 2:
        print("Atleast One for ", vars)
    self.clause_list.extend(cnf.clauses)


def ExactlyOne_constraints(self, vars):
    cnf = CardEnc.equals(
        lits=vars, top_id=self.new_vars.next_var - 1, encoding=self.args.cardinality
    )
    if cnf.nv + 1 > self.new_vars.next_var:
        self.new_vars.set_next_var(cnf.nv + 1)
    if self.args.verbose > 2:
        print("Exactly One for ", vars)
    self.clause_list.extend(cnf.clauses)


def ExactlyTwo_constraints(self, vars):
    cnf = CardEnc.equals(
        lits=vars,
        top_id=self.new_vars.next_var - 1,
        encoding=self.args.cardinality,
        bound=2,
    )
    if cnf.nv + 1 > self.new_vars.next_var:
        self.new_vars.set_next_var(cnf.nv + 1)
    if self.args.verbose > 2:
        print("Exactly Two for ", vars)
    self.clause_list.extend(cnf.clauses)


def AtmostTwo_constraints(self, vars):
    cnf = CardEnc.atmost(
        lits=vars,
        top_id=self.new_vars.next_var - 1,
        encoding=self.args.cardinality,
        bound=2,
    )
    if cnf.nv + 1 > self.new_vars.next_var:
        self.new_vars.set_next_var(cnf.nv + 1)
    if self.args.verbose > 2:
        print("Atmost Two for ", vars)
    self.clause_list.extend(cnf.clauses)


def single_direction(in_pair, dict):
    # we extract the pair that exists:
    (p1, p2) = in_pair
    if (p1, p2) in dict:
        out_pair = (p1, p2)
    else:
        out_pair = (p2, p1)
    return out_pair


def unit_clause(self, var):
    self.clause_list.append([var])


# single clause:
def or_clause(self, clause):
    self.clause_list.append(clause)


# single implication with the then list:
def if_then_clause(self, if_var, then_list):
    implication_clause = [-if_var]
    implication_clause.extend(then_list)
    self.clause_list.append(implication_clause)


# assumes if_vars are from conjunction clause:
def if_and_then_clause(self, if_vars, then_list):
    if_clause = []
    for var in if_vars:
        if_clause.append(-var)
    if_clause.extend(then_list)
    self.clause_list.append(if_clause)


# assumes if_vars are from conjunction clauses:
def if_and_then_equal_clauses(self, if_vars, x1, x2):
    if_and_then_clause(self, if_vars, [-x1, x2])
    if_and_then_clause(self, if_vars, [x1, -x2])


# single implication with the then list and
# for each item in list, if apply reverse implication
def iff_clauses(self, if_var, then_list):
    if_then_clause(self, if_var, then_list)
    for var in then_list:
        self.clause_list.append([-var, if_var])


# one clause for each variable in the then_list:
def if_then_each_clause(self, if_var, then_list):
    for var in then_list:
        self.clause_list.append([-if_var, var])


def iff_then_each_clause(self, if_var, then_list):
    if_then_each_clause(self, if_var, then_list)
    temp_clause = [if_var]
    for var in then_list:
        temp_clause.append(-var)
    self.clause_list.append(temp_clause)


# one clause for each negated variable in the then_list:
def if_then_each_not_clause(self, if_var, then_list):
    for var in then_list:
        self.clause_list.append([-if_var, -var])


########################################################################################
# Parser and dependency functions:
########################################################################################


def compute_predecessors_successors(self):
    self.cx_dict = {}
    self.lq_pair_list = []
    self.cx_predecessors = {}
    self.cx_successors = {}

    for gate_index in range(len(self.logical_circuit)):
        gate = self.logical_circuit[gate_index]
        if len(gate.qubits) == 2:
            # for now asserting every 2 qubit operation is "cx":
            assert gate.operation.name == "cx"
            ctrl = gate.qubits[0]._index
            data = gate.qubits[1]._index
            # getting qubit pairs:
            # assuming bidirectional for coupling graph:
            if (ctrl, data) not in self.lq_pair_list and (
                data,
                ctrl,
            ) not in self.lq_pair_list:
                self.lq_pair_list.append((ctrl, data))
            self.cx_dict[gate_index] = (ctrl, data)
            # get dependencies from dictionary:
            (ctrl_dep, data_dep) = self.cnot_depends[gate_index]
            assert gate_index not in self.cx_predecessors
            # adding successors and predecessors for control qubit:
            for single_ctrl_dep in ctrl_dep:
                self.cx_predecessors[gate_index] = [single_ctrl_dep]
                if single_ctrl_dep not in self.cx_successors:
                    self.cx_successors[single_ctrl_dep] = [gate_index]
                elif gate_index not in self.cx_successors[single_ctrl_dep]:
                    self.cx_successors[single_ctrl_dep].append(gate_index)
            # adding successors and predecessors for data qubit:
            for single_data_dep in data_dep:
                if gate_index not in self.cx_predecessors:
                    self.cx_predecessors[gate_index] = [single_data_dep]
                elif single_data_dep not in self.cx_predecessors[gate_index]:
                    self.cx_predecessors[gate_index].append(single_data_dep)

                if single_data_dep not in self.cx_successors:
                    self.cx_successors[single_data_dep] = [gate_index]
                elif gate_index not in self.cx_successors[single_data_dep]:
                    self.cx_successors[single_data_dep].append(gate_index)


# Parse and compute cnot gate list with dependencies satisfied:
def parse_and_compute(self):
    # circuit is given in quantum circuit format:
    self.input_circuit = self.args.circuit_in
    self.logical_circuit = self.input_circuit.copy()
    self.num_lqubits = len(self.input_circuit.qubits)
    if self.args.verbose > 0:
        print(self.input_circuit)

    # cancel CNOTS
    if self.args.cnot_cancel == 1:
        deps = relaxed_dependencies(self.logical_circuit, verbose=self.args.verbose)
        self.logical_circuit = cancel_cnots(
            self.logical_circuit, deps, verbose=self.args.verbose
        )

    # extracting CNOT gates and computing dependencies
    if self.args.relaxed == 0:
        self.cnot_depends = strict_dependencies(
            self.logical_circuit, verbose=self.args.verbose
        )
    else:
        self.cnot_depends = relaxed_dependencies(
            self.logical_circuit, verbose=self.args.verbose
        )

    self.list_cx_gates = all_cx_gates(self.logical_circuit)
    compute_predecessors_successors(self)

    # for easy access of cnot gates positions, we generate a dict:
    self.cnot_dict = {}
    for i in range(len(self.list_cx_gates)):
        cx_gate = self.list_cx_gates[i]
        self.cnot_dict[cx_gate] = i

    if self.args.verbose > 2:
        print("cnot gates: ", self.list_cx_gates)
        print("cnot position dict: ", self.cnot_dict)
        print("cnot to logical pair dict: ", self.cx_dict)
        print("cnot_depends dict:")
        for key, value in self.cnot_depends.items():
            print(key, value)
        print("cnot predecessors:")
        print(self.cx_predecessors)
        print("logical qubit pairs:")
        print(self.lq_pair_list)


def set_architecture(self):

    # edge list is injected from args
    (
        self.coupling_map,
        self.bi_coupling_map,
        self.bridge_bicoupling_map,
        self.bridge_middle_pqubit_dict,
        self.reverse_swap_distance_dict,
        self.num_pqubits,
    ) = platform(
        self.args.platform,
        self.args.bidirectional,
        self.args.coupling_graph,
        self.args.verbose,
    )

    self.scoupling = []
    # for swapping, we only need one of the directions in coupling:
    for [x1, x2] in self.coupling_map:
        if ([x1, x2] not in self.scoupling) and ([x2, x1] not in self.scoupling):
            self.scoupling.append([x1, x2])

    # sorting coupling maps for consistency:
    for coupling in self.bi_coupling_map:
        coupling = sorted(coupling)
    self.bi_coupling_map = sorted(self.bi_coupling_map)
    for coupling in self.scoupling:
        coupling = sorted(coupling)
    self.scoupling = sorted(self.scoupling)

    # finding longest swaps neeeded in the coupling graph:
    self.max_swap_distance = max(k for k, v in self.reverse_swap_distance_dict.items())

    if self.args.verbose > 1:
        print("single directional coupling map: ", self.scoupling)
        print("max swaps to connect any two physical qubits: ", self.max_swap_distance)


########################################################################################
# Core constraint functions:
########################################################################################


def extract_physical_qubit_slices(self, mapping_vars):
    horizontal_slice = []
    for i in range(self.num_pqubits):
        cur_list = []
        for j in range(self.num_lqubits):
            cur_list.append(mapping_vars[j][i])
        horizontal_slice.append(cur_list)
    return horizontal_slice


def initialize_ancillary_clauses(self, cur_mpvars):
    # for anciliary and non-anciliary swaps, we need to know if the physical qubits are mapped
    # we use mapped pvars to specify that:
    self.cur_sb.mapped_pvars = self.new_vars.get_vars(self.num_pqubits)

    # we need to update the status of mapped pvars based on the mapped physical qubits:
    # if one of the physical qubit is mapped then the mapped_pvar is true:
    for vars_id in range(len(cur_mpvars)):
        vars = cur_mpvars[vars_id]
        mapped_pvar = self.cur_sb.mapped_pvars[vars_id]
        iff_clauses(self, mapped_pvar, vars)

    # If initial mapping is specified and ancillary qubits are not allowed, we disable the uninitialized physical qubits in all time steps:
    if self.args.initial_mapping is not None and self.args.allow_ancillas == False:
        # We disable the mapped_pvars for the given physical qubits not in initial mapping:
        for pqubit in range(self.num_pqubits):
            if pqubit not in self.args.initial_mapping.values():
                # if pqubit is not in initial mapping, then mapped_pvar must be false:
                unit_clause(self, -self.cur_sb.mapped_pvars[pqubit])
            else:
                # if pqubit is in initial mapping, then mapped_pvar must be true:
                unit_clause(self, self.cur_sb.mapped_pvars[pqubit])


def ancillary_constraints(self, tstep):
    # now we need to handle if the ancilliary swap can be used or not:
    for swap_ind in range(len(self.cur_sb.swaps)):
        cur_swap_var = self.cur_sb.swaps[swap_ind]
        # depending on the swap var index, we first get the swapping physical qubits var indexes:
        p1_index, p2_index = self.scoupling[swap_ind]
        mapped_p1var = self.blocks[tstep - 1].mapped_pvars[p1_index]
        mapped_p2var = self.blocks[tstep - 1].mapped_pvars[p2_index]
        if self.args.allow_ancillas:
            # if ancillary can be used, then atleast one of the qubits must be mapped:
            # swap_pair(p1,p2) -> (mapped_pvar(p1) V mapped_pvar(p2))
            if_then_clause(self, cur_swap_var, [mapped_p1var, mapped_p2var])
        else:
            # swap_pair(p1,p2) -> (mapped_pvar(p1) & mapped_pvar(p2))
            if_then_each_clause(self, cur_swap_var, [mapped_p1var, mapped_p2var])


def swapp_exclusion_constraints(self):
    # in the physical swap auxiliary variables, we exclude the combinations of physical qubit that are not connected:
    for k, pairs in self.reverse_swap_distance_dict.items():
        if k != 0:
            for p1, p2 in pairs:
                p1_var, p2_var = self.cur_sb.swaps_p[p1], self.cur_sb.swaps_p[p2]
                # if p1_var is true, then p2_var is false:
                if_then_clause(self, p1_var, [-p2_var])


# instead of auxiliary variables, we give clauses directly for connectivity:
def lqubit_distance_constraints(self):
    for lq_ind in range(len(self.lq_pair_list)):
        l1, l2 = self.lq_pair_list[lq_ind]
        lq_var = self.cur_sb.lq_pairs[lq_ind]
        for key in self.reverse_swap_distance_dict.keys():
            if key == 0:
                cur_lq_var = lq_var
            else:
                cur_lq_var = -lq_var
            for p1, p2 in self.reverse_swap_distance_dict[key]:
                # print(l1,l2,p1,p2)
                # if l1 and l2 are mapped to distance p1, p2 then lq_pair var with (l1,l2) be always true/false:
                add_mapping_distance_var_clauses(self, l1, l2, p1, p2, cur_lq_var)


# instead of auxiliary variables, we give clauses directly for connectivity:
def lqubit_bridge_distance_constraints(self, tstep):
    for lq_ind in range(len(self.lq_pair_list)):
        l1, l2 = self.lq_pair_list[lq_ind]
        blq_var = self.cur_sb.bridge_lq_pairs[lq_ind]
        for key in self.reverse_swap_distance_dict.keys():
            if key == 1:
                cur_blq_var = blq_var
            else:
                cur_blq_var = -blq_var
            for p1, p2 in self.reverse_swap_distance_dict[key]:
                # print(l1,l2,p1,p2)
                # if l1 and l2 are mapped to distance p1, p2 then lq_pair var with (l1,l2) be always true/false:
                add_mapping_distance_var_clauses(self, l1, l2, p1, p2, cur_blq_var)


# implies var is (l1,l2) are mapped to (p1,p2), or if (l1,l2) to (p2,p1):
def add_mapping_distance_var_clauses(self, l1, l2, p1, p2, var):
    if_and_then_clause(
        self, [self.cur_sb.mlvars[l1][p1], self.cur_sb.mlvars[l2][p2]], [var]
    )
    if_and_then_clause(
        self, [self.cur_sb.mlvars[l1][p2], self.cur_sb.mlvars[l2][p1]], [var]
    )


# implies var is (l1,l2) are mapped to (p1,p2), or if (l1,l2) to (p2,p1):
def add_mapping_distance_var_t_clauses(self, l1, l2, p1, p2, var, t):
    if_and_then_clause(
        self, [self.blocks[t].mlvars[l1][p1], self.blocks[t].mlvars[l2][p2]], [var]
    )
    if_and_then_clause(
        self, [self.blocks[t].mlvars[l1][p2], self.blocks[t].mlvars[l2][p1]], [var]
    )


def twoway_constraints(self, tstep):
    # print(self.list_cx_gates)
    # print(self.cx_predecessors)
    # print(self.cx_successors)
    for cnot_ind in range(len(self.list_cx_gates)):
        cnot = self.list_cx_gates[cnot_ind]
        predlist_cnot_var, cur_cnot_var, succlist_cnot_var = (
            self.cur_sb.pred_cnot_var_dict[cnot],
            self.cur_sb.cnot_var_dict[cnot],
            self.cur_sb.succ_cnot_var_dict[cnot],
        )
        # print(cnot,predlist_cnot_var, cur_cnot_var, succlist_cnot_var)
        # ExactlyOne constraints on P,C,S vars for each cnot:
        # every cnot must be true either in the same block or before or after:
        ExactlyOne_constraints(
            self, [predlist_cnot_var, cur_cnot_var, succlist_cnot_var]
        )

        # predecessor constraints:

        # if tstep 0 then the predecessor list must be all zero:
        if tstep == 0:
            unit_clause(self, -predlist_cnot_var)

        # if c is true, then each of its predecessor must be true in either same block
        # or in the predecessor list, which implies in some previous block:
        if cnot in self.cx_predecessors:
            # print(cnot,self.cx_predecessors[cnot])
            for pred_cnot in self.cx_predecessors[cnot]:
                predlist_predcnot_var = self.cur_sb.pred_cnot_var_dict[pred_cnot]
                cur_predcnot_var = self.cur_sb.cnot_var_dict[pred_cnot]
                # print(cur_cnot_var, predlist_predcnot_var, cur_predcnot_var)
                if_then_clause(
                    self, cur_cnot_var, [cur_predcnot_var, predlist_predcnot_var]
                )

        # if p is true, then its own predecessors in the predecessor list are true within the same block:
        if cnot in self.cx_predecessors:
            # print(cnot,self.cx_predecessors[cnot])
            for pred_cnot in self.cx_predecessors[cnot]:
                predlist_predcnot_var = self.cur_sb.pred_cnot_var_dict[pred_cnot]
                # print(predlist_predcnot_var)
                if_then_clause(self, predlist_cnot_var, [predlist_predcnot_var])

        #   interblock predecessor constraints:
        #   any p can only be true, iff it is true in previous predecessor list or previous cur cnot list:
        if tstep > 0:
            previous_predlist_cnot_var = self.blocks[tstep - 1].pred_cnot_var_dict[cnot]
            previous_cnot_var = self.blocks[tstep - 1].cnot_var_dict[cnot]
            # print(previous_predlist_cnot_var,previous_cnot_var)
            if_then_clause(
                self, predlist_cnot_var, [previous_predlist_cnot_var, previous_cnot_var]
            )
            if_then_clause(self, previous_predlist_cnot_var, [predlist_cnot_var])
            if_then_clause(self, previous_cnot_var, [predlist_cnot_var])

        # sucessor constraints:

        # last time step needs sucessor list to be all zero, but we add them as assumptions:

        # if c is true, then each of its successor must be true in either same block
        # or in the successor list, which implies in some later block:
        if cnot in self.cx_successors:
            # print(cnot,self.cx_successors[cnot])
            for succ_cnot in self.cx_successors[cnot]:
                succlist_succnot_var = self.cur_sb.succ_cnot_var_dict[succ_cnot]
                cur_succnot_var = self.cur_sb.cnot_var_dict[succ_cnot]
                # print(cur_cnot_var, succlist_succnot_var, cur_succnot_var)
                if_then_clause(
                    self, cur_cnot_var, [succlist_succnot_var, cur_succnot_var]
                )

        # if s is true, then its own sucessors must be true in the successor list within the same block:
        if cnot in self.cx_successors:
            # print(cnot,self.cx_successors[cnot])
            for succ_cnot in self.cx_successors[cnot]:
                succlist_succcnot_var = self.cur_sb.succ_cnot_var_dict[succ_cnot]
                # print(succlist_succcnot_var)
                if_then_clause(self, succlist_cnot_var, [succlist_succcnot_var])

        #   interblock successor constraints:
        #   any s can only be true, iff it is true in next successor list or next cur cnot list:
        # since we do incremental, previous timestep successor cnot is true iff current cnot is true or current successor is true:
        if tstep > 0:
            previous_succcnot_var = self.blocks[tstep - 1].succ_cnot_var_dict[cnot]
            # print(previous_succcnot_var,cur_cnot_var, succlist_cnot_var)
            if_then_clause(
                self, previous_succcnot_var, [cur_cnot_var, succlist_cnot_var]
            )
            if_then_clause(self, cur_cnot_var, [previous_succcnot_var])
            if_then_clause(self, succlist_cnot_var, [previous_succcnot_var])

        # pushing all the cnots to top whenever possible:
        # if a cnots predecessors are not postponed, then cnot cannot be postponed unless logical qubit pair is not connected:
        if cnot in self.cx_predecessors:
            # print(cnot,self.cx_predecessors[cnot])
            if_cond_list = []
            for pred_cnot in self.cx_predecessors[cnot]:
                # not in the successor list means the predecessor is not postponed:
                if_cond_list.append(-self.cur_sb.succ_cnot_var_dict[pred_cnot])
            # if current cnot is postponed:
            if_cond_list.append(succlist_cnot_var)
            # implies that the logical qubit pair is not connected:
            qubit_pair = single_direction(self.cx_dict[cnot], self.cur_sb.lq_pair_dict)
            if_and_then_clause(
                self, if_cond_list, [-self.cur_sb.lq_pair_dict[qubit_pair]]
            )


def ALO_twoway_cnot_constraints(self, tstep):

    # if tstep is 0, then one of the cnots is true:
    if tstep == 0 and len(self.cur_sb.cnot_vars) > 0:
        AtleastOne_constraints(self, self.cur_sb.cnot_vars)

    # if assumption var is true, then all the successor vars are false:
    if_then_each_not_clause(self, self.cur_sb.cnot_ass_var, self.cur_sb.succ_cnot_vars)

    # previous cnot assumption var must be false in forward search strategy:
    if tstep > 0 and self.args.search_strategy == "forward":
        unit_clause(self, -self.blocks[tstep - 1].cnot_ass_var)


def disable_swaps(self, sat_solver, tstep):
    # If the Time step is disabled. Then we disable all the swap variables in the backward search:
    assert self.args.search_strategy == "backward"
    self.tsteps_swap_disabled = []
    for i in range(tstep, self.args.start + 1):
        # If swaps are not disabled due to jumping, we disable them now.
        if i in self.tsteps_swap_disabled:
            continue
        for swap_var in self.blocks[i].swaps:
            sat_solver.add_clause([-swap_var])
        for swapp_var in self.blocks[i].swaps_p:
            sat_solver.add_clause([-swapp_var])
        self.tsteps_swap_disabled.append(i)


def cnot_to_lqubitpair_constraints(self):
    # for each cnot gate, we imply if the cnot is true then the corresponding logical qubit pair is connected:
    for i in range(len(self.list_cx_gates)):
        qubit_pair = single_direction(
            self.cx_dict[self.list_cx_gates[i]], self.cur_sb.lq_pair_dict
        )
        if_then_clause(
            self, self.cur_sb.cnot_vars[i], [self.cur_sb.lq_pair_dict[qubit_pair]]
        )


# for time step zero, We fix the physical qubits for given logical qubit mapping:
def set_initial_mapping(self):
    # loop through logical physical initial mapping:
    for logical_qubit, physical_qubit in self.args.initial_mapping.items():
        # Unit clause for the mapped physical qubit:
        unit_clause(self, self.cur_sb.mpvars[physical_qubit][logical_qubit])
