import os
import glob


class RunPlanner:

  def run_madagascar_optimal(self,mode, heur):
    # removing existing plan for correctness:
    if os.path.exists(self.args.plan_file):
      os.remove(self.args.plan_file)
    if os.system(heur + " >" + os.devnull) != 0:
        print(f"Error: planner {self.args.planner} requires executable '" + heur +  "' (Madagascar) on the path")
        exit(-1)
    # plan horizon, starting with 0:
    plan_length = 0
    while(True):
      command = heur + " -P " + str(mode) + " -F " + str(plan_length) + " -T " + str(plan_length) + " -o " + self.args.plan_file +" -t "+ str(int(self.args.time)) +" " +  self.args.pddl_domain_out + " " + self.args.pddl_problem_out + " > " + self.args.log_out
      print(command)
      os.system(command)
      # check if the plan is not found:
      with open(self.args.log_out) as file:
        contents = file.read()
        # we loop until we find a plan:
        if ("PLAN NOT FOUND" not in contents):
          break
        else:
          plan_length = plan_length + 1

  def run_fdownward(self):
    # removing existing plan for correctness:
    if os.path.exists(self.args.plan_file):
      os.remove(self.args.plan_file)
    if (self.args.planner == "fdss-sat"):
      planner_options = "--alias seq-sat-fdss-2023 --portfolio-single-plan"
    elif(self.args.planner == "fd-ms"):
      planner_options = '--alias seq-opt-merge-and-shrink'
    elif(self.args.planner == "lama"):
      planner_options = '--alias lama'

    if os.system("fast-downward.py -v >" + os.devnull) != 0:
       print(f"Error: planner {self.args.planner} requires executable 'fast-downward.py' on the path")
       exit(-1)
    command = "fast-downward.py "+ planner_options +" --log-level warning --plan-file " + self.args.plan_file + " --sas-file " +self.args.SAS_file + "  --overall-time-limit "+ str(int(self.args.time)) +"s " + self.args.pddl_domain_out + " " +self.args.pddl_problem_out +" > " +self.args.log_out
    if self.args.verbose > 1: print(command, flush=True)
    os.system(command)


  def run_scorpion(self):
    # removing existing plan for correctness:
    if os.path.exists(self.args.plan_file):
      os.remove(self.args.plan_file)

    if os.system("fast-downward.py -v >" + os.devnull) != 0:
       print(f"Error: planner {self.args.planner} requires executable 'fast-downward.py' on the path")
       exit(-1)
    command = 'fast-downward.py ' + " --log-level warning --plan-file " + self.args.plan_file + " --sas-file " +self.args.SAS_file + "  --overall-time-limit "+ str(int(self.args.time)) +"s " + \
    '--transform-task preprocess-h2 '+ self.args.pddl_domain_out + " " +self.args.pddl_problem_out +\
    ' --search "astar(scp_online([projections(sys_scp('+\
    ' max_time=100, max_time_per_restart=10, max_pdb_size=2M, max_collection_size=20M,'+\
    '  pattern_type=interesting_non_negative, create_complete_transition_system=true),'+\
    ' create_complete_transition_system=true)],'+\
    'saturator=perimstar, max_time=100, max_size=1M, interval=10K, orders=greedy_orders()))"'  + " > " +self.args.log_out
    if self.args.verbose > 1: print(command, flush=True)
    os.system(command)


  def parse_fdplan(self):
    # for lama, the plan files of the format plan.*
    # we need the plan file with largest index (if it exists):
    if ("lama" in self.args.planner):
      files_list = glob.glob(self.args.plan_file + ".*")
      max_file_index = -1
      plan_file = self.args.plan_file
      for filename in files_list:
        cur_index = int(filename.split(".")[-1])
        if max_file_index < cur_index:
          max_file_index = cur_index
          plan_file =  filename
      
      self.args.plan_file = plan_file

    try:
      f = open(self.args.plan_file, "r")
      lines = f.readlines()
      f.close()
    except FileNotFoundError:
      if self.args.verbose > 0 : print(f"No plan could be found.")
      self.plan = None
      return
    self.plan = []
    for line in lines:
      # only if not a commit:
      if (";" not in line):
        self.plan.append(line.strip(")\n").strip("()").split(" "))
        #print(line)
    return self.plan

  def parse_Mplan(self):
    try:
      f = open(self.args.plan_file, "r")
      lines = f.readlines()
      f.close()
    except FileNotFoundError:
      print(f"No plan could be found.")
      return
    self.plan = []
    for line in lines:
      [action_name, parameters] = line.split(" ")[-1].strip(")\n").split("(")
      paramters_list = parameters.split(",")
      new_action_list = []
      new_action_list.append(action_name)
      new_action_list.extend(paramters_list)
      self.plan.append(new_action_list)
      #print(new_action_list)

  def parse_MpCplan(self):
    try:
      f = open(self.args.plan_file, "r")
      lines = f.readlines()
      f.close()
    except FileNotFoundError:
      print(f"No plan could be found.")
      self.plan = None
      return
    self.plan = []
    for line in lines:
      plan_step, actions = line.split(": ")
      #print(plan_step,actions)
      actions_list = actions.strip("\n").split(" ")
      for action in actions_list:
        [action_name, parameters] = action.split(" ")[-1].strip(")\n").split("(")
        paramters_list = parameters.split(",")
        new_action_list = []
        new_action_list.append(action_name)
        new_action_list.extend(paramters_list)
        self.plan.append(new_action_list)
        #print(new_action_list)

  # Parses domain and problem file:
  def __init__(self, args):
    self.args = args

    if ("fd" in self.args.planner or "lama" in self.args.planner):
      self.run_fdownward()
      self.parse_fdplan()
    elif (self.args.planner == "scorpion"):
      self.run_scorpion()
      self.parse_fdplan()
    elif("M-seq-optimal" == self.args.planner):
      # sequential plans
      self.run_madagascar_optimal(0, "M")
      self.parse_Mplan()
    elif("Mp-seq-optimal" == self.args.planner):
      # sequential plans
      self.run_madagascar_optimal(0, "Mp")
      self.parse_Mplan()
    elif("M-parA-optimal" == self.args.planner):
      # A-step parallel plans
      self.run_madagascar_optimal(1, "M")
      self.parse_MpCplan()
    elif("M-parE-optimal" == self.args.planner):
      # E-step parallel plans
      self.run_madagascar_optimal(2, "M")
      self.parse_MpCplan()