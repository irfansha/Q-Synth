# Irfansha Shaik, 31.01.2024, Aarhus
import math
from src.CnotSynthesis.circuit_utils.constraints import Constraints
from src.CnotSynthesis.circuit_utils.variables_dispatcher import VarDispatcher


class LiftedQbf:

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
        if self.options.minimization == "depth":
            # CNOT and touched variables:
            for i in range(self.options.plan_length):
                self.quantifier_block.append(
                    "e " + " ".join(str(x) for x in self.cnot_variables[i]) + " 0"
                )
                self.quantifier_block.append(
                    "e " + " ".join(str(x) for x in self.touched_qvars[i]) + " 0"
                )
        else:
            assert self.options.minimization == "gates"
            # Control and target cnot variables:
            for i in range(self.options.plan_length):
                self.quantifier_block.append(
                    "e " + " ".join(str(x) for x in self.control_qvars[i]) + " 0"
                )
                self.quantifier_block.append(
                    "e " + " ".join(str(x) for x in self.target_qvars[i]) + " 0"
                )
        # Forall row variables:
        self.quantifier_block.append(
            "a " + " ".join(str(x) for x in self.forall_rows) + " 0"
        )
        # Exists row variables:
        self.quantifier_block.append(
            "e " + " ".join(str(x) for x in self.exists_rows) + " 0"
        )
        # Cell variables:
        for i in range(self.options.plan_length + 1):
            self.quantifier_block.append(
                "e " + " ".join(str(x) for x in self.cells[i]) + " 0"
            )

    def generate_transition_depth_optimal(self, time_step):
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
                and [control_id, target_id] not in self.options.coupling_graph
            ):
                self.constraints.unit_clause(
                    -self.cnot_variables[time_step][cnot_varid]
                )
                continue
            self.constraints.if_then_clause(
                self.cnot_variables[time_step][cnot_varid],
                [self.touched_qvars[time_step][target_id]],
            )

            # for each cnot var, if the control qubit is true then the target qubit is flipped:
            self.constraints.if_and_then_notequal_clauses(
                [
                    self.cnot_variables[time_step][cnot_varid],
                    self.cells[time_step][control_id],
                ],
                self.cells[time_step][target_id],
                self.cells[time_step + 1][target_id],
            )
            # for each cnot var, if the control qubit is false then the target qubit is propagated:
            self.constraints.if_and_then_equal_clauses(
                [
                    self.cnot_variables[time_step][cnot_varid],
                    -self.cells[time_step][control_id],
                ],
                self.cells[time_step][target_id],
                self.cells[time_step + 1][target_id],
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
            self.constraints.if_and_then_equal_clauses(
                [-self.touched_qvars[time_step][column_id]],
                self.cells[time_step][column_id],
                self.cells[time_step + 1][column_id],
            )

    def generate_transition_cnot_optimal(self, time_step):
        # Exactly one of the control and target vars is true:
        self.constraints.ExactlyOne_constraints(self.control_qvars[time_step])
        self.constraints.ExactlyOne_constraints(self.target_qvars[time_step])
        # If coupling graph is given then we disable unconnected cnot operations:
        if self.options.coupling_graph != None:
            for control_id in range(self.num_qubits):
                for target_id in range(self.num_qubits):
                    if [control_id, target_id] not in self.options.coupling_graph:
                        self.constraints.or_clause(
                            [
                                -self.control_qvars[time_step][control_id],
                                -self.target_qvars[time_step][target_id],
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
                # if coupling graph is given and the qubit pair is not connected we skip:
                if (
                    self.options.coupling_graph != None
                    and [control_id, target_id] not in self.options.coupling_graph
                ):
                    continue
                # if the control and target qubits are true, and control cell is also true, then the target cell is flipped:
                self.constraints.if_and_then_notequal_clauses(
                    [
                        self.control_qvars[time_step][control_id],
                        self.target_qvars[time_step][target_id],
                        self.cells[time_step][control_id],
                    ],
                    self.cells[time_step][target_id],
                    self.cells[time_step + 1][target_id],
                )
                # if the control and target qubits are true, and control cell is false, then the target cell is propagated:
                self.constraints.if_and_then_equal_clauses(
                    [
                        self.control_qvars[time_step][control_id],
                        self.target_qvars[time_step][target_id],
                        -self.cells[time_step][control_id],
                    ],
                    self.cells[time_step][target_id],
                    self.cells[time_step + 1][target_id],
                )

        # if not target qubit then the corresponding cell is propagated to the next time step:
        for column_id in range(self.num_qubits):
            self.constraints.if_and_then_equal_clauses(
                [-self.target_qvars[time_step][column_id]],
                self.cells[time_step][column_id],
                self.cells[time_step + 1][column_id],
            )

    def generate_initial_gate(self):
        # initial state is specified in time step 0:
        time_step = 0

        # implications from forall to exists row variables:
        for row_id in range(self.num_qubits):
            cur_row = self.constraints.generate_binary_format(self.forall_rows, row_id)
            self.constraints.if_and_then_clause(cur_row, [self.exists_rows[row_id]])

        # Exactly One constraints for row variables and 0th timestep cell variables:
        self.constraints.ExactlyOne_constraints(self.exists_rows)
        # self.constraints.ExactlyOne_constraints(self.cells[time_step])

        # We initialize identity matrix diagonally:
        # This implies to equalities with the exists rows and cells:
        for row_id in range(self.num_qubits):
            self.constraints.eq_clause(
                self.exists_rows[row_id], self.cells[time_step][row_id]
            )

    # Generating goal constraints:
    def generate_goal_gate(self):
        time_step = self.options.plan_length
        # if the right row is enabled in exists row variable, then we set the cells to that row values:
        for row_id in range(self.num_qubits):
            for column_id in range(self.num_qubits):
                cell = self.matrix.destab_x[row_id][column_id]
                if cell == True:
                    self.constraints.if_then_clause(
                        self.exists_rows[row_id], [self.cells[time_step][column_id]]
                    )
                else:
                    self.constraints.if_then_clause(
                        self.exists_rows[row_id], [-self.cells[time_step][column_id]]
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
        if self.options.verbose > 1:
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
            # we remember the cnot var indices that use a control var:
            self.control_cnotvar_dict = {}
            # we remember the cnot var indices that change a target var:
            self.target_cnotvar_dict = {}
            counter = 0
            for control_id in range(self.num_qubits):
                for target_id in range(self.num_qubits):
                    if control_id != target_id:
                        self.control_target_dict[counter] = (control_id, target_id)
                        self.initialize_or_add_element(
                            self.control_cnotvar_dict, control_id, counter
                        )
                        self.initialize_or_add_element(
                            self.target_cnotvar_dict, target_id, counter
                        )
                        counter = counter + 1

            if self.options.verbose > 1:
                print("Number of CNOT operators: ", self.num_cnot_vars)
                print("CNOT Variables: ", self.cnot_variables)
                print("Touched qubit Variables: ", self.touched_qvars)
                print("Control-Target Dict Variables: ", self.control_target_dict)
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
            if self.options.verbose > 1:
                print("Control CNOT vars: ", self.control_qvars)
                print("Target CNOT vars: ", self.target_qvars)

        # we assert that more than 1 qubits exist:
        assert self.num_qubits > 1
        self.num_log_qubits = math.ceil(math.log2(self.num_qubits))

        # Allocating forall (log) row variables:
        self.forall_rows = self.encoding_variables.get_vars(self.num_log_qubits)
        # Allocating existential row variables:
        self.exists_rows = self.encoding_variables.get_vars(self.num_qubits)

        if self.options.verbose > 1:
            print("Forall (log) row variables: ", self.forall_rows)
            print("Exists row variables: ", self.exists_rows)

        # For each row, we allocate n cells, each correspond to a column:
        self.cells = []
        for i in range(self.options.plan_length + 1):
            self.cells.append(self.encoding_variables.get_vars(self.num_qubits))

        if self.options.verbose > 1:
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

        self.print_encoding_tofile(self.options.qdimacs_out)
