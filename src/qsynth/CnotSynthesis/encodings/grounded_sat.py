# Irfansha Shaik, 12.02.2024, Aarhus
from qsynth.CnotSynthesis.circuit_utils.constraints import Constraints
from qsynth.CnotSynthesis.circuit_utils.variables_dispatcher import VarDispatcher
from pysat.card import *


class GroundedSat:
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

    def generate_transition_depth_optimal(self, time_step):
        initial_timestep = 0
        # Atleast One can be dropped without loosing correctness, might find better depth solutions:
        if (
            self.options.search_strategy != "backward"
            or "fixed-bounded_cx-depth" in self.options.minimization
        ):
            self.constraints.AtleastOne_constraints(self.cnot_variables[time_step])
        # adding confliction constraints from same control and target qubits:
        for control_id in range(self.num_qubits):
            cur_conflicting_cnot_list = []
            for cnot_varid in self.control_cnotvar_dict[control_id]:
                cur_conflicting_cnot_list.append(
                    self.cnot_variables[time_step][cnot_varid]
                )
            for cnot_varid in self.target_cnotvar_dict[control_id]:
                cur_conflicting_cnot_list.append(
                    self.cnot_variables[time_step][cnot_varid]
                )
            self.constraints.AtmostOne_constraints(cur_conflicting_cnot_list)

        for cnot_varid in range(self.num_cnot_vars):
            # we update the touched var:
            (control_id, target_id) = self.control_target_dict[cnot_varid]
            # If coupling graph is given and current cnot var is on disconnected qubits, we drop the constraints:
            # we further disable the corresponding cnot vars:
            if (
                self.options.coupling_graph != None
                and not self.options.qubit_permute
                and [control_id, target_id] not in self.options.coupling_graph
            ):
                self.constraints.unit_clause(
                    -self.cnot_variables[time_step][cnot_varid]
                )
                continue
            # If coupling graph is given and qubit permutation is enable
            # then we disable permuted unconnected cnot operations:
            elif (
                self.options.coupling_graph != None
                and self.options.qubit_permute
                and [control_id, target_id] not in self.options.coupling_graph
            ):
                # we disable the pair (p,q) if (i,j) is mapped to them:
                # (m_{i,p} & m_{j,q} -> (-cnot_{p,q})):
                for permuted_cid in range(self.num_qubits):
                    for permuted_tid in range(self.num_qubits):
                        if (
                            permuted_cid,
                            permuted_tid,
                        ) in self.reverse_control_target_dict:
                            permuted_cnotvarid = self.reverse_control_target_dict[
                                (permuted_cid, permuted_tid)
                            ]
                            self.constraints.or_clause(
                                [
                                    -self.cells[initial_timestep][control_id][
                                        permuted_cid
                                    ],
                                    -self.cells[initial_timestep][target_id][
                                        permuted_tid
                                    ],
                                    -self.cnot_variables[time_step][permuted_cnotvarid],
                                ]
                            )
            # if imply touched variables for propagation:
            self.constraints.if_then_clause(
                self.cnot_variables[time_step][cnot_varid],
                [self.touched_qvars[time_step][target_id]],
            )

            # forall rows, we duplicate the constraints:
            for row_id in range(self.num_qubits):
                if (
                    self.options.search_strategy != "backward"
                    or "fixed-bounded_cx-depth" in self.options.minimization
                ):
                    # for each cnot var, if the control qubit is true then the target qubit is flipped:
                    self.constraints.if_and_then_notequal_clauses(
                        [
                            self.cnot_variables[time_step][cnot_varid],
                            self.cells[time_step][row_id][control_id],
                        ],
                        self.cells[time_step][row_id][target_id],
                        self.cells[time_step + 1][row_id][target_id],
                    )
                    # for each cnot var, if the control qubit is false then the target qubit is propagated:
                    self.constraints.if_and_then_equal_clauses(
                        [
                            self.cnot_variables[time_step][cnot_varid],
                            -self.cells[time_step][row_id][control_id],
                        ],
                        self.cells[time_step][row_id][target_id],
                        self.cells[time_step + 1][row_id][target_id],
                    )
                else:
                    # for each cnot var, if the control qubit is true then the target qubit is flipped:
                    # in backward search, we only update if indictor variable is set to true:
                    self.constraints.if_and_then_notequal_clauses(
                        [
                            self.cnot_variables[time_step][cnot_varid],
                            self.cells[time_step][row_id][control_id],
                            self.indicator_vars[time_step],
                        ],
                        self.cells[time_step][row_id][target_id],
                        self.cells[time_step + 1][row_id][target_id],
                    )
                    # for each cnot var, if the control qubit is false then the target qubit is propagated:
                    self.constraints.if_and_then_equal_clauses(
                        [
                            self.cnot_variables[time_step][cnot_varid],
                            -self.cells[time_step][row_id][control_id],
                            self.indicator_vars[time_step],
                        ],
                        self.cells[time_step][row_id][target_id],
                        self.cells[time_step + 1][row_id][target_id],
                    )

        # we imply one of the cnot vars to be true if a touched var is true:
        for target_id in range(self.num_qubits):
            cur_cnot_vars = []
            for cnot_varid in self.target_cnotvar_dict[target_id]:
                cur_cnot_vars.append(self.cnot_variables[time_step][cnot_varid])
            self.constraints.if_then_clause(
                self.touched_qvars[time_step][target_id], cur_cnot_vars
            )

        # if not touched then cells are propagated to the next time step:
        for column_id in range(self.num_qubits):
            # forall rows, we duplicate the constraints:
            for row_id in range(self.num_qubits):
                self.constraints.if_and_then_equal_clauses(
                    [-self.touched_qvars[time_step][column_id]],
                    self.cells[time_step][row_id][column_id],
                    self.cells[time_step + 1][row_id][column_id],
                )
                if (
                    self.options.search_strategy == "backward"
                    and "fixed-bounded_cx-depth" not in self.options.minimization
                ):
                    # We propagate if indicator variable is set to zero, then we propagate:
                    self.constraints.if_and_then_equal_clauses(
                        [-self.indicator_vars[time_step]],
                        self.cells[time_step][row_id][column_id],
                        self.cells[time_step + 1][row_id][column_id],
                    )

    def generate_transition_cnot_optimal(self, time_step):
        initial_timestep = 0
        # Exactly one of the control and target vars is true:
        self.constraints.ExactlyOne_constraints(self.control_qvars[time_step])
        self.constraints.ExactlyOne_constraints(self.target_qvars[time_step])
        # If coupling graph is given and qubit permutation is disabled
        # then we disable unconnected cnot operations:
        if self.options.coupling_graph != None and not self.options.qubit_permute:
            for control_id in range(self.num_qubits):
                for target_id in range(self.num_qubits):
                    if [control_id, target_id] not in self.options.coupling_graph:
                        self.constraints.or_clause(
                            [
                                -self.control_qvars[time_step][control_id],
                                -self.target_qvars[time_step][target_id],
                            ]
                        )
        # If coupling graph is given and qubit permutation is enable
        # then we disable permuted unconnected cnot operations:
        elif self.options.coupling_graph != None and self.options.qubit_permute:
            for control_id in range(self.num_qubits):
                for target_id in range(self.num_qubits):
                    if [control_id, target_id] not in self.options.coupling_graph:
                        # we disable the pair (p,q) if (i,j) is mapped to them:
                        # (m_{i,p} & m_{j,q} -> (-ctrl_{p} | -trg_{q})):
                        for permuted_cid in range(self.num_qubits):
                            for permuted_tid in range(self.num_qubits):
                                self.constraints.or_clause(
                                    [
                                        -self.cells[initial_timestep][control_id][
                                            permuted_cid
                                        ],
                                        -self.cells[initial_timestep][target_id][
                                            permuted_tid
                                        ],
                                        -self.control_qvars[time_step][permuted_cid],
                                        -self.target_qvars[time_step][permuted_tid],
                                    ]
                                )
        else:
            # If a coupling graph is not given,
            # Chosen control and target qubit must not be true at the same time, since a cnot is applied on different qubits:
            for qid in range(self.num_qubits):
                self.constraints.or_clause(
                    [
                        -self.control_qvars[time_step][qid],
                        -self.target_qvars[time_step][qid],
                    ]
                )

        for control_id in range(self.num_qubits):
            for target_id in range(self.num_qubits):
                # we do not have a cnot on same control and target qubits:
                if control_id == target_id:
                    continue
                # if coupling graph is given and qubit not permuted and the qubit pair is not connected we skip:
                if (
                    self.options.coupling_graph != None
                    and (not self.options.qubit_permute)
                    and [control_id, target_id] not in self.options.coupling_graph
                ):
                    continue
                # Forall rows, we add the cell update clauses:
                for row_id in range(self.num_qubits):
                    # if the control and target qubits are true, and control cell is also true, then the target cell is flipped:
                    if (
                        self.options.search_strategy != "backward"
                        or "fixed-bounded_cx-depth" in self.options.minimization
                    ):
                        self.constraints.if_and_then_notequal_clauses(
                            [
                                self.control_qvars[time_step][control_id],
                                self.target_qvars[time_step][target_id],
                                self.cells[time_step][row_id][control_id],
                            ],
                            self.cells[time_step][row_id][target_id],
                            self.cells[time_step + 1][row_id][target_id],
                        )
                        # if the control and target qubits are true, and control cell is false, then the target cell is propagated:
                        self.constraints.if_and_then_equal_clauses(
                            [
                                self.control_qvars[time_step][control_id],
                                self.target_qvars[time_step][target_id],
                                -self.cells[time_step][row_id][control_id],
                            ],
                            self.cells[time_step][row_id][target_id],
                            self.cells[time_step + 1][row_id][target_id],
                        )
                    else:
                        # we only update if the indicator variable is set in the backward search:
                        self.constraints.if_and_then_notequal_clauses(
                            [
                                self.control_qvars[time_step][control_id],
                                self.target_qvars[time_step][target_id],
                                self.cells[time_step][row_id][control_id],
                                self.indicator_vars[time_step],
                            ],
                            self.cells[time_step][row_id][target_id],
                            self.cells[time_step + 1][row_id][target_id],
                        )
                        # if the control and target qubits are true, and control cell is false, then the target cell is propagated:
                        self.constraints.if_and_then_equal_clauses(
                            [
                                self.control_qvars[time_step][control_id],
                                self.target_qvars[time_step][target_id],
                                -self.cells[time_step][row_id][control_id],
                                self.indicator_vars[time_step],
                            ],
                            self.cells[time_step][row_id][target_id],
                            self.cells[time_step + 1][row_id][target_id],
                        )

        # if not target qubit then the corresponding cell is propagated to the next time step:
        for column_id in range(self.num_qubits):
            # Forall rows, we add the cell update clauses:
            for row_id in range(self.num_qubits):
                self.constraints.if_and_then_equal_clauses(
                    [-self.target_qvars[time_step][column_id]],
                    self.cells[time_step][row_id][column_id],
                    self.cells[time_step + 1][row_id][column_id],
                )
                if (
                    self.options.search_strategy == "backward"
                    and "fixed-bounded_cx-depth" not in self.options.minimization
                ):
                    # We propagate if indicator variable is set to zero, then we propagate:
                    self.constraints.if_and_then_equal_clauses(
                        [-self.indicator_vars[time_step]],
                        self.cells[time_step][row_id][column_id],
                        self.cells[time_step + 1][row_id][column_id],
                    )

    def generate_initial_gate(self):
        # initial state is specified in time step 0:
        time_step = 0

        # Exactly One constraints for cells in each row, due to initial identity matrix:
        for row_id in range(self.num_qubits):
            self.constraints.ExactlyOne_constraints(self.cells[time_step][row_id])

        if not self.options.qubit_permute:
            # We initialize identity matrix diagonally:
            # This implies unit clauses on diagonal cell vars:
            for qid in range(self.num_qubits):
                self.constraints.unit_clause(self.cells[time_step][qid][qid])
        else:
            # Exactly One constraints for cells in each column, if initial matrix permutations are allowed:
            # Atmost One constraints are sufficient in theory, we can drop atleast one constraints:
            for column_id in range(self.num_qubits):
                cur_column_vars = []
                for row_id in range(self.num_qubits):
                    cur_column_vars.append(self.cells[time_step][row_id][column_id])
                self.constraints.ExactlyOne_constraints(cur_column_vars)

    # Generating goal constraints:
    def generate_goal_gate(self):
        time_step = self.options.plan_length
        # we add unit clauses for True and False cells in the destabilizer X matrix:
        for row_id in range(self.num_qubits):
            for column_id in range(self.num_qubits):
                cell = self.matrix.destab_x[row_id][column_id]
                if cell == True:
                    self.constraints.unit_clause(
                        self.cells[time_step][row_id][column_id]
                    )
                else:
                    self.constraints.unit_clause(
                        -self.cells[time_step][row_id][column_id]
                    )

    # For a given key, the given element is added to its list
    # if the list is not available a new one is created:
    def initialize_or_add_element(self, dict, key, value):
        # updating target id dict:
        if key not in dict:
            dict[key] = [value]
        else:
            dict[key].append(value)

    def gate_ordering(self, time_step):
        # If gates are applied on independent qubits, then we order based on the control qubit:
        for cur_control_id in range(self.num_qubits):
            for cur_target_id in range(self.num_qubits):
                if cur_control_id == cur_target_id:
                    continue
                if self.options.minimization == "cx-count":
                    cur_contrl_var = self.control_qvars[time_step][cur_control_id]
                    cur_target_var = self.target_qvars[time_step][cur_target_id]
                    # every previous cnot var that has larger control qubit is disabled, when the target qubits are not same:
                    for prev_control_id in range(self.num_qubits):
                        for prev_target_id in range(self.num_qubits):
                            if prev_control_id == prev_target_id:
                                continue

                            prev_contrl_var = self.control_qvars[time_step - 1][
                                prev_control_id
                            ]
                            prev_target_var = self.target_qvars[time_step - 1][
                                prev_target_id
                            ]
                            # 2 CNOTs are independent if:
                            # - they have same target qubits
                            # - they do not share control and target qubits:
                            if (prev_target_id == cur_target_id) or (
                                (cur_target_id != prev_control_id)
                                and (cur_control_id != prev_target_id)
                            ):
                                # print(prev_control_id, prev_target_id, cur_control_id, cur_target_id)
                                # if If previous control qubit is greater than current control qubit, we disable the cnot pair:
                                # -(cur_contrl_var & cur_target_var) | -(prev_contrl_var & prev_target_var):
                                if prev_control_id > cur_control_id:
                                    self.constraints.or_clause(
                                        [
                                            -cur_contrl_var,
                                            -cur_target_var,
                                            -prev_contrl_var,
                                            -prev_target_var,
                                        ]
                                    )
                                # if previous control qubit is equal to current control qubit,
                                # then previous target qubit must be smaller than current target qubit:
                                if prev_control_id == cur_control_id:
                                    if prev_target_id >= cur_target_id:
                                        # if previou control and current control are same,
                                        # then previous target must be smaller than current target:
                                        # If not, we disable the cnot pair:
                                        # -(cur_contrl_var & cur_target_var) | -(prev_contrl_var & prev_target_var):
                                        self.constraints.or_clause(
                                            [
                                                -cur_contrl_var,
                                                -cur_target_var,
                                                -prev_contrl_var,
                                                -prev_target_var,
                                            ]
                                        )
                else:
                    assert (
                        self.options.minimization == "cx-depth"
                        or "local_cx-count" in self.options.minimization
                        or self.options.minimization
                        == "bounded_cx-count_local_cx-depth"
                    )
                    cur_cnot_var = self.cnot_variables[time_step][
                        self.reverse_control_target_dict[
                            (cur_control_id, cur_target_id)
                        ]
                    ]
                    # For the control and target qubits,
                    # - if a CNOT was applied in current step,
                    # - some CNOT must have been applied on either control or target qubits in the previous step.
                    prev_control_cnots_list = []
                    # gathering CNOTs from current control id and target id as a control var in previous step:
                    for cnot_varid in self.control_cnotvar_dict[cur_control_id]:
                        prev_control_cnots_list.append(
                            self.cnot_variables[time_step - 1][cnot_varid]
                        )
                    for cnot_varid in self.control_cnotvar_dict[cur_target_id]:
                        prev_control_cnots_list.append(
                            self.cnot_variables[time_step - 1][cnot_varid]
                        )
                    # Assert no duplicates in prev_cnots_list:
                    assert sorted(prev_control_cnots_list) == sorted(
                        list(set(prev_control_cnots_list))
                    ), "Duplicate CNOT variables found in previous step for control and target qubits."
                    # we imply that one of the CNOTs in previous step is enabled or
                    # if a CNOT is applied as a target on cur_control_id or cur_target_id qubits,
                    # it must have been touched in the previous step:
                    self.constraints.if_then_clause(
                        cur_cnot_var,
                        prev_control_cnots_list
                        + [
                            self.touched_qvars[time_step - 1][cur_control_id],
                            self.touched_qvars[time_step - 1][cur_target_id],
                        ],
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
        for time_step in range(self.options.plan_length):
            all_cnotvars.extend(self.cnot_variables[time_step])

        # we add atmost k constraints for all cnot vars:
        self.atmostk_constraints(all_cnotvars, self.options.local_cxcount_bound)
        if self.options.verbose > 1:
            print(
                f"local CNOT count bound set to less than {self.options.local_cxcount_bound}"
            )

    def __init__(self, matrix, options, num_qubits, verbose=0):
        self.matrix = matrix
        self.options = options
        self.num_qubits = num_qubits
        self.verbose = verbose
        self.quantifier_block = []
        self.clause_list = []
        self.encoding_variables = VarDispatcher()
        self.constraints = Constraints(self.clause_list)

        # We assume that we have more than 1 qubit:
        assert self.num_qubits > 1
        if self.options.verbose > 2:
            print("Number of Qubits: ", self.num_qubits)

        if (
            self.options.minimization == "cx-depth"
            or "local_cx-count" in self.options.minimization
            or self.options.minimization == "bounded_cx-count_local_cx-depth"
        ):
            # number of valid CNOT operator are n*(n-1):
            self.num_cnot_vars = self.num_qubits * (self.num_qubits - 1)
            # Allocating CNOT operator variables, and touched qubit variables at each time step:
            self.cnot_variables = []
            self.touched_qvars = []
            for i in range(self.options.plan_length):
                self.cnot_variables.append(
                    self.encoding_variables.get_vars(self.num_cnot_vars)
                )
                self.touched_qvars.append(
                    self.encoding_variables.get_vars(self.num_qubits)
                )

            # we fix the control and target indicies for cnot variables:
            self.control_target_dict = {}
            self.reverse_control_target_dict = {}
            # we remember the cnot var indices that use a control var:
            self.control_cnotvar_dict = {}
            # we remember the cnot var indices that change a target var:
            self.target_cnotvar_dict = {}
            counter = 0
            for control_id in range(self.num_qubits):
                for target_id in range(self.num_qubits):
                    if control_id != target_id:
                        self.control_target_dict[counter] = (control_id, target_id)
                        self.reverse_control_target_dict[(control_id, target_id)] = (
                            counter
                        )
                        self.initialize_or_add_element(
                            self.control_cnotvar_dict, control_id, counter
                        )
                        self.initialize_or_add_element(
                            self.target_cnotvar_dict, target_id, counter
                        )
                        counter = counter + 1

            if self.options.verbose > 2:
                print("Number of CNOT operators: ", self.num_cnot_vars)
                print("CNOT Variables: ", self.cnot_variables)
                print("Touched qubit Variables: ", self.touched_qvars)
                print("Control-Target Dict Variables: ", self.control_target_dict)
                print(
                    "Reverse Control-Target Dict Variables: ",
                    self.reverse_control_target_dict,
                )
                print("Control-Cnot Dict Variables: ", self.control_cnotvar_dict)
                print("Target-Cnot Dict Variables: ", self.target_cnotvar_dict)
        else:
            assert self.options.minimization == "cx-count"
            self.control_qvars = []
            self.target_qvars = []
            # for cnot optimization, we only need one control and target qubit:
            # we simply use one-hot encoding to keep the number of variables linear:
            for i in range(self.options.plan_length):
                self.control_qvars.append(
                    self.encoding_variables.get_vars(self.num_qubits)
                )
                self.target_qvars.append(
                    self.encoding_variables.get_vars(self.num_qubits)
                )
            if self.options.verbose > 2:
                print("Control CNOT vars: ", self.control_qvars)
                print("Target CNOT vars: ", self.target_qvars)

        # For each row, we allocate n cells, each correspond to a column:
        self.cells = []
        for time_step in range(self.options.plan_length + 1):
            single_row_cells = []
            for row_id in range(self.num_qubits):
                single_row_cells.append(
                    self.encoding_variables.get_vars(self.num_qubits)
                )
            self.cells.append(single_row_cells)

        if self.options.verbose > 2:
            print("Cell variables: ", self.cells)

        # for backward search, we use indicator variables to enable the time step:
        if (
            self.options.search_strategy == "backward"
            and "fixed-bounded_cx-depth" not in self.options.minimization
        ):
            self.indicator_vars = self.encoding_variables.get_vars(
                self.options.plan_length
            )

        self.generate_initial_gate()

        for i in range(self.options.plan_length):
            if (
                self.options.minimization == "cx-depth"
                or "local_cx-count" in self.options.minimization
                or self.options.minimization == "bounded_cx-count_local_cx-depth"
            ):
                self.generate_transition_depth_optimal(i)
            else:
                assert self.options.minimization == "cx-count"
                self.generate_transition_cnot_optimal(i)
            if i >= 1 and self.options.gate_ordering:
                self.gate_ordering(i)

        self.generate_goal_gate()
        # if local-cx-count is chosen for minimization, we add additional constraints on CNOT count:
        if (
            "local_cx-count" in self.options.minimization
            or self.options.minimization == "bounded_cx-count_local_cx-depth"
        ):
            self.local_cx_count_constraints()

        self.generate_quantifier_blocks()

        self.print_encoding_tofile(self.options.dimacs_out)
