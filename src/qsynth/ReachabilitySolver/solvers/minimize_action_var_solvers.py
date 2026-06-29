from typing import Optional

from pysat.card import ITotalizer, CardEnc
from pysat.formula import CNFPlus
from pysat.solvers import Solver

from qsynth.ReachabilitySolver.framework.reachability_encoding import ReachabilityEncoding
from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution
from qsynth.ReachabilitySolver.framework.reachability_solver import ReachabilitySolver
from qsynth.ReachabilitySolver.solvers.ind_solvers import make_ind_cnf, get_disabled_time_steps, \
    count_true_indicator_variables, i, get_false_indicator_variables, get_true_indicator_variables
from qsynth.ReachabilitySolver.solvers.solver_utils import get_reachability_solution_from_model, add_implication_to_cnf, \
    AuxiliaryVariable, get_action_var_ids_up_to_time_k, write_intermediate_solution


class ForwardActionVarSolver(ReachabilitySolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses linear forward search for the
    minimal number of true action variables by enforcing an AtMost(k) constraint in iteration k on the action variables.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps or action variables.
    """
    def solve(self, reachability_encoding: ReachabilityEncoding) -> Optional[ReachabilitySolution]:
        id_pool = reachability_encoding.id_pool
        v_id = id_pool.id
        upper_bound = reachability_encoding.upper_bound
        action_var_ids = get_action_var_ids_up_to_time_k(reachability_encoding, upper_bound)
        model = None
        satisfiable = False
        k = 0
        while (not satisfiable) and k <= len(action_var_ids):
            cnf = make_cnf_with_bound_k(reachability_encoding, k)
            with Solver(name="cd19") as solver:
                solver.append_formula(cnf)
                satisfiable = solver.solve()
                if satisfiable:
                    model = solver.get_model()
                else:
                    k += 1

        solution = get_reachability_solution_from_model(
            upper_bound,
            reachability_encoding,
            model
        )
        return solution


class BackwardActionVarSolver(ReachabilitySolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses linear reverse search for the
    minimal number of true action variables by iteratively lowering the bound, k, of an AtMost(k) constraint on the
    action variables. This strategy shrinks the make-span if it finds a solution using fewer time steps than the upper
    bound. Note that this improves solving time but can result in suboptimal results (if a solution exists that uses
    fewer action variables but requires more time steps).

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps or action variables.
    """

    def __init__(self, intermediate_solution_path=None):
        self.intermediate_solution_path = intermediate_solution_path


    def solve(self, reachability_encoding: ReachabilityEncoding) -> Optional[ReachabilitySolution]:
        id_pool = reachability_encoding.id_pool
        v_id = id_pool.id
        upper_bound = reachability_encoding.upper_bound
        cnf = make_ind_cnf(reachability_encoding)
        # Make action variables false for unused time steps
        cnf.extend(false_action_vars_in_unused_time_steps(reachability_encoding))
        action_var_ids = get_action_var_ids_up_to_time_k(reachability_encoding, upper_bound)
        model = None
        satisfiable = True
        with Solver(name="cd19") as solver:
            solver.append_formula(cnf)
            #print(f"{solver.nof_vars()} variables and {solver.nof_clauses()} clauses")
            # Get initial satisfiable solution
            solver.solve()
            model = solver.get_model()
            best_so_far = reachability_encoding.action_variable_bound
            with ITotalizer(lits=action_var_ids, ubound=best_so_far, top_id=id_pool.top) as totalizer:
                solver.append_formula(totalizer.cnf)
                while satisfiable and best_so_far > 0:
                    # AtMost(best_so_far - 1)
                    #print(f"AtMost({best_so_far-1}) on {len(action_var_ids)} CNOT variables")
                    #print(f"{solver.nof_vars()} variables and {solver.nof_clauses()} clauses")
                    if solver.solve(assumptions=[-totalizer.rhs[best_so_far - 1]]):
                        model = solver.get_model()
                        best_so_far = count_action_variables(model, action_var_ids)
                        # Remove unused time steps
                        used_time_steps = count_true_indicator_variables(model, id_pool)
                        solver.append_formula([[ -v_id(i(t)) ] for t in range(used_time_steps, upper_bound)])
                        solution = get_reachability_solution_from_model(
                            upper_bound,
                            reachability_encoding, model,
                            disabled_time_steps=get_disabled_time_steps(model, id_pool)
                        )
                        if self.intermediate_solution_path is not None:
                            write_intermediate_solution(reachability_encoding, solution, self.intermediate_solution_path)

                    else:
                        satisfiable = False

        solution = get_reachability_solution_from_model(
            upper_bound,
            reachability_encoding,
            model,
            disabled_time_steps=get_disabled_time_steps(model, id_pool)
        )
        return solution


def make_cnf_with_bound_k(reachability_encoding, k) -> CNFPlus:
    reachability_encoding.id_pool.restart()
    cnf = CNFPlus()
    # We make a CNF like K-STEP but the number of time steps is min{action_var_bound, time_step_bound}.
    number_of_time_steps = min(k, reachability_encoding.upper_bound)
    cnf.extend(reachability_encoding.get_initial_state_for_time(0))
    cnf.extend(reachability_encoding.get_goal_state_for_time(number_of_time_steps))
    for t in range(number_of_time_steps):
        cnf.extend(reachability_encoding.get_transition_predicate_for_time(t))

    action_var_ids = get_action_var_ids_up_to_time_k(reachability_encoding, number_of_time_steps)
    atmost = CardEnc.atmost(lits=action_var_ids, bound=k, vpool=reachability_encoding.id_pool)
    cnf.extend(atmost)

    return cnf


def count_action_variables(model, action_var_ids):
    return len([var for var in model if var > 0 and var in action_var_ids])


def false_action_vars_in_unused_time_steps(reachability_encoding):
    cnf = CNFPlus()
    v_id = reachability_encoding.id_pool.id
    for t in range(reachability_encoding.upper_bound):
        action_variables = reachability_encoding.get_action_variables_for_time(t)
        for a in action_variables:
            # ¬i_t => ¬a  ∀a ∈ action_variables
            cnf.append([--v_id(i(t)), -v_id(a)])
    return cnf