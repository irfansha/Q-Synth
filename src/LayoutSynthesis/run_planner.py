# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

import os


class RunPlanner:

    def choose_domain_file(self):
        domain = None
        # Global and Lifted models use a fixed domain file (choice depends also on ancillary bits)
        # Local models use a generated domain file
        if self.args.model == "global":
            domain = os.path.join(self.args.domains, "global-domain")
        elif self.args.model == "lifted":
            domain = os.path.join(self.args.domains, "lifted")
            if self.args.relaxed == 1:
                domain += "-relaxed"
            else:
                domain += "-strict"
                if self.args.bridge == 1:
                    domain += "-bridge"
        elif "local" in self.args.model:
            return (
                self.args.pddl_domain_out
            )  # NOTE: here we return directly, independent of ancillary
        else:
            print(f"Error: model {self.args.model} is not understood")
            exit(-1)
        if not self.args.allow_ancillas:
            return domain + "-noanc.pddl"
        else:
            return domain + ".pddl"

    def run_fdownward(self):
        # removing existing plan for correctness:
        if os.path.exists(self.args.plan_file):
            os.remove(self.args.plan_file)
        if self.args.solver == "fd-bjolp":
            planner_options = "--alias seq-opt-bjolp"
        elif self.args.solver == "fd-ms":
            planner_options = "--alias seq-opt-merge-and-shrink"
        elif self.args.solver == "fd-lmcut":
            planner_options = "--alias seq-opt-lmcut"
        elif self.args.solver == "fdss-sat":
            planner_options = "--alias seq-sat-fdss-2018 --portfolio-single-plan"
        elif self.args.solver == "fdss-opt":
            planner_options = "--alias seq-opt-fdss-1"
        elif self.args.solver == "fdss-opt-2":
            planner_options = "--alias seq-opt-fdss-2"

        domain = self.choose_domain_file()

        if os.system("fast-downward.py -v >" + os.devnull) != 0:
            print(
                f"Error: planner {self.args.solver} requires executable 'fast-downward.py' on the path"
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
            + domain
            + " "
            + self.args.pddl_problem_out
            + " > "
            + self.args.log_out
        )
        if self.args.verbose > 0:
            print(command, flush=True)
        os.system(command)

    def run_madagascar_optimal(self):
        domain = self.choose_domain_file()
        plan_length = self.pddl_instance.num_actions
        if os.system("M >" + os.devnull) != 0:
            print(
                f"Error: planner {self.args.solver} requires executable 'M' (Madagascar) on the path"
            )
            exit(-1)
        while 1:
            command = (
                "M -P 0 -F "
                + str(plan_length)
                + " -T "
                + str(plan_length)
                + " -o "
                + self.args.plan_file
                + " -t "
                + str(int(self.args.time))
                + " "
                + domain
                + " "
                + self.args.pddl_problem_out
                + " > "
                + self.args.log_out
            )
            print(command)
            os.system(command)
            # check if the plan is not found:
            with open(self.args.log_out) as file:
                contents = file.read()
                # we loop until we find a plan:
                if "PLAN NOT FOUND" not in contents:
                    break
                else:
                    plan_length += 1

    def parse_fdplan(self):
        try:
            f = open(self.args.plan_file, "r")
            lines = f.readlines()
            f.close()
        except FileNotFoundError:
            self.plan = None
            return

        self.plan = []
        for line in lines:
            # only if not a commit:
            if ";" not in line:
                self.plan.append(line.strip(")\n").strip("()").split(" "))
                # print(line)

    def parse_Mplan(self):
        try:
            f = open(self.args.plan_file, "r")
            lines = f.readlines()
            f.close()
        except FileNotFoundError:
            self.plan = None
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

    # Parses domain and problem file:
    def __init__(self, args, pddl_instance):
        self.args = args
        self.pddl_instance = pddl_instance

        if "fd" in self.args.solver:
            self.run_fdownward()
            self.parse_fdplan()
        elif "madagascar" == self.args.solver:
            self.run_madagascar_optimal()
            self.parse_Mplan()
        else:
            print(f"Error: solver {self.args.solver} is not understood")
            exit(-1)
