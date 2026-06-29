from typing import Optional

from pysat.formula import CNFPlus
from pysat.solvers import Solver

from qsynth.ReachabilitySolver.framework.reachability_encoding import ReachabilityEncoding
from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution
from qsynth.ReachabilitySolver.framework.reachability_solver import ReachabilitySolver
from qsynth.ReachabilitySolver.solvers.solver_utils import get_reachability_solution_from_model, \
    bound_number_of_action_variables_to_time_t


def make_k_step_cnf(k: int, reachability_encoding: ReachabilityEncoding) -> CNFPlus:
    cnf = CNFPlus()

    cnf.extend(reachability_encoding.get_initial_state_for_time(0))
    cnf.extend(reachability_encoding.get_goal_state_for_time(k))
    for t in range(k):
        cnf.extend(reachability_encoding.get_transition_predicate_for_time(t))

    return cnf


class KStepTimeStepSolver(ReachabilitySolver):
    """
    Solves a reachability problem by iteratively checking if it can be solved in k steps for increasing values of k.
    The search is unbounded unless an upper_bound is provided in the ReachabilityEncoding.
    """
    def solve(self, reachability_encoding: ReachabilityEncoding) -> Optional[ReachabilitySolution]:
        upper_bound = reachability_encoding.upper_bound
        k = 0
        satisfied = False
        solution = None
        while not satisfied:
            if upper_bound is not None and k > upper_bound:
                break
            cnf = make_k_step_cnf(k, reachability_encoding)
            if reachability_encoding.action_variable_bound is not None:
                cnf.extend(bound_number_of_action_variables_to_time_t(reachability_encoding, k))
            with Solver(name="cd19") as solver:
                solver.append_formula(cnf)
                if solver.solve():
                    satisfied = True
                    model = solver.get_model()
                    solution = get_reachability_solution_from_model(k, reachability_encoding, model)
                else:
                    k += 1
            reachability_encoding.id_pool.restart()
        return solution

