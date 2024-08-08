import os, subprocess
from src.CnotSynthesis.encodings.generate_initial_swaps import extract_swaps_for_initial_mapping

class SolveandExtractPlan:

  def remove_existing_files(self):
    # removing existing files from previous run for correctness:
    existing_files = [self.options.qdimacs_out, self.options.dimacs_out, self.options.preprocessor_out, self.options.solver_out]
    for file in existing_files:
      if os.path.exists(file):
        os.remove(file)

  def extract_initial_map(self, encoder):
    initial_time_step = 0
    for qid in range(encoder.num_qubits):
      for row_id in range(encoder.num_qubits):
        cell_var = encoder.cells[initial_time_step][row_id][qid]
        if(self.sol_map[cell_var]):
          self.qubit_map[qid] = row_id
          break
    extract_swaps_for_initial_mapping(self.qubit_map, self.plan, encoder.num_qubits)

  def extract_depth_optimal_plan(self, encoder):
    if (self.options.qubit_permute == True):
      self.extract_initial_map(encoder)
    for cnot_list in encoder.cnot_variables:
      for cnot_var_id in range(len(cnot_list)):
        cnot_var = cnot_list[cnot_var_id]
        # if preprocessor removes some variables, we assume they are false:
        if cnot_var not in self.sol_map:
          continue
        if self.sol_map[cnot_var]:
          qubit1, qubit2 = encoder.control_target_dict[cnot_var_id]
          self.plan.append(('cnot','q'+str(qubit1), 'q'+str(qubit2)))

  def extract_cnot_optimal_plan(self, encoder):
    if (self.options.qubit_permute == True):
      self.extract_initial_map(encoder)
    for plan_step in range(encoder.options.plan_length):
      cnot_qubit1, cnot_qubit2 = -1, -1
      for qid in range(encoder.num_qubits):
        cnot_control_var = encoder.control_qvars[plan_step][qid]
        if cnot_control_var not in self.sol_map: continue
        if (self.sol_map[cnot_control_var]):
          cnot_qubit1 = qid
      for qid in range(encoder.num_qubits):
        cnot_target_var = encoder.target_qvars[plan_step][qid]
        if cnot_target_var not in self.sol_map: continue
        if (self.sol_map[cnot_target_var]):
          cnot_qubit2 = qid

      self.plan.append(('cnot','q'+str(cnot_qubit1), 'q'+str(cnot_qubit2)))

  def run_command(self, command):
    try:
      subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True, timeout=self.options.remaining_time)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.options.time)+ " seconds.")
    except subprocess.CalledProcessError as e:
      # 10, 20 are statuses for SAT and UNSAT:
      if ("exit status 10" not in str(e) and "exit status 20"  not in str(e)):
        print("Error from solver :", e, e.output)

  def run_caqe(self):

    if self.options.preprocessor == 'bloqqer':
      if os.system("bloqqer -h >" + os.devnull) != 0:
          print(f"Error: preprocessor {self.options.preprocessor} requires executable bloqqer on the path")
          exit(-1)
      preprocessing_command = "bloqqer --timeout=100 " + self.options.qdimacs_out + " > " + self.options.preprocessor_out
      if self.options.verbose > 1: print(preprocessing_command)
      os.system(preprocessing_command)

      # if preprocessor solves the instance directly and its a sat instance, we run the solver directly on original instance for plan extraction:
      with open(self.options.preprocessor_out) as f:
        lines = f.readlines()
        header = lines[0].strip("\n")
        num_clauses =  int(header.split(" ")[-1])
        if (num_clauses == 0):
          self.options.preprocessor_out = self.options.qdimacs_out
    if os.system("caqe -h >" + os.devnull) != 0:
        print(f"Error: solver {self.options.solver} requires executable caqe on the path")
        exit(-1)
    # Handle is preprocessor already solves the instance:
    if self.options.preprocessor != 'None':
      command = "caqe --qdo " + self.options.preprocessor_out + " > " + self.options.solver_out
    else:
      command = "caqe --qdo " + self.options.qdimacs_out + " > " + self.options.solver_out
    if self.options.verbose > 1: print(command)
    
    self.run_command(command)

    if (self.timed_out != True):
      # parse caqe output:
      self.parse_caqe_output()


  # parsing the caqe solver output:
  def parse_caqe_output(self):
    f = open(self.options.solver_out, 'r')
    lines = f.readlines()
    # Printing the data to the output for correctness purposes:
    '''
    for line in lines:
      #if (line != '\n' and 'V' not in line):
      if (line != '\n'):
        nline = line.strip("\n")
        print(nline)
    '''
    # Making sure the state of solution is explicitly specified:
    for line in lines:
      if ('c Unsatisfiable' in line):
        self.sat = 0
        return

    for line in lines:
      if ('c Satisfiable' in line):
        self.sat = 1
        break

    for line in lines:
      if ('V' in line):
        temp = line.split(" ")
        if (temp != ['\n']):
          literal = temp[1]
          if int(literal) > 0:
            self.sol_map[int(literal)] = 1
          else:
            self.sol_map[-int(literal)] = 0

  def run_cadical(self):

    if os.system("cadical -h >" + os.devnull) != 0:
        print(f"Error: solver {self.options.solver} requires executable cadical on the path")
        exit(-1)
    command = "cadical -q " + self.options.dimacs_out + " > " + self.options.solver_out
    if self.options.verbose > 1: print(command)
    self.run_command(command)
    if (self.timed_out != True):
      # parse caqe output:
      self.parse_cadical_output()

  # parsing the caqe solver output:
  def parse_cadical_output(self):
    f = open(self.options.solver_out, 'r')
    lines = f.readlines()
    # Making sure the state of solution is explicitly specified:
    for line in lines:
      if ('s UNSATISFIABLE' in line):
        self.sat = 0
        return

    for line in lines:
      if ('s SATISFIABLE' in line):
        self.sat = 1
        break

    for line in lines:
      if ('v' in line):
        single_line_assignments = line.split(" ")
        # ignoring first element with v:
        for cur_assignment in single_line_assignments[1:]:
          literal = cur_assignment.strip("\n")
          if int(literal) > 0:
            self.sol_map[int(literal)] = 1
          else:
            self.sol_map[-int(literal)] = 0

  def __init__(self, options):
    self.options = options
    self.sol_map = {}
    self.qubit_map = {}
    self.plan = []
    # we initialize the status with -1, by default unknown:
    self.sat = -1
    self.timed_out = False
    self.remove_existing_files()

