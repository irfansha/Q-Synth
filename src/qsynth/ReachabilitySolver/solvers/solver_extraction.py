from enum import Enum

from qsynth.ReachabilitySolver.solvers.inc_solver import IncTimeStepSolver
from qsynth.ReachabilitySolver.solvers.ind_solvers import GoingUpTimeStepSolver, GoingDownTimeStepSolver, \
    FromMiddleTimeStepSolver, \
    AtMostTimeStepSolver, BinaryTimeStepSolver, MaxSatSolver, MaxSatTimeStepSolver, MaxSatActionVarSolver
from qsynth.ReachabilitySolver.solvers.k_step_solver import KStepTimeStepSolver
from qsynth.ReachabilitySolver.solvers.minimize_action_var_solvers import BackwardActionVarSolver, \
    ForwardActionVarSolver


def get_solver_for_strategy(strategy, minimize="time_steps", intermediate_solution_path=None):
    """
    Returns a ReachabilitySolver instance implementing the given strategy.
    Args:
        strategy (str): The strategy to use, defaults to "forward".
        minimize (str): Either "time_steps" or "action_vars". Defaults to "time_steps".
        intermediate_solution_path (str): Path to intermediate solution files.
    """
    if minimize not in ["time_steps", "action_vars"]:
        raise ValueError(f"Unknown minimization target: {minimize}")
    strategy = strategy.translate(str.maketrans("", "", "-_ "))  # remove -, _ and spaces
    if minimize == "time_steps":
        if strategy in ["forward", "kstep"]:
            return KStepTimeStepSolver()
        elif strategy == "kstep":
            return KStepTimeStepSolver()
        elif strategy == "inc":
            return IncTimeStepSolver()
        elif strategy == "goingup":
            return GoingUpTimeStepSolver()
        elif strategy in ["backward", "goingdown"]:
            return GoingDownTimeStepSolver(intermediate_solution_path)
        elif strategy == "frommiddle":
            return FromMiddleTimeStepSolver(intermediate_solution_path)
        elif strategy == "atmost":
            return AtMostTimeStepSolver(intermediate_solution_path)
        elif strategy == "binary":
            return BinaryTimeStepSolver(intermediate_solution_path)
        elif strategy == "maxsat":
            return MaxSatTimeStepSolver()
        else:
            raise ValueError(f"Unknown solving strategy, {strategy}, for minimizing {minimize}")
    elif minimize == "action_vars":
        if strategy == "forward":
            return ForwardActionVarSolver()
        elif strategy in ["backward", "goingdown"]:
            return BackwardActionVarSolver(intermediate_solution_path)
        elif strategy == "maxsat":
            return MaxSatActionVarSolver()
        else:
            raise ValueError(f"Unknown solving strategy, {strategy}, for minimizing {minimize}")
    else:
        raise ValueError(f"Unknown minimization target: {minimize}")


class ReachabilitySolverNames(Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    K_STEP = "kstep"
    INC = "inc"
    GOING_UP = "goingup"
    GOING_DOWN = "goingdown"
    FROM_MIDDLE = "frommiddle"
    ATMOST = "atmost"
    BINARY = "binary"
    MAXSAT = "maxsat"

    @staticmethod
    def is_valid(solver_name):
        solver_name = solver_name.translate(str.maketrans("", "", "-_ "))  # remove -, _ and spaces
        return solver_name in set(solver.value for solver in ReachabilitySolverNames)
