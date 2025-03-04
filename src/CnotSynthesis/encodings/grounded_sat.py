# Irfansha Shaik, 12.02.2024, Aarhus
from src.CnotSynthesis.circuit_utils.constraints import Constraints
from src.CnotSynthesis.circuit_utils.variables_dispatcher import VarDispatcher


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

        # if not target qubit then the corresponding cell is propagated to the next time step:
        for column_id in range(self.num_qubits):
            # Forall rows, we add the cell update clauses:
            for row_id in range(self.num_qubits):
                self.constraints.if_and_then_equal_clauses(
                    [-self.target_qvars[time_step][column_id]],
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

        if self.options.minimization == "depth":
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
            assert self.options.minimization == "gates"
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

        self.generate_initial_gate()

        for i in range(self.options.plan_length):
            if self.options.minimization == "depth":
                self.generate_transition_depth_optimal(i)
            else:
                assert self.options.minimization == "gates"
                self.generate_transition_cnot_optimal(i)

        self.generate_goal_gate()

        self.generate_quantifier_blocks()

        self.print_encoding_tofile(self.options.dimacs_out)
