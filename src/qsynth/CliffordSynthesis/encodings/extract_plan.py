import os, subprocess
from qsynth.CnotSynthesis.encodings.generate_initial_swaps import (
    extract_swaps_for_initial_mapping,
)


class ExtractPlan:
    def extract_initial_map(self, encoder):
        initial_time_step = 0
        for qid in range(encoder.num_qubits):
            for row_id in range(encoder.num_qubits):
                cell_var = encoder.x_cells[initial_time_step][row_id][qid]
                if self.sol_map[cell_var]:
                    self.qubit_map[qid] = row_id
                    break
        extract_swaps_for_initial_mapping(self.qubit_map, self.plan, encoder.num_qubits)

    def extract_simpleaux_plan(self, encoder):
        if self.options.qubit_permute == True:
            self.extract_initial_map(encoder)

        for plan_step in range(encoder.options.plan_length):
            # single qubit gates:
            for qid in range(encoder.num_qubits):
                [i_ctrl, hp_ctrl, ph_ctrl] = encoder.single_qvars[plan_step][qid]
                if hp_ctrl in self.sol_map and self.sol_map[hp_ctrl]:
                    self.plan.append(("h-gate", "q" + str(qid)))
                    self.plan.append(("s-gate", "q" + str(qid)))
                elif ph_ctrl in self.sol_map and self.sol_map[ph_ctrl]:
                    self.plan.append(("s-gate", "q" + str(qid)))
                    self.plan.append(("h-gate", "q" + str(qid)))
                else:
                    assert i_ctrl in self.sol_map and self.sol_map[i_ctrl]
            # cnot gates:
            for ctrl in range(encoder.num_qubits):
                for trg in range(encoder.num_qubits):
                    cnot_var = encoder.cnot_qvars[plan_step][ctrl][trg]
                    if cnot_var in self.sol_map and self.sol_map[cnot_var]:
                        if encoder.options.search_strategy == "backward":
                            if encoder.indicator_vars[plan_step] not in self.sol_map:
                                continue
                            elif self.sol_map[encoder.indicator_vars[plan_step]] == 0:
                                continue
                        self.plan.append(("cnot", "q" + str(ctrl), "q" + str(trg)))
        # last layer single qubit gates:
        for qid in range(encoder.num_qubits):
            [
                i_last,
                h_last,
                p_last,
                hp_last,
                ph_last,
                hph_last,
            ] = encoder.last_single_qvars[qid]
            if i_last in self.sol_map and self.sol_map[i_last]:
                continue
            elif h_last in self.sol_map and self.sol_map[h_last]:
                self.plan.append(("h-gate", "q" + str(qid)))
            elif p_last in self.sol_map and self.sol_map[p_last]:
                self.plan.append(("s-gate", "q" + str(qid)))
            elif hp_last in self.sol_map and self.sol_map[hp_last]:
                self.plan.append(("h-gate", "q" + str(qid)))
                self.plan.append(("s-gate", "q" + str(qid)))
            elif ph_last in self.sol_map and self.sol_map[ph_last]:
                self.plan.append(("s-gate", "q" + str(qid)))
                self.plan.append(("h-gate", "q" + str(qid)))
            else:
                assert hph_last in self.sol_map and self.sol_map[hph_last]
                self.plan.append(("h-gate", "q" + str(qid)))
                self.plan.append(("s-gate", "q" + str(qid)))
                self.plan.append(("h-gate", "q" + str(qid)))

    def __init__(self, options, solver):
        self.options = options
        self.sol_map = solver.sol_map
        self.qubit_map = solver.qubit_map
        self.plan = []
