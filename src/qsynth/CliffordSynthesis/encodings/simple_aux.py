# Irfansha Shaik, 02.10.2024, Aarhus
from qsynth.CnotSynthesis.circuit_utils.constraints import Constraints
from qsynth.CnotSynthesis.circuit_utils.variables_dispatcher import VarDispatcher
from pysat.card import *


class SimpleAux:
    def print_clause_tofile(self, clause, f):
        f.write(" ".join(str(x) for x in clause) + " 0\n")

    def print_encoding_tofile(self, file_path):
        f = open(file_path, "w")
        for qblock in self.quantifier_block:
            f.write(qblock + "\n")
        for clause in self.clause_list:
            self.print_clause_tofile(clause, f)

    # Generates quanifier blocks:
    def generate_quantifier_blocks(self):
        # Header:
        self.quantifier_block.append(
            "p cnf "
            + str(self.encoding_variables.next_var - 1)
            + " "
            + str(len(self.clause_list))
        )

    def apply_igate_constraints(self, var, column_id, time_step):
        # ----------------------
        # I gate:
        # ----------------------
        # x_i = x_i and z_i = z_i
        # Forall rows, we add the x_cell and z_cells update clauses:
        # we propagate x and z:
        for row_id in range(self.num_rows):
            self.constraints.if_then_each_clause(
                var,
                [
                    self.prop_xvars[time_step][row_id][column_id],
                    self.prop_zvars[time_step][row_id][column_id],
                ],
            )

    def apply_hgate_constraints(self, var, column_id, time_step):
        # ----------------------
        # H gate:
        # ----------------------
        # x_i = z_i and z_i = x_i
        # Forall rows, we add the x_cell and z_cells update clauses:
        for row_id in range(self.num_rows):
            self.constraints.if_and_then_equal_clauses(
                [var],
                self.x_cells[time_step][row_id][column_id],
                self.z_cells[time_step + 1][row_id][column_id],
            )
            self.constraints.if_and_then_equal_clauses(
                [var],
                self.z_cells[time_step][row_id][column_id],
                self.x_cells[time_step + 1][row_id][column_id],
            )

    def apply_sgate_constraints(self, var, column_id, time_step):
        # ----------------------
        # S gate:
        # ----------------------
        # x_i = x_i and z_i = x_i + z_i
        # Forall rows, we add the x_cell and z_cells update clauses:
        for row_id in range(self.num_rows):
            self.constraints.if_then_clause(
                var, [self.prop_xvars[time_step][row_id][column_id]]
            )
            self.constraints.if_and_then_clause(
                [var, self.x_cells[time_step][row_id][column_id]],
                [self.flip_zvars[time_step][row_id][column_id]],
            )
            self.constraints.if_and_then_clause(
                [var, -self.x_cells[time_step][row_id][column_id]],
                [self.prop_zvars[time_step][row_id][column_id]],
            )

    def apply_hsgate_constraints(self, var, column_id, time_step):
        # ----------------------
        # HS gate:
        # ----------------------
        # x_i = z_i and z_i = x_i + z_i
        # Forall rows, we add the x_cell and z_cells update clauses:
        for row_id in range(self.num_rows):
            self.constraints.if_and_then_equal_clauses(
                [var],
                self.z_cells[time_step][row_id][column_id],
                self.x_cells[time_step + 1][row_id][column_id],
            )
            self.constraints.if_and_then_clause(
                [var, self.x_cells[time_step][row_id][column_id]],
                [self.flip_zvars[time_step][row_id][column_id]],
            )
            self.constraints.if_and_then_clause(
                [var, -self.x_cells[time_step][row_id][column_id]],
                [self.prop_zvars[time_step][row_id][column_id]],
            )

    def apply_shgate_constraints(self, var, column_id, time_step):
        # ----------------------
        # SH gate:
        # ----------------------
        # x_i = x_i + z_i and z_i = x_i
        # Forall rows, we add the x_cell and z_cells update clauses:
        for row_id in range(self.num_rows):
            self.constraints.if_and_then_clause(
                [var, self.z_cells[time_step][row_id][column_id]],
                [self.flip_xvars[time_step][row_id][column_id]],
            )
            self.constraints.if_and_then_clause(
                [var, -self.z_cells[time_step][row_id][column_id]],
                [self.prop_xvars[time_step][row_id][column_id]],
            )
            self.constraints.if_and_then_equal_clauses(
                [var],
                self.x_cells[time_step][row_id][column_id],
                self.z_cells[time_step + 1][row_id][column_id],
            )

    def apply_hshgate_constraints(self, var, column_id, time_step):
        # ----------------------
        # HSH gate:
        # ----------------------
        # x_i = x_i + z_i and z_i = z_i
        # Forall rows, we add the x_cell and z_cells update clauses:
        for row_id in range(self.num_rows):
            self.constraints.if_and_then_clause(
                [var, self.z_cells[time_step][row_id][column_id]],
                [self.flip_xvars[time_step][row_id][column_id]],
            )
            self.constraints.if_and_then_clause(
                [var, -self.z_cells[time_step][row_id][column_id]],
                [self.prop_xvars[time_step][row_id][column_id]],
            )
            self.constraints.if_then_clause(
                var, [self.prop_zvars[time_step][row_id][column_id]]
            )

    def auxilary_flip_propagate_constraints(self):
        for time_step in range(2 * self.options.plan_length + 1):
            # clauses for flipping and propagation:
            for column_id in range(self.num_qubits):
                for row_id in range(self.num_rows):
                    self.constraints.if_and_then_equal_clauses(
                        [self.prop_xvars[time_step][row_id][column_id]],
                        self.x_cells[time_step][row_id][column_id],
                        self.x_cells[time_step + 1][row_id][column_id],
                    )
                    self.constraints.if_and_then_notequal_clauses(
                        [self.flip_xvars[time_step][row_id][column_id]],
                        self.x_cells[time_step][row_id][column_id],
                        self.x_cells[time_step + 1][row_id][column_id],
                    )
                    self.constraints.if_and_then_notequal_clauses(
                        [],
                        self.prop_xvars[time_step][row_id][column_id],
                        self.flip_xvars[time_step][row_id][column_id],
                    )

                    self.constraints.if_and_then_equal_clauses(
                        [self.prop_zvars[time_step][row_id][column_id]],
                        self.z_cells[time_step][row_id][column_id],
                        self.z_cells[time_step + 1][row_id][column_id],
                    )
                    self.constraints.if_and_then_notequal_clauses(
                        [self.flip_zvars[time_step][row_id][column_id]],
                        self.z_cells[time_step][row_id][column_id],
                        self.z_cells[time_step + 1][row_id][column_id],
                    )
                    self.constraints.if_and_then_notequal_clauses(
                        [],
                        self.prop_zvars[time_step][row_id][column_id],
                        self.flip_zvars[time_step][row_id][column_id],
                    )

    def single_gate_constraints(self, layer_id):
        # we apply single gates in timestep=2*layer_id:
        time_step = 2 * layer_id
        if self.options.verbose > 2:
            print(
                f"single gate constraints, layer id: {layer_id}, timestep: {time_step}"
            )

        for column_id in range(self.num_qubits):
            # Exactly one of the control and target single qubit vars is true:
            self.constraints.ExactlyOne_constraints(
                self.single_qvars[layer_id][column_id]
            )

        # If not the chosen qubits, we apply identity gate by default:
        for column_id in range(self.num_qubits):
            control_var = self.control_qvars[layer_id][column_id]
            target_var = self.target_qvars[layer_id][column_id]
            i_gvar = self.single_qvars[layer_id][column_id][0]
            self.constraints.if_and_then_clause([-control_var, -target_var], [i_gvar])

        # If not an I gate, then the qubit be control or target qubit:
        for column_id in range(self.num_qubits):
            control_var = self.control_qvars[layer_id][column_id]
            target_var = self.target_qvars[layer_id][column_id]
            hs_gvar = self.single_qvars[layer_id][column_id][1]
            sh_gvar = self.single_qvars[layer_id][column_id][2]
            self.constraints.if_then_clause(hs_gvar, [control_var, target_var])
            self.constraints.if_then_clause(sh_gvar, [control_var, target_var])

        for column_id in range(self.num_qubits):
            [i_gvar, hs_gvar, sh_gvar] = self.single_qvars[layer_id][column_id]
            self.apply_igate_constraints(i_gvar, column_id, time_step)
            # we only apply other gates if qubit is not disabled:
            self.apply_hsgate_constraints(hs_gvar, column_id, time_step)
            self.apply_shgate_constraints(sh_gvar, column_id, time_step)

    def cnot_constraints(self, layer_id):
        # we apply cnot gate in timestep=2*layer_id+1:
        time_step = (2 * layer_id) + 1
        if self.options.verbose > 2:
            print(f"cnot constraints, layer id: {layer_id}, timestep: {time_step}")

        if layer_id >= 1 and self.options.gate_ordering:
            self.gate_ordering(layer_id)

        # gathering all cnot vars for the current layer:
        all_cnotvars = []
        for vars in self.cnot_qvars[layer_id]:
            all_cnotvars.extend(vars)

        # we fix the depth of the circuit if the optimal search is not backwards or if we are minimizing local CNOT count:
        if self.options.search_strategy != "backward":
            # Atleast one of the control and target vars is true if not backward search:
            self.constraints.AtleastOne_constraints(self.control_qvars[layer_id])
            self.constraints.AtleastOne_constraints(self.target_qvars[layer_id])
            # Atleast one of the cnot vars is true if not backward search:
            self.constraints.AtleastOne_constraints(all_cnotvars)
        else:
            # if backward search is true, then we only all control and target qubit if the indicator is true:
            self.constraints.iff_clauses(
                self.indicator_vars[layer_id], self.control_qvars[layer_id]
            )
            self.constraints.iff_clauses(
                self.indicator_vars[layer_id], self.target_qvars[layer_id]
            )
            # if backward search is true, then we cnot var is true only if the indicator is true:
            self.constraints.iff_clauses(self.indicator_vars[layer_id], all_cnotvars)

        # if a control var is true then it cannot be target var:
        for qid in range(self.num_qubits):
            self.constraints.AtmostOne_constraints(
                [
                    self.control_qvars[layer_id][qid],
                    self.target_qvars[layer_id][qid],
                ]
            )

        if self.options.minimization == "cx-count":
            # Atmost one of the control and target vars, cnot vars is true:
            self.constraints.AtmostOne_constraints(self.control_qvars[layer_id])
            self.constraints.AtmostOne_constraints(self.target_qvars[layer_id])
            self.constraints.AtmostOne_constraints(all_cnotvars)
        else:
            assert (
                self.options.minimization == "cx-depth"
                or self.options.minimization == "bounded_cx-depth_local_cx-count"
                or self.options.minimization == "bounded_cx-count_local_cx-depth"
            )
            for i in range(self.num_qubits):
                # gather all cnot vars with i as control qubit:
                cur_control_cnot_vars = self.cnot_qvars[layer_id][i]
                # gather all cnot vars with i as target qubit:
                cur_target_cnot_vars = self.cnot_vars_target_slices[layer_id][i]
                cur_all_cnot_vars = []
                cur_all_cnot_vars.extend(cur_control_cnot_vars)
                cur_all_cnot_vars.extend(cur_target_cnot_vars)
                # removing any duplicates:
                cur_all_cnot_vars = list(set(cur_all_cnot_vars))
                self.constraints.AtmostOne_constraints(cur_all_cnot_vars)
                control_var = self.control_qvars[layer_id][i]
                target_var = self.target_qvars[layer_id][i]
                # if we set any control then one of the cur_control_cnot_vars must be true:
                self.constraints.if_then_clause(control_var, cur_control_cnot_vars)
                # if we set any target then one of the cur_target_cnot_vars must be true:
                self.constraints.if_then_clause(target_var, cur_target_cnot_vars)

        # Chosen control qubit must be strictly less than target qubit:
        for q_1 in range(self.num_qubits):
            for q_2 in range(self.num_qubits):
                cnot_var = self.cnot_qvars[layer_id][q_1][q_2]
                control_var = self.control_qvars[layer_id][q_1]
                target_var = self.target_qvars[layer_id][q_2]
                # Connecting valid cnot vars and auxiliary variables:
                if self.options.minimization == "cx-count":
                    self.constraints.iff_then_each_clause(
                        cnot_var, [control_var, target_var]
                    )
                    if q_1 >= q_2:
                        self.constraints.or_clause([-control_var, -target_var])
                else:
                    assert (
                        self.options.minimization == "cx-depth"
                        or self.options.minimization
                        == "bounded_cx-depth_local_cx-count"
                        or self.options.minimization
                        == "bounded_cx-count_local_cx-depth"
                    )
                    # for parallel cnots, we cannot allow bidirectional constraints:
                    self.constraints.if_then_each_clause(
                        cnot_var, [control_var, target_var]
                    )
                if q_1 >= q_2 or (
                    self.options.platform != None
                    and [q_1, q_2] not in self.options.coupling_graph
                ):
                    # Disable illegal cnot variables:
                    self.constraints.unit_clause(-cnot_var)

        for control_id in range(self.num_qubits):
            for target_id in range(control_id + 1, self.num_qubits):
                # we do not have a cnot on same control and target qubits:
                assert control_id != target_id
                # we do not need to add clauses for illegal cnot vars:
                if control_id >= target_id or (
                    self.options.platform != None
                    and [control_id, target_id] not in self.options.coupling_graph
                ):
                    continue
                cnot_var = self.cnot_qvars[layer_id][control_id][target_id]
                # Forall rows:
                for row_id in range(self.num_rows):
                    # x_j = x_i + x_j, x_cells are updated:
                    self.constraints.if_and_then_clause(
                        [cnot_var, self.x_cells[time_step][row_id][control_id]],
                        [self.flip_xvars[time_step][row_id][target_id]],
                    )
                    self.constraints.if_and_then_clause(
                        [cnot_var, -self.x_cells[time_step][row_id][control_id]],
                        [self.prop_xvars[time_step][row_id][target_id]],
                    )
                    # z_i = z_i + z_j, x_cells are updated:
                    self.constraints.if_and_then_clause(
                        [cnot_var, self.z_cells[time_step][row_id][target_id]],
                        [self.flip_zvars[time_step][row_id][control_id]],
                    )
                    self.constraints.if_and_then_clause(
                        [cnot_var, -self.z_cells[time_step][row_id][target_id]],
                        [self.prop_zvars[time_step][row_id][control_id]],
                    )

        # x_i = x_i, z_j = z_j
        for column_id in range(self.num_qubits):
            # Forall rows, we add the x_cell update clauses:
            for row_id in range(self.num_rows):
                # if not target qubit then the corresponding x_cell is propagated to the next time step:
                self.constraints.if_then_clause(
                    -self.target_qvars[layer_id][column_id],
                    [self.prop_xvars[time_step][row_id][column_id]],
                )
                # if not control qubit then the corresponding z_cell is propagated to the next time step:
                self.constraints.if_then_clause(
                    -self.control_qvars[layer_id][column_id],
                    [self.prop_zvars[time_step][row_id][column_id]],
                )

    def last_layer_constraints(self, plan_length):
        time_step = 2 * plan_length
        if self.options.verbose > 2:
            print(f"layer layer constraints, timestep: {time_step}")
        for column_id in range(self.num_qubits):
            self.constraints.ExactlyOne_constraints(self.last_single_qvars[column_id])

        for column_id in range(self.num_qubits):
            [
                i_gvar,
                h_gvar,
                s_gvar,
                hs_gvar,
                sh_gvar,
                hsh_gvar,
            ] = self.last_single_qvars[column_id]
            self.apply_igate_constraints(i_gvar, column_id, time_step)
            # we only apply other gates if qubit is not disabled:
            self.apply_hgate_constraints(h_gvar, column_id, time_step)
            self.apply_sgate_constraints(s_gvar, column_id, time_step)
            self.apply_hsgate_constraints(hs_gvar, column_id, time_step)
            self.apply_shgate_constraints(sh_gvar, column_id, time_step)
            self.apply_hshgate_constraints(hsh_gvar, column_id, time_step)

    def generate_transition_cnot_optimal(self, layer_id):
        self.single_gate_constraints(layer_id)
        self.cnot_constraints(layer_id)

    def generate_initial_gate(self):
        # initial state is specified in time step 0:
        time_step = 0
        if self.options.verbose > 2:
            print(f"initial constraints, timestep: {time_step}")
        # Exactly One constraints for cells in each row, due to initial identity stabilizer matrix:
        for row_id in range(self.num_rows):
            if row_id < self.num_qubits:
                # destabilizer x is identity matrix:
                self.constraints.ExactlyOne_constraints(self.x_cells[time_step][row_id])
                # destabilizer z is zero matrix:
                for z_var in self.z_cells[time_step][row_id]:
                    self.constraints.unit_clause(-z_var)
            else:
                # destabilizer z is identity matrix:
                self.constraints.ExactlyOne_constraints(self.z_cells[time_step][row_id])
                # stabilizer x is zero matrix:
                for x_var in self.x_cells[time_step][row_id]:
                    self.constraints.unit_clause(-x_var)

        # We initialize identity matrix diagonally:
        # This implies unit clauses on diagonal cell vars:
        for qid in range(self.num_qubits):
            cid = qid
            destabilizer_rid = qid
            stabilizer_rid = qid + self.num_qubits
            # x cells in destabilizer and z cells in stabilizer must be same:
            self.constraints.eq_clause(
                self.x_cells[time_step][destabilizer_rid][cid],
                self.z_cells[time_step][stabilizer_rid][cid],
            )
            # if permutation is disabled, then unit clauses on x cells:
            if not self.options.qubit_permute:
                self.constraints.unit_clause(
                    self.x_cells[time_step][destabilizer_rid][cid]
                )
            else:
                single_destab_x_column = []
                single_stab_z_column = []
                # When permutation is enabled, then we have exactly one constraints also on column vars:
                for rid in range(self.num_qubits):
                    destab_rid = rid
                    stab_rid = rid + self.num_qubits
                    single_destab_x_column.append(
                        self.x_cells[time_step][destab_rid][cid]
                    )
                    single_stab_z_column.append(self.z_cells[time_step][stab_rid][cid])
                self.constraints.ExactlyOne_constraints(single_destab_x_column)
                self.constraints.ExactlyOne_constraints(single_stab_z_column)

    # if a x_cell is true, then positive unit clause
    # else negative unit clause:
    def add_x_cell_unit_clause(self, time_step, cell, row, column):
        if cell == True:
            self.constraints.unit_clause(self.x_cells[time_step][row][column])
        else:
            self.constraints.unit_clause(-self.x_cells[time_step][row][column])

    # if a z_cell is true, then positive unit clause
    # else negative unit clause:
    def add_z_cell_unit_clause(self, time_step, cell, row, column):
        if cell == True:
            self.constraints.unit_clause(self.z_cells[time_step][row][column])
        else:
            self.constraints.unit_clause(-self.z_cells[time_step][row][column])

    # Generating goal constraints:
    def generate_goal_gate(self):
        time_step = 2 * self.options.plan_length + 1
        if self.options.verbose > 2:
            print(f"goal constraints, timestep: {time_step}")
        # we add unit clauses for True and False cells in the destabilizer X matrix:
        for row_id in range(self.num_qubits):
            for column_id in range(self.num_qubits):
                # Adding destab x value:
                self.add_x_cell_unit_clause(
                    time_step,
                    self.matrix.destab_x[row_id][column_id],
                    row_id,
                    column_id,
                )
                # Adding destab z value:
                self.add_z_cell_unit_clause(
                    time_step,
                    self.matrix.destab_z[row_id][column_id],
                    row_id,
                    column_id,
                )

                # Adding stab x value, stabilzer matrices stay below destabilizers so we increment row_id:
                self.add_x_cell_unit_clause(
                    time_step,
                    self.matrix.stab_x[row_id][column_id],
                    self.num_qubits + row_id,
                    column_id,
                )
                # Adding stab z value:
                self.add_z_cell_unit_clause(
                    time_step,
                    self.matrix.stab_z[row_id][column_id],
                    self.num_qubits + row_id,
                    column_id,
                )

    def gate_ordering(self, layer_id):
        # If gates are applied on independent qubits, then we order based on the control qubit:
        for cur_control_id in range(self.num_qubits):
            for cur_target_id in range(cur_control_id + 1, self.num_qubits):
                cur_cnot_var = self.cnot_qvars[layer_id][cur_control_id][cur_target_id]
                if self.options.minimization == "cx-count":
                    # every previous cnot var that has larger control qubit is disabled, when the target qubits are not same:
                    for prev_control_id in range(cur_control_id + 1, self.num_qubits):
                        for prev_target_id in range(
                            prev_control_id + 1, self.num_qubits
                        ):
                            # we do not add symmetry breaking if target qubits are same:
                            if (cur_target_id != prev_control_id) and (
                                cur_target_id != prev_target_id
                            ):
                                # print(prev_control_id, prev_target_id, cur_control_id, cur_target_id)
                                prev_cnot_var = self.cnot_qvars[layer_id - 1][
                                    prev_control_id
                                ][prev_target_id]
                                # now, every current cnot var has smaller control qubit than the previous step.
                                # so we disable all such pairs:
                                self.constraints.or_clause(
                                    [-cur_cnot_var, -prev_cnot_var]
                                )
                else:
                    assert (
                        self.options.minimization == "cx-depth"
                        or self.options.minimization
                        == "bounded_cx-depth_local_cx-count"
                        or self.options.minimization
                        == "bounded_cx-count_local_cx-depth"
                    )
                    prev_control_var_i = self.control_qvars[layer_id - 1][
                        cur_control_id
                    ]
                    prev_control_var_j = self.control_qvars[layer_id - 1][cur_target_id]
                    prev_target_var_i = self.target_qvars[layer_id - 1][cur_control_id]
                    prev_target_var_j = self.target_qvars[layer_id - 1][cur_target_id]
                    self.constraints.if_then_clause(
                        cur_cnot_var,
                        [
                            prev_control_var_i,
                            prev_control_var_j,
                            prev_target_var_i,
                            prev_target_var_j,
                        ],
                    )

    # May be TODO: we can drop some constraints when qubits are disabled
    # while correctness is same, the initial encoding size can be reduced
    # of course, with some propagation (via unit clauses), it is the same for the sat solver:
    def simple_path_constriants(self):
        for i in range(self.options.plan_length + 1):
            for j in range(i + 1, i + self.cycle_upper_bound + 1):
                if j > self.options.plan_length:
                    break
                # print(i-1, j-1)
                # we apply inequality constraints in cnot gate time step with timestep=2*layer_id+1:
                time_step_i = (2 * (i - 1)) + 1
                time_step_j = (2 * (j - 1)) + 1
                # print(self.different_xvars[(i-1,j-1)])
                # gather and exactly one constraint on different varaibles
                # we only need one such witness:

                all_different_cvariables = []
                all_different_cvariables.extend(self.different_xcvars[(i - 1, j - 1)])
                all_different_cvariables.extend(self.different_zcvars[(i - 1, j - 1)])
                # adding AtleastOne constraints are also correct:
                self.constraints.ExactlyOne_constraints(
                    self.different_rvars[(i - 1, j - 1)]
                )
                self.constraints.ExactlyOne_constraints(all_different_cvariables)
                for column_id in range(self.num_qubits):
                    x_columnvar = self.different_xcvars[(i - 1, j - 1)][column_id]
                    z_columnvar = self.different_zcvars[(i - 1, j - 1)][column_id]
                    for row_id in range(self.num_rows):
                        r_var = self.different_rvars[(i - 1, j - 1)][row_id]
                        self.constraints.if_and_then_notequal_clauses(
                            [r_var, x_columnvar],
                            self.x_cells[time_step_i][row_id][column_id],
                            self.x_cells[time_step_j][row_id][column_id],
                        )
                        self.constraints.if_and_then_notequal_clauses(
                            [r_var, z_columnvar],
                            self.z_cells[time_step_i][row_id][column_id],
                            self.z_cells[time_step_j][row_id][column_id],
                        )

    # Cardinality constraints for atmost and atleast k:
    def atmostk_constraints(self, vars, k):
        cnf = CardEnc.atmost(
            lits=vars,
            top_id=self.encoding_variables.next_var - 1,
            encoding=self.options.cardinality,
            bound=k,
        )
        if cnf.nv + 1 > self.encoding_variables.next_var:
            self.encoding_variables.set_next_var(cnf.nv + 1)
        if self.options.verbose > 2:
            print(f"Atmost {k} for {vars}")
        self.constraints.clause_list.extend(cnf.clauses)

    def atleastk_constraints(self, vars, k):
        cnf = CardEnc.atleast(
            lits=vars,
            top_id=self.encoding_variables.next_var - 1,
            encoding=self.options.cardinality,
            bound=k,
        )
        if cnf.nv + 1 > self.encoding_variables.next_var:
            self.encoding_variables.set_next_var(cnf.nv + 1)
        if self.options.verbose > 2:
            print(f"Atleast {k} for {vars}")
        self.constraints.clause_list.extend(cnf.clauses)

    # we generate constraints for local CNOT count optimization using Pysat:
    # We basically use cardinality constraints to restrict the number of CNOT variables in the encoding:
    def local_cx_count_constraints(self):
        all_cnotvars = []
        for layer_id in range(self.options.plan_length):
            if self.options.verbose > 2:
                print(f"local cnot count constraints, layer id: {layer_id}")
            for vars in self.cnot_qvars[layer_id]:
                all_cnotvars.extend(vars)

        # we add atmost k constraints for all cnot vars:
        self.atmostk_constraints(all_cnotvars, self.options.local_cxcount_bound)
        if self.options.verbose > 1:
            print(
                f"local CNOT count bound set to less than or equal {self.options.local_cxcount_bound}"
            )

    def __init__(self, matrix, options, num_qubits, verbose=0):
        self.matrix = matrix
        self.options = options
        self.num_qubits = num_qubits
        self.num_rows = 2 * self.num_qubits
        self.verbose = verbose
        self.quantifier_block = []
        self.clause_list = []
        self.encoding_variables = VarDispatcher()
        self.constraints = Constraints(self.clause_list)

        # We assume that we have more than 1 qubit:
        # TODO : update for clifford synthesis:
        assert self.num_qubits > 1
        if self.options.verbose > 2:
            print("Number of Qubits: ", self.num_qubits)

        self.single_qvars = []
        self.last_single_qvars = []
        self.control_qvars = []
        self.target_qvars = []
        self.cnot_qvars = []
        # for cnot optimization, we only need one control and target qubit:
        # we simply use one-hot encoding to keep the number of variables linear:
        for i in range(self.options.plan_length):
            self.control_qvars.append(self.encoding_variables.get_vars(self.num_qubits))
            self.target_qvars.append(self.encoding_variables.get_vars(self.num_qubits))

        if self.options.verbose > 2:
            print("Control CNOT vars: ", self.control_qvars)
            print("Target CNOT vars: ", self.target_qvars)

        # we generate all the cnot combinations are disable illegal ones:
        for i in range(self.options.plan_length):
            single_cnot_vars = []
            for qid in range(self.num_qubits):
                single_cnot_vars.append(
                    self.encoding_variables.get_vars(self.num_qubits)
                )
            self.cnot_qvars.append(single_cnot_vars)

        # for easy access of cnot vars with same target qubit, we create new list:
        self.cnot_vars_target_slices = []
        for i in range(self.options.plan_length):
            cnot_vars_target_slice = []
            for trg in range(self.num_qubits):
                cur_target_vars = []
                for ctrl in range(self.num_qubits):
                    cur_target_vars.append(self.cnot_qvars[i][ctrl][trg])
                cnot_vars_target_slice.append(cur_target_vars)
            self.cnot_vars_target_slices.append(cnot_vars_target_slice)

        if self.options.verbose > 2:
            print("CNOT vars: ", self.cnot_qvars)
            print("CNOT vars target slices: ", self.cnot_vars_target_slices)

        for i in range(self.options.plan_length):
            single_timestep_variables = []
            for qid in range(self.num_qubits):
                # for clifford synthesis, we need 3 varaibles each for control and target qubits:
                single_timestep_variables.append(self.encoding_variables.get_vars(3))
            self.single_qvars.append(single_timestep_variables)

        if self.options.verbose > 2:
            print("single vars: ", self.single_qvars)

        # For each row, we allocate n cells, each correspond to a column:
        self.x_cells = []
        self.z_cells = []
        self.flip_xvars = []
        self.prop_xvars = []
        self.flip_zvars = []
        self.prop_zvars = []

        # we need makespan of 2*plan_length+1, one for single qubit gates and one for 2-qubit cnot gates layer, and last single qubit layer:
        for time_step in range((2 * self.options.plan_length) + 2):
            single_x_row_cells = []
            single_z_row_cells = []
            if time_step < (2 * self.options.plan_length) + 1:
                single_flipx_vars = []
                single_flipz_vars = []
                single_propx_vars = []
                single_propz_vars = []

            # we need 2*n rows for clifford stabilizer matrix:
            for row_id in range(self.num_rows):
                single_x_row_cells.append(
                    self.encoding_variables.get_vars(self.num_qubits)
                )
                single_z_row_cells.append(
                    self.encoding_variables.get_vars(self.num_qubits)
                )
                # for each cell, we also define flip and propagate variables for both x and z:
                if time_step < (2 * self.options.plan_length) + 1:
                    single_flipx_vars.append(
                        self.encoding_variables.get_vars(self.num_qubits)
                    )
                    single_flipz_vars.append(
                        self.encoding_variables.get_vars(self.num_qubits)
                    )
                    single_propx_vars.append(
                        self.encoding_variables.get_vars(self.num_qubits)
                    )
                    single_propz_vars.append(
                        self.encoding_variables.get_vars(self.num_qubits)
                    )

            self.x_cells.append(single_x_row_cells)
            self.z_cells.append(single_z_row_cells)
            if time_step < (2 * self.options.plan_length) + 1:
                self.flip_xvars.append(single_flipx_vars)
                self.flip_zvars.append(single_flipz_vars)
                self.prop_xvars.append(single_propx_vars)
                self.prop_zvars.append(single_propz_vars)

        if self.options.verbose > 2:
            print("flip x vars: ", self.flip_xvars)
            print("flip z vars: ", self.flip_zvars)
            print("prop x vars: ", self.prop_xvars)
            print("prop z vars: ", self.prop_zvars)
            print("x cells: ", self.x_cells)
            print("z cells: ", self.z_cells)

        if self.options.simple_path_restrictions:
            # Simple path difference variables:
            # we do not want any layer to repeat including the initial state.
            # we assume initial state be -1 layer:
            # we generate variables for each valid layer pair:
            self.different_xcvars = {}
            self.different_zcvars = {}
            self.different_rvars = {}
            # if cycle bound is -1, then we break cycles for all layers:
            if self.options.cycle_bound == -1:
                self.cycle_upper_bound = self.options.plan_length
            else:
                self.cycle_upper_bound = self.options.cycle_bound
            for i in range(self.options.plan_length + 1):
                for j in range(i + 1, i + self.cycle_upper_bound + 1):
                    if j > self.options.plan_length:
                        break
                    # generating variables only for relevant layer pairs:
                    # adjusting index to -1 to allow initial state as a layer:
                    self.different_xcvars[(i - 1, j - 1)] = (
                        self.encoding_variables.get_vars(self.num_qubits)
                    )
                    self.different_zcvars[(i - 1, j - 1)] = (
                        self.encoding_variables.get_vars(self.num_qubits)
                    )
                    self.different_rvars[(i - 1, j - 1)] = (
                        self.encoding_variables.get_vars(2 * self.num_qubits)
                    )

        # single qubit gate sequences for each qubit:
        for i in range(self.num_qubits):
            self.last_single_qvars.append(self.encoding_variables.get_vars(6))

        if self.options.verbose > 2:
            print("last layer single vars: ", self.last_single_qvars)

        # for backward search, we use indicator variables to enable the time step:
        if self.options.search_strategy == "backward":
            self.indicator_vars = self.encoding_variables.get_vars(
                self.options.plan_length
            )
            # assert that gate ordering and simple path are not enabled:
            assert not self.options.simple_path_restrictions
            assert not self.options.gate_ordering

        self.generate_initial_gate()

        self.auxilary_flip_propagate_constraints()

        # print(self.clause_list)

        for i in range(self.options.plan_length):
            self.generate_transition_cnot_optimal(i)

        self.last_layer_constraints(self.options.plan_length)

        self.generate_goal_gate()

        if self.options.simple_path_restrictions:
            self.simple_path_constriants()

        # if local-cx-count is chosen for minimization, we add additional constraints on CNOT count:
        if (
            self.options.minimization == "bounded_cx-depth_local_cx-count"
            or self.options.minimization == "bounded_cx-count_local_cx-depth"
        ):
            self.local_cx_count_constraints()

        self.generate_quantifier_blocks()

        self.print_encoding_tofile(self.options.dimacs_out)
