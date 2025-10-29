import os, subprocess
from pathlib import Path


class RunSolvers:
    def remove_existing_files(self):
        # removing existing files from previous run for correctness:
        existing_files = ["qdimacs_out", "dimacs_out", "preprocessor_out", "solver_out"]
        for file in existing_files:
            if hasattr(self.options, file) and os.path.exists(f"self.options.{file}"):
                os.remove(file)

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
            # print("Time out after " + str(self.options.time) + " seconds.")
        except subprocess.CalledProcessError as e:
            # 10, 20 are statuses for SAT and UNSAT:
            if "exit status 10" not in str(e) and "exit status 20" not in str(e):
                print("Error from solver :", e, e.output)
        if not self.timed_out and output_file != None:
            with open(output_file, "w") as f:
                f.write(result.stdout)

    def run_caqe(self):

        if self.options.preprocessor == "bloqqer":
            if os.system("bloqqer -h >" + os.devnull) != 0:
                print(
                    f"Error: preprocessor {self.options.preprocessor} requires executable bloqqer on the path"
                )
                exit(-1)
            preprocessing_command = (
                "bloqqer --timeout=100 "
                + self.options.qdimacs_out
                + " > "
                + self.options.preprocessor_out
            )
            if self.options.verbose > 1:
                print(preprocessing_command)
            os.system(preprocessing_command)

            # if preprocessor solves the instance directly and its a sat instance, we run the solver directly on original instance for plan extraction:
            with open(self.options.preprocessor_out) as f:
                lines = f.readlines()
                header = lines[0].strip("\n")
                num_clauses = int(header.split(" ")[-1])
                if num_clauses == 0:
                    self.options.preprocessor_out = self.options.qdimacs_out
        if os.system("caqe -h >" + os.devnull) != 0:
            print(
                f"Error: solver {self.options.solver} requires executable caqe on the path"
            )
            exit(-1)
        # Handle is preprocessor already solves the instance:
        if self.options.preprocessor != "None":
            command = "caqe --qdo " + self.options.preprocessor_out
        else:
            command = "caqe --qdo " + self.options.qdimacs_out
        if self.options.verbose > 1:
            print(command)
        self.run_command(command, output_file=self.options.solver_out)
        if self.timed_out != True:
            # parse caqe output:
            self.parse_caqe_output()

    # parsing the caqe solver output:
    def parse_caqe_output(self):
        f = open(self.options.solver_out, "r")
        lines = f.readlines()
        # Making sure the state of solution is explicitly specified:
        for line in lines:
            if "c Unsatisfiable" in line:
                self.sat = 0
                return

        for line in lines:
            if "c Satisfiable" in line:
                self.sat = 1
                break

        for line in lines:
            if "V" in line:
                temp = line.split(" ")
                if temp != ["\n"]:
                    literal = temp[1]
                    if int(literal) > 0:
                        self.sol_map[int(literal)] = 1
                    else:
                        self.sol_map[-int(literal)] = 0

    def run_pysat_solvers(self):
        solver_name = self.options.solver.lstrip("pysat-")
        run_solvers_path = os.path.abspath(__file__)
        utilities_path = Path(run_solvers_path).parent
        run_pysat_solver_path = os.path.join(utilities_path, "run_pysat_solver.py")
        command = (
            "python3 "
            + run_pysat_solver_path
            + " --cnf "
            + self.options.dimacs_out
            + " --solver "
            + solver_name
        )
        if self.options.verbose > 1:
            print(command)
        self.run_command(command, self.options.solver_out)
        if self.timed_out != True:
            # parse pysat output:
            f = open(self.options.solver_out, "r")
            lines = f.readlines()
            assert len(lines) == 1, "Error: pysat output should be a single line"
            if lines[0].strip() == "UNSAT":
                self.sat = 0
            else:
                self.sat = 1
                # parsing the solution:
                for literal in lines[0].strip().split(" "):
                    if int(literal) > 0:
                        self.sol_map[int(literal)] = 1
                    else:
                        self.sol_map[-int(literal)] = 0

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
        # we initialize the status with -1, by default unknown:
        self.sat = -1
        self.timed_out = False
        self.remove_existing_files()
