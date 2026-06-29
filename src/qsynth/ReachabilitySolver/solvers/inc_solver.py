from typing import Optional

from pysat.card import CardEnc, ITotalizer
from pysat.formula import CNFPlus
from pysat.solvers import Solver

from qsynth.ReachabilitySolver.framework.reachability_encoding import ReachabilityEncoding
from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution
from qsynth.ReachabilitySolver.framework.reachability_solver import ReachabilitySolver
from qsynth.ReachabilitySolver.solvers.solver_utils import add_implication_to_cnf, get_reachability_solution_from_model, \
    AuxiliaryVariable


class IncTimeStepSolver(ReachabilitySolver):
    """
    Solves a reachability problem using Incremental SAT. It iteratively tries to find a solution in k steps for
    increasing values of k. In the k'th iteration it adds the constraints for time k to the SAT solver, and using
    assumption variables it enforces the goal state only at time k+1.
    """
    def solve(self, reachability_encoding: ReachabilityEncoding) -> Optional[ReachabilitySolution]:
        id_pool = reachability_encoding.id_pool
        v_id = id_pool.id
        k = 0
        upper_bound = reachability_encoding.upper_bound
        action_var_bound = reachability_encoding.action_variable_bound
        satisfied = False
        solution = None
        with Solver(name="cd19") as solver:
            if action_var_bound is not None:
                totalizer = initialize_totalizer_for_action_var_bound(reachability_encoding)
                solver.append_formula(totalizer.cnf)
            while not satisfied:
                if upper_bound is not None and k > upper_bound:
                    break
                cnf = make_inc_cnf_for_step(k, reachability_encoding)
                solver.append_formula(cnf)
                # Assume goal state to be reached at time k
                assumptions = [ v_id(f(k)) ]
                # If there are fewer action variables than the bound, don't enforce it
                if action_var_bound is not None and action_var_bound < len(totalizer.rhs):
                    # Else enforce action variable bound as an assumption
                    assumptions.append(-totalizer.rhs[action_var_bound])
                if solver.solve(assumptions=assumptions):
                    satisfied = True
                    model = solver.get_model()
                    solution = get_reachability_solution_from_model(k, reachability_encoding, model)
                else:
                    k += 1
                    if action_var_bound is not None:
                        new_clauses = extend_action_var_bound_for_time_k(k, reachability_encoding, totalizer)
                        solver.append_formula(new_clauses)
        return solution


def make_inc_cnf_for_step(k: int, reachability_encoding: ReachabilityEncoding) -> CNFPlus:
    cnf = CNFPlus()
    id_pool = reachability_encoding.id_pool
    v_id = id_pool.id
    if k == 0:
        cnf.extend(reachability_encoding.get_initial_state_for_time(0))
        goal_cnf = reachability_encoding.get_goal_state_for_time(0)
        add_implication_to_cnf(v_id(f(0)), goal_cnf)
        cnf.extend(goal_cnf)
    else:
        transition_cnf = reachability_encoding.get_transition_predicate_for_time(k - 1)
        cnf.extend(transition_cnf)

        # Disable assumption variable from previous time step with unit clause so solver can remove clauses
        cnf.append([-v_id(f(k - 1))])

        goal_cnf = reachability_encoding.get_goal_state_for_time(k)
        add_implication_to_cnf(v_id(f(k)), goal_cnf)
        # We add the following constraint: f_k => G(x)
        cnf.extend(goal_cnf)

    return cnf


def initialize_totalizer_for_action_var_bound(reachability_encoding: ReachabilityEncoding) -> ITotalizer:
    id_pool = reachability_encoding.id_pool
    v_id = id_pool.id
    action_var_bound = reachability_encoding.action_variable_bound
    action_var_ids = set(v_id(var) for var in reachability_encoding.get_action_variables_for_time(0))
    totalizer = ITotalizer(lits=action_var_ids, ubound=action_var_bound, top_id=id_pool.top)
    # Update IDPool to avoid overlapping id's
    id_pool.occupy(id_pool.top + 1, totalizer.top_id)
    return totalizer


def extend_action_var_bound_for_time_k(k: int, reachability_encoding: ReachabilityEncoding, totalizer: ITotalizer) -> CNFPlus:
    id_pool = reachability_encoding.id_pool
    v_id = id_pool.id
    action_var_ids = set(v_id(var) for var in reachability_encoding.get_action_variables_for_time(k-1))
    # Add action vars for time k under the AtMost-bound
    totalizer.extend(lits=action_var_ids, top_id=id_pool.top)
    # Update IDPool to avoid overlapping id's
    id_pool.occupy(id_pool.top + 1, totalizer.top_id)
    # Only return the new clauses to avoid duplicate clauses
    new_clauses = totalizer.cnf.clauses[-totalizer.nof_new:]
    return new_clauses


def f(t):
    return AuxiliaryVariable(f"f {t}")
