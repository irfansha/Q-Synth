import os
import subprocess
import time
import signal

from abc import ABC, abstractmethod

TMP_FOLDER = "intermediate_files"  # TODO: should be taken from program arguments

OPTIMAL = "optimal"
SATISFYING = "satisfying"

OUTPUT_FILES = [
    f"{TMP_FOLDER}/output.txt",
    *[f"{TMP_FOLDER}/output.txt.{i}" for i in range(50)],
]


class SolverOutput:
    def __init__(self) -> None:
        pass


class SolverSolution(SolverOutput):
    __match_args__ = ("actions",)

    def __init__(self, actions: list[str]):
        self.actions = actions

    def __str__(self):
        return "\n".join(self.actions)


class SolverNoSolution(SolverOutput):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self):
        return "No solution found."


class SolverTimeout(SolverOutput):
    def __init__(self) -> None:
        super().__init__()

    def __str__(self):
        return "Timeout."


class Solver(ABC):
    solver_class: str
    description: str = "No description."
    accepts_conditional: bool

    @abstractmethod
    def command(
        self,
        domain: str,
        problem: str,
        output: str,
        time_limit_s: str,
        min_plan_length: int,
        max_plan_length: int,
        min_layers: int,
        max_layers: int,
    ) -> str:
        """
        `min_plan_length` and `max_plan_length` are the minimum and maximum plan lengths, respectively.

        Parallel plans solvers also accept `min_layers` and `max_layers` as the minimum and maximum number of layers (parallel actions) to take.
        """
        pass

    @abstractmethod
    def parse_actions(self, solution: str) -> list[str]:
        pass

    def solve(
        self,
        domain: str,
        problem: str,
        time_limit_s: int,
        min_plan_length: int,
        max_plan_length: int,
        min_layers: int,
        max_layers: int,
    ) -> tuple[SolverOutput, float]:
        """
        Solve a problem.

        Args
        ----
        - problem (`str`): Problem to solve as a string input to the solver.
        - time_limit_s (`int`): Time limit in seconds.
        - min_plan_length (`int`): Minimum plan length.
        - max_plan_length (`int`): Maximum plan length.
        - min_layers (`int`): Minimum number of layers (parallel actions) to take.
        - max_layers (`int`): Maximum number of layers (parallel actions) to take.

        Returns
        --------
        - `str`: Solution to the problem as a string output from the solver.
        - `float`: Time taken to solve the problem in seconds.
        """

        if not os.path.exists(TMP_FOLDER):
            os.makedirs(TMP_FOLDER)

        domain_file = os.path.join(TMP_FOLDER, "domain.pddl")
        problem_file = os.path.join(TMP_FOLDER, "problem.pddl")
        output_file = os.path.join(TMP_FOLDER, "output.txt")

        for output_file in OUTPUT_FILES:
            if os.path.exists(output_file):
                os.remove(output_file)

        with open(domain_file, "w") as f:
            f.write(domain)

        with open(problem_file, "w") as f:
            f.write(problem)

        command = self.command(
            domain_file,
            problem_file,
            OUTPUT_FILES[0],
            str(time_limit_s + 100),
            min_plan_length,
            max_plan_length,
            min_layers,
            max_layers,
        )
        start = time.time()
        try:
            p = subprocess.Popen(
                command,
                start_new_session=True,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            p.wait(timeout=time_limit_s)
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            return SolverTimeout(), time_limit_s
        except KeyboardInterrupt:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            p.wait()
            raise KeyboardInterrupt

        end = time.time()
        elapsed = end - start

        solution_produced = any(
            os.path.exists(output_file) for output_file in OUTPUT_FILES
        )

        if not solution_produced:
            return SolverNoSolution(), elapsed

        # get latest output file
        output_file = max(
            OUTPUT_FILES, key=lambda p: os.path.getctime(p) if os.path.exists(p) else 0
        )
        with open(output_file, "r") as f:
            solution = f.read()

        actions = self.parse_actions(solution)
        return SolverSolution(actions), elapsed


class FAST_DOWNWARD_MERGE_AND_SHRINK(Solver):
    solver_class = OPTIMAL
    description = "The Fast-Downward Merge and Shrink planner.\nSource: https://www.fast-downward.org"
    accepts_conditional = True

    def command(
        self,
        domain: str,
        problem: str,
        output: str,
        time_limit_s: str,
        min_plan_length: int,
        max_plan_length: int,
        min_layers: int,
        max_layers: int,
    ) -> str:
        return f"fast-downward.py --plan-file {output} --overall-time-limit {time_limit_s}s {domain} {problem} --search 'astar(merge_and_shrink(merge_strategy=merge_precomputed(merge_tree=linear(variable_order=reverse_level)),shrink_strategy=shrink_bisimulation(greedy=true),label_reduction=exact(before_shrinking=true,before_merging=false),max_states=infinity,threshold_before_merge=1))'"

    def parse_actions(self, solution: str) -> list[str]:
        lines = solution.strip().split("\n")
        without_cost_line = lines[:-1]
        without_parentheses = [line[1:-1] for line in without_cost_line]
        actions_as_parts = [line.split(" ") for line in without_parentheses]
        actions = [
            f"{parts[0]}({','.join([p for p in parts[1:]])})"
            for parts in actions_as_parts
        ]
        return actions

    def solve(
        self,
        domain: str,
        problem: str,
        time_limit_s: int,
        min_plan_length: int,
        max_plan_length: int,
        min_layers: int,
        max_layers: int,
    ) -> tuple[SolverOutput, float]:

        # Test if fast-downward is on path
        if os.system("fast-downward.py -v >" + os.devnull) != 0:
            print(
                "Error: model 'fd-ms'  requires executable 'fast-downward.py' on the path"
            )
            return SolverNoSolution(), 0.0
        return super().solve(
            domain,
            problem,
            time_limit_s,
            min_plan_length,
            max_plan_length,
            min_layers,
            max_layers,
        )


class FAST_DOWNWARD_BJOLP(Solver):
    solver_class = OPTIMAL
    description = (
        "The Fast-Downward BJOLP planner.\nSource: https://www.fast-downward.org"
    )
    accepts_conditional = False

    def command(
        self,
        domain: str,
        problem: str,
        output: str,
        time_limit_s: str,
        min_plan_length: int,
        max_plan_length: int,
        min_layers: int,
        max_layers: int,
    ) -> str:
        return f"fast-downward.py --alias seq-opt-bjolp --plan-file {output} --overall-time-limit {time_limit_s}s {domain} {problem}"

    def parse_actions(self, solution: str) -> list[str]:
        lines = solution.strip().split("\n")
        without_cost_line = lines[:-1]
        without_parentheses = [line[1:-1] for line in without_cost_line]
        actions_as_parts = [line.split(" ") for line in without_parentheses]
        actions = [
            f"{parts[0]}({','.join([p for p in parts[1:]])})"
            for parts in actions_as_parts
        ]
        return actions

    def solve(
        self,
        domain: str,
        problem: str,
        time_limit_s: int,
        min_plan_length: int,
        max_plan_length: int,
        min_layers: int,
        max_layers: int,
    ) -> tuple[SolverOutput, float]:

        # Test if fast-downward is on path
        if os.system("fast-downward.py -v >" + os.devnull) != 0:
            print(
                "Error: model 'fd-bjolp'  requires executable 'fast-downward.py' on the path"
            )
            return SolverNoSolution(), 0.0
        return super().solve(
            domain,
            problem,
            time_limit_s,
            min_plan_length,
            max_plan_length,
            min_layers,
            max_layers,
        )
