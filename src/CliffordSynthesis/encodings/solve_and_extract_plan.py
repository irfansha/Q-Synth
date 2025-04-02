import os, subprocess
from src.CnotSynthesis.encodings.generate_initial_swaps import (
    extract_swaps_for_initial_mapping,
)


class SolveandExtractPlan:

    def remove_existing_files(self):
        # removing existing files from previous run for correctness:
        existing_files = [self.options.dimacs_out, self.options.solver_out]
        for file in existing_files:
            if os.path.exists(file):
                os.remove(file)

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
                        if encoder.options.optimal_search == "b":
                            if encoder.indicator_vars[plan_step] not in self.sol_map:
                                continue
                            elif self.sol_map[encoder.indicator_vars[plan_step]] == 0:
                                continue
                        self.plan.append(("cnot", "q" + str(ctrl), "q" + str(trg)))
        # last layer single qubit gates:
        for qid in range(encoder.num_qubits):
            [i_last, h_last, p_last, hp_last, ph_last, hph_last] = (
                encoder.last_single_qvars[qid]
            )
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

    def run_command(self, command, output_file=None):
        result = None
        try:
            result = subprocess.run(
                command.split(),
                shell=False,
                capture_output=True,
                text=True,
                timeout=self.options.remaining_time,
            )
        except subprocess.TimeoutExpired:
            self.timed_out = True
            print("Time out after " + str(self.options.time) + " seconds.")
        except subprocess.CalledProcessError as e:
            # 10, 20 are statuses for SAT and UNSAT:
            if "exit status 10" not in str(e) and "exit status 20" not in str(e):
                print("Error from solver :", e, e.output)
        if not self.timed_out and output_file != None:
            with open(output_file, "w") as f:
                f.write(result.stdout)

    def run_cadical(self):

        if os.system("cadical -h >" + os.devnull) != 0:
            print(
                f"Error: solver {self.options.solver} requires executable cadical on the path"
            )
            exit(-1)
        command = "cadical -q " + self.options.dimacs_out
        if self.options.verbose > 1:
            print(command)
        self.run_command(command, self.options.solver_out)
        if self.timed_out != True:
            # parse caqe output:
            self.parse_cadical_output()

    # parsing the caqe solver output:
    def parse_cadical_output(self):
        f = open(self.options.solver_out, "r")
        lines = f.readlines()
        # Making sure the state of solution is explicitly specified:
        for line in lines:
            if "s UNSATISFIABLE" in line:
                self.sat = 0
                return

        for line in lines:
            if "s SATISFIABLE" in line:
                self.sat = 1
                break

        for line in lines:
            if "v" in line:
                # stripping empty space and trailing '\n', mainly for mallob:
                line = line.strip(" \n")
                single_line_assignments = line.split(" ")
                # ignoring first element with v:
                for cur_assignment in single_line_assignments[1:]:
                    literal = cur_assignment.strip("\n")
                    if int(literal) > 0:
                        self.sol_map[int(literal)] = 1
                    else:
                        self.sol_map[-int(literal)] = 0

    # gimsatul, a parallel sat solver:
    def run_gimsatul(self):
        if os.system("gimsatul -h >" + os.devnull) != 0:
            print(
                f"Error: solver {self.options.solver} requires executable gimsatul on the path"
            )
            exit(-1)
        assert self.options.nthreads >= 1, "Error: number of threads must be atleast 1"
        command = (
            f"gimsatul -q --threads={self.options.nthreads} {self.options.dimacs_out}"
        )
        if self.options.verbose > 1:
            print(command)
        self.run_command(command, self.options.solver_out)
        if self.timed_out != True:
            # parse gimsatul output, same as cadical parsing:
            self.parse_cadical_output()

    # mallob, a parallel sat solver:
    def run_mallob(self):
        if os.system("./mallob/build/mallob -h >" + os.devnull) != 0:
            print(
                f"Error: solver {self.options.solver} requires installed mallob in the QSynth folder"
            )
            exit(-1)
        assert self.options.nthreads >= 1, "Error: number of threads must be atleast 1"
        cwd = os.getcwd()
        os.chdir(os.path.join(cwd, "mallob"))
        if self.options.verbose > 1:
            print("Entering mallob directory")
        command = f"./build/mallob -satsolver='(kc)*' -t={self.options.nthreads} -mono={self.options.dimacs_out} -s2f={self.options.solver_out}"
        if self.options.verbose > 1:
            print(command)
        self.run_command(command)
        os.chdir(cwd)
        if self.options.verbose > 1:
            print("Exited mallob directory")
        if self.timed_out != True:
            # parse gimsatul output, same as cadical parsing:
            self.parse_cadical_output()

    def __init__(self, options):
        self.options = options
        self.sol_map = {}
        self.qubit_map = {}
        self.plan = []
        # we initialize the status with -1, by default unknown:
        self.sat = -1
        self.timed_out = False
        self.remove_existing_files()
