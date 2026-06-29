import os
import glob


class RunPlanner:

    def run_madagascar(self, heur):
        # for now running and parsing sequential plans:
        # removing existing plan for correctness:
        if os.path.exists(self.args.plan_file):
            os.remove(self.args.plan_file)
        if (heur == "M"):
            if os.system("M >" + os.devnull) != 0:
                print(f"Error: planner {self.args.solver} requires executable 'M' (Madagascar) on the path")
                exit(-1)
            command = "M -P 0 -o " + self.args.plan_file + " -t "+ str(int(self.args.time)) +" " +  self.args.pddl_domain_out + " " + self.args.pddl_problem_out +" > " + self.args.log_out
        elif (heur == "MpC"):
            if os.system("MpC >" + os.devnull) != 0:
                print(f"Error: planner {self.args.solver} requires executable 'MpC' (Madagascar) on the path")
                exit(-1)
            if self.args.encoding != "normalform":
                plan_bound = self.args.oneq_gate_count + self.args.twoq_gate_count
                command = "Mp -o " + self.args.plan_file + " -T " + str(plan_bound) + " -t "+ str(int(self.args.time)) +" " +  self.args.pddl_domain_out + " " + self.args.pddl_problem_out + " > " + self.args.log_out
            else:
                command = "Mp -o " + self.args.plan_file + " -t "+ str(int(self.args.time)) +" " +  self.args.pddl_domain_out + " " + self.args.pddl_problem_out + " > " + self.args.log_out
        print(command)
        os.system(command)
        
    def run_madagascar_optimal(self, mode, heur):
        # removing existing plan for correctness:
        if os.path.exists(self.args.plan_file):
            os.remove(self.args.plan_file)
        if os.system(heur + " >" + os.devnull) != 0:
            print(
                f"Error: planner {self.args.planner} requires executable '"
                + heur
                + "' (Madagascar) on the path"
            )
            exit(-1)
        # plan horizon, starting with 0:
        plan_length = 0
        while True:
            command = (
                heur
                + " -1 " # enforcing atleast one action per time step
                + " -P "
                + str(mode)
                + " -F "
                + str(plan_length)
                + " -T "
                + str(plan_length)
                + " -o "
                + self.args.plan_file
                + " -t "
                + str(int(self.args.time))
                + " "
                + self.args.pddl_domain_out
                + " "
                + self.args.pddl_problem_out
                + " > "
                + self.args.log_out
            )
            #print(command)
            os.system(command)
            # check if the plan is not found:
            with open(self.args.log_out) as file:
                contents = file.read()
                # we loop until we find a plan:
                if "PLAN NOT FOUND" not in contents:
                    break
                else:
                    plan_length = plan_length + 1

    def run_fdownward(self):
        # removing existing plan for correctness:
        if os.path.exists(self.args.plan_file):
            os.remove(self.args.plan_file)
        if self.args.planner == "fdss-sat":
            planner_options = "--alias seq-sat-fdss-2023 --portfolio-single-plan"
        elif self.args.planner == "fd-ms":
            planner_options = "--alias seq-opt-merge-and-shrink"
        elif self.args.planner == "lama":
            planner_options = "--alias lama"

        if os.system("fast-downward.py -v >" + os.devnull) != 0:
            print(
                f"Error: planner {self.args.planner} requires executable 'fast-downward.py' on the path"
            )
            exit(-1)
        command = (
            "fast-downward.py "
            + planner_options
            + " --log-level warning --plan-file "
            + self.args.plan_file
            + " --sas-file "
            + self.args.SAS_file
            + "  --overall-time-limit "
            + str(int(self.args.time))
            + "s "
            #+ "--overall-memory-limit "
            #+ "8000M "
            + self.args.pddl_domain_out
            + " "
            + self.args.pddl_problem_out
            + " > "
            + self.args.log_out
        )
        if self.args.verbose > 1:
            print(command, flush=True)
        os.system(command)

    def run_scorpion(self):
        # removing existing plan for correctness:
        if os.path.exists(self.args.plan_file):
            os.remove(self.args.plan_file)
        # assumes scorpion version of fast-downward is installed, and symbolical link 'scorpion' points to the installation directory:
        if os.system("scorpion.py -v >" + os.devnull) != 0:
            print(
                f"Error: planner {self.args.planner} requires executable 'scorpion.py' on the path"
            )
            exit(-1)
        command = (
            "scorpion.py "
            + " --log-level warning --plan-file "
            + self.args.plan_file
            + " --sas-file "
            + self.args.SAS_file
            + "  --overall-time-limit "
            + str(int(self.args.time))
            + "s "
            #+ "--overall-memory-limit "
            #+ "8000M "
            + self.args.pddl_domain_out
            + " "
            + self.args.pddl_problem_out
            + f' --search "astar(max_cp_ms(shrink_strategy=shrink_bisimulation(greedy=false),label_reduction=exact(before_shrinking=true,before_merging=false),merge_strategy=merge_sccs(order_of_sccs=topological,merge_selector=score_based_filtering(scoring_functions=[goal_relevance,dfp,total_order(atomic_ts_order=reverse_level,product_ts_order=new_to_old,atomic_before_product=true)])),max_states=50K,threshold_before_merge=1,main_loop_max_time={int(self.args.time/2)},cost_partitioning=scp(order_generator=greedy_orders(random_seed=2020,scoring_function=max_heuristic_per_stolen_costs)),compute_atomic_snapshot=false,main_loop_target_num_snapshots=0,main_loop_snapshot_each_iteration=0,atomic_label_reduction=false,snapshot_moment=after_label_reduction,filter_trivial_factors=true,offline_cps=false))"'
            + " > "
            + self.args.log_out
        )
        if self.args.verbose > 1:
            print(command, flush=True)
        os.system(command)


    def run_symk(self):
        # removing existing plan for correctness:
        if os.path.exists(self.args.plan_file):
            os.remove(self.args.plan_file)
        # assumes symk version of fast-downward is installed, and symbolical link 'symk' points to the installation directory:
        if os.system("symk.py -v >" + os.devnull) != 0:
            print(
                f"Error: planner {self.args.planner} requires executable 'symk.py' on the path"
            )
            exit(-1)
        command = (
            "symk.py "
            + " --log-level warning --plan-file "
            + self.args.plan_file
            + " --sas-file "
            + self.args.SAS_file
            + "  --overall-time-limit "
            + str(int(self.args.time))
            + "s "
            #+ "--overall-memory-limit "
            #+ "8000M "
            + self.args.pddl_domain_out
            + " "
            + self.args.pddl_problem_out
            + ' --search "sym_bd()" '
            + " > "
            + self.args.log_out
        )
        if self.args.verbose > 1:
            print(command, flush=True)
        os.system(command)

    def parse_fdplan(self):
        # for lama, the plan files of the format plan.*
        # we need the plan file with largest index (if it exists):
        if "lama" in self.args.planner:
            files_list = glob.glob(self.args.plan_file + ".*")
            max_file_index = -1
            plan_file = self.args.plan_file
            for filename in files_list:
                cur_index = int(filename.split(".")[-1])
                if max_file_index < cur_index:
                    max_file_index = cur_index
                    plan_file = filename

            self.args.plan_file = plan_file

        try:
            f = open(self.args.plan_file, "r")
            lines = f.readlines()
            f.close()
        except FileNotFoundError:
            if self.args.verbose > 0:
                print(f"No plan could be found.")
            self.plan = None
            return
        self.plan = []
        for line in lines:
            # only if not a commit:
            if ";" not in line:
                self.plan.append(line.strip(")\n").strip("()").split(" "))
                # print(line)
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
            # print(new_action_list)

    def parse_MpCplan(self):
        try:
            f = open(self.args.plan_file, "r")
            lines = f.readlines()
            f.close()
        except FileNotFoundError:
            print(f"No plan could be found.")
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

        if "fd" in self.args.planner or "lama" in self.args.planner:
            self.run_fdownward()
            self.parse_fdplan()
        elif "scorpion" in self.args.planner:
            # scorpion uses different version of fast-downward:
            self.run_scorpion()
            self.parse_fdplan()
        elif "symk" in self.args.planner:
            # symk planner uses different version of fast-downward:
            self.run_symk()
            self.parse_fdplan()
        elif "madagascar" == self.args.planner:
            # sequential plans
            self.run_madagascar_optimal(0, "M")
            self.parse_Mplan()
        elif "madagascar-mpc" == self.args.planner:
            # parallel plans
            self.run_madagascar("MpC")
            self.parse_MpCplan()
        else:
            assert False, "choose fd-ms, lama or madagascar planner"
