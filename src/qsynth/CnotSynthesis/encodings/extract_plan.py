import os, subprocess
from qsynth.CnotSynthesis.encodings.generate_initial_swaps import (
    extract_swaps_for_initial_mapping,
)


class ExtractPlan:
    def extract_initial_map(self, encoder):
        initial_time_step = 0
        for qid in range(encoder.num_qubits):
            for row_id in range(encoder.num_qubits):
                cell_var = encoder.cells[initial_time_step][row_id][qid]
                if self.sol_map[cell_var]:
                    self.qubit_map[qid] = row_id
                    break
        extract_swaps_for_initial_mapping(self.qubit_map, self.plan, encoder.num_qubits)

    def extract_depth_optimal_plan(self, encoder):
        if self.options.qubit_permute == True:
            self.extract_initial_map(encoder)
        for time_step in range(len(encoder.cnot_variables)):
            cnot_list = encoder.cnot_variables[time_step]
            for cnot_var_id in range(len(cnot_list)):
                cnot_var = cnot_list[cnot_var_id]
                # if preprocessor removes some variables, we assume they are false:
                if cnot_var not in self.sol_map:
                    continue
                if self.sol_map[cnot_var]:
                    qubit1, qubit2 = encoder.control_target_dict[cnot_var_id]
                    # we only add if the indicator variables are enable during backward search:
                    if (
                        encoder.options.search_strategy == "backward"
                        and "fixed-bounded_cx-depth" not in encoder.options.minimization
                    ):
                        indicator_var = encoder.indicator_vars[time_step]
                        if (
                            indicator_var not in self.sol_map
                            or self.sol_map[indicator_var] == 0
                        ):
                            continue
                    self.plan.append(("cnot", "q" + str(qubit1), "q" + str(qubit2)))

    def extract_cnot_optimal_plan(self, encoder):
        if self.options.qubit_permute == True:
            self.extract_initial_map(encoder)
        for plan_step in range(encoder.options.plan_length):
            cnot_qubit1, cnot_qubit2 = -1, -1
            for qid in range(encoder.num_qubits):
                cnot_control_var = encoder.control_qvars[plan_step][qid]
                if cnot_control_var not in self.sol_map:
                    continue
                if self.sol_map[cnot_control_var]:
                    cnot_qubit1 = qid
            for qid in range(encoder.num_qubits):
                cnot_target_var = encoder.target_qvars[plan_step][qid]
                if cnot_target_var not in self.sol_map:
                    continue
                if self.sol_map[cnot_target_var]:
                    cnot_qubit2 = qid
            # we only add if the indicator variables are enable during backward search:
            if (
                encoder.options.search_strategy == "b"
                and "fixed-bounded_cx-depth" not in encoder.options.minimization
            ):
                indicator_var = encoder.indicator_vars[plan_step]
                if (
                    indicator_var not in self.sol_map
                    or self.sol_map[indicator_var] == 0
                ):
                    continue
            self.plan.append(("cnot", "q" + str(cnot_qubit1), "q" + str(cnot_qubit2)))

    def __init__(self, options, solver):
        self.options = options
        self.sol_map = solver.sol_map
        self.qubit_map = solver.qubit_map
        self.plan = []
