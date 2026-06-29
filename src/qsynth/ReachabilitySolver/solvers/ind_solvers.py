from abc import abstractmethod

from pysat.card import ITotalizer, CardEnc
from pysat.examples.rc2 import RC2
from pysat.formula import CNFPlus, WCNF
from pysat.solvers import Solver

from qsynth.ReachabilitySolver.framework.reachability_encoding import ReachabilityEncoding
from qsynth.ReachabilitySolver.framework.reachability_solver import ReachabilitySolver
from qsynth.ReachabilitySolver.solvers.solver_utils import add_implication_to_cnf, AuxiliaryVariable, \
    get_reachability_solution_from_model, write_intermediate_solution, get_action_var_ids_up_to_time_k, \
    bound_number_of_action_variables_to_time_t


class GoingUpTimeStepSolver(ReachabilitySolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses linear forward search for the
    minimal number of used time steps by only using the first k steps in iteration k.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps.
    """

    def solve(self, reachability_encoding):
        id_pool = reachability_encoding.id_pool
        v_id = id_pool.id
        upper_bound = reachability_encoding.upper_bound
        cnf = make_ind_cnf(reachability_encoding)
        if reachability_encoding.action_variable_bound is not None:
            cnf.extend(bound_number_of_action_variables_to_time_t(reachability_encoding, upper_bound))
        solution = None
        with Solver(name="cd19") as solver:
            solver.append_formula(cnf)
            for k in range(upper_bound + 1):
                assumptions = [v_id(i(t)) if t < k else -v_id(i(t)) for t in range(upper_bound)]
                if solver.solve(assumptions=assumptions):
                    model = solver.get_model()
                    solution = get_reachability_solution_from_model(
                        k,
                        reachability_encoding,
                        model,
                        disabled_time_steps=get_disabled_time_steps(model, id_pool)
                    )
                    break
        return solution


class SatToUnsatSolver(ReachabilitySolver):
    """
    Abstract class for sat-to-unsat solvers minimizing the number of time steps.
    Implements the main solver loop and lets subclasses decide assumption strategies.
    """

    def __init__(self, intermediate_solution_path=None):
        self.upper_bound = None
        self.intermediate_solution_path = intermediate_solution_path

    def solve(self, reachability_encoding: ReachabilityEncoding):
        id_pool = reachability_encoding.id_pool
        self.upper_bound = reachability_encoding.upper_bound
        upper_bound = reachability_encoding.upper_bound
        cnf = make_ind_cnf(reachability_encoding)
        # We bound the number of action variables if a bound is specified
        if reachability_encoding.action_variable_bound is not None:
            cnf.extend(bound_number_of_action_variables_to_time_t(reachability_encoding, upper_bound))
        best_so_far = upper_bound + 1
        model = None
        satisfiable = True
        solution = None
        with Solver(name="cd19") as solver:
            solver.append_formula(cnf)

            while satisfiable and best_so_far > 0:
                assumption_formula = self.get_assumption_formula(model, id_pool, best_so_far)
                solver.append_formula(assumption_formula)

                assumptions = self.get_assumptions(model, id_pool, best_so_far)
                if solver.solve(assumptions=assumptions):
                    model = solver.get_model()
                    best_so_far = count_true_indicator_variables(model, id_pool)
                    solution = get_reachability_solution_from_model(
                        upper_bound,
                        reachability_encoding, model,
                        disabled_time_steps=get_disabled_time_steps(model, id_pool)
                    )
                    if self.intermediate_solution_path is not None:
                        write_intermediate_solution(reachability_encoding, solution, self.intermediate_solution_path)
                else:
                    satisfiable = False
        return solution

    def get_assumption_formula(self, model, id_pool, best_so_far):
        """
        Gets called in each iteration of the solver loop for adding extra formulas to the solver before calling solve().
        Args:
            model: List containing last satisfying assignment to CNF formula.
            id_pool: IDPool to use for constructing CNF formula.
            best_so_far: The lowest number of time steps in a satisfiable solution so far.

        Returns:
            A CNF formula to add to the SAT problem before solving.
        """
        raise NotImplementedError()

    def get_assumptions(self, model, id_pool, best_so_far):
        """

        Args:
            model: List containing last satisfying assignment to CNF formula.
            id_pool: IDPool to use for constructing CNF formula.
            best_so_far: The lowest number of time steps in a satisfiable solution so far.

        Returns:
            A list of assumptions (literals as integers) to use in the next solver call.
        """
        raise NotImplementedError()


class GoingDownTimeStepSolver(SatToUnsatSolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses linear reverse search for the
    minimal number of used time steps. It always requires the first k steps to be used for a solution using k steps.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps.
    """

    def __init__(self, intermediate_solution_path):
        super().__init__(intermediate_solution_path)

    def get_assumption_formula(self, model, id_pool, best_so_far):
        return []

    def get_assumptions(self, model, id_pool, best_so_far):
        v_id = id_pool.id
        return [-v_id(i(t)) for t in range(best_so_far - 1, self.upper_bound)]


class FromMiddleTimeStepSolver(SatToUnsatSolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses linear reverse search for the
    minimal number of used time steps. It always requires the middle k steps to be used for a solution using k steps.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps.
    """

    def __init__(self, intermediate_solution_path):
        super().__init__(intermediate_solution_path)

    def get_assumption_formula(self, model, id_pool, best_so_far):
        return []

    def get_assumptions(self, model, id_pool, best_so_far):
        v_id = id_pool.id
        b = self.upper_bound
        first_false_ind_var = (best_so_far - 1) // 2
        last_false_ind_var = b - 1 - (best_so_far // 2)
        return [-v_id(i(t)) for t in range(first_false_ind_var, last_false_ind_var + 1) if t < b]


class AtMostTimeStepSolver(SatToUnsatSolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses ATLEAST-clauses to enforce
    that at least one more indicator variable must be false in the next iteration. It assumes indicator variables that
    were true in the last solution to also be true in the next iteration.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps.
    """

    def __init__(self, intermediate_solution_path):
        super().__init__(intermediate_solution_path)

    def get_assumption_formula(self, model, id_pool, best_so_far):
        if model is None:
            return []
        else:
            true_indicator_vars = get_true_indicator_variables(model, id_pool)
            return CardEnc.atleast(lits=[-var for var in true_indicator_vars], bound=1)

    def get_assumptions(self, model, id_pool, best_so_far):
        if model is None:
            return []
        else:
            return [-var for var in get_false_indicator_variables(model, id_pool)]


class BinaryTimeStepSolver(ReachabilitySolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses binary search to find the
    minimal number of time steps. It always requires the first k steps to be used for a solution using k steps.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps.
    """

    def __init__(self, intermediate_solution_path):
        super().__init__()
        self.intermediate_solution_path = intermediate_solution_path

    def solve(self, reachability_encoding):
        id_pool = reachability_encoding.id_pool
        v_id = id_pool.id
        upper_bound = reachability_encoding.upper_bound
        cnf = make_ind_cnf(reachability_encoding)
        if reachability_encoding.action_variable_bound is not None:
            cnf.extend(bound_number_of_action_variables_to_time_t(reachability_encoding, upper_bound))
        # add clauses specifying that only consecutive time steps may be used
        for t in range(upper_bound - 1):
            # ¬i^t => ¬i^t+1
            cnf.append([--v_id(i(t)), -v_id(i(t + 1))])
        solution = None
        with Solver(name="cd19") as solver:
            solver.append_formula(cnf)
            last_unsat = -1
            best_so_far = upper_bound
            mid = best_so_far
            # The complex boolean condition is to handle the edge case of the upper bound being 0
            while last_unsat < best_so_far - 1 or (solution is None and upper_bound == 0):
                # Make first 'last_unsat' time steps true (we know these steps must be used in any solution)
                assumptions = [v_id(i(t)) for t in range(last_unsat + 1) ]
                # Only allow using the first 'mid' time steps; the rest should be false
                assumptions += [-v_id(i(t)) for t in range(upper_bound) if t >= mid]
                if solver.solve(assumptions=assumptions):
                    best_so_far = mid
                    model = solver.get_model()
                    solution = get_reachability_solution_from_model(
                        upper_bound,
                        reachability_encoding,
                        model,
                        disabled_time_steps=get_disabled_time_steps(model, id_pool)
                    )
                    if self.intermediate_solution_path is not None:
                        write_intermediate_solution(reachability_encoding, solution, self.intermediate_solution_path)
                else:
                    last_unsat = mid
                mid = (last_unsat + best_so_far + 1) // 2

        return solution


class MaxSatSolver(ReachabilitySolver):
    @abstractmethod
    def make_soft_clauses(self, reachability_encoding):
        pass

    def solve(self, reachability_encoding):
        id_pool = reachability_encoding.id_pool
        v_id = id_pool.id
        upper_bound = reachability_encoding.upper_bound
        cnf = make_ind_cnf(reachability_encoding)
        if reachability_encoding.action_variable_bound is not None:
            cnf.extend(bound_number_of_action_variables_to_time_t(reachability_encoding, upper_bound))
        # add clauses specifying that only consecutive time steps may be used
        for t in range(upper_bound - 1):
            # ¬i^t => ¬i^t+1
            cnf.append([--v_id(i(t)), -v_id(i(t + 1))])

        weighted_cnf = self.make_soft_clauses(reachability_encoding)
        weighted_cnf.extend(cnf)

        rc2 = RC2(weighted_cnf, incr=True)
        model = rc2.compute()

        if model is None:
            # No solution was found
            return None

        solution = get_reachability_solution_from_model(
            upper_bound,
            reachability_encoding,
            model,
            disabled_time_steps=get_disabled_time_steps(model, id_pool)
        )
        return solution


class MaxSatTimeStepSolver(MaxSatSolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses MaxSAT to find the minimal
    number of time steps. It adds each indicator variable negated as a soft clause. The MaxSAT solver will maximize
    the number of satisfied soft clauses <=> minimize the number of used time steps.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps.
    """
    def make_soft_clauses(self, reachability_encoding):
        weighted_cnf = WCNF()
        v_id = reachability_encoding.id_pool.id
        # Add soft clauses with false indicator variables
        for t in range(reachability_encoding.upper_bound):
            weighted_cnf.append([-v_id(i(t))], weight=1)
        return weighted_cnf


class MaxSatActionVarSolver(MaxSatSolver):
    """
    Solves a reachability problem using the IND encoding (see below). This strategy uses MaxSAT to find the minimal
    number of action variables. It adds each action variable negated as a soft clause. The MaxSAT solver will maximize
    the number of satisfied soft clauses <=> minimize the number of true action variables.

    The IND encoding solves a reachability problem by defining it for every time step up to a given upper bound. Each
    time step gets an assumption variable ('indicator variable', i^t) indicating whether the time step is used or not.
    Different strategies can then be employed to find the minimal number of time steps.
    """
    def make_soft_clauses(self, reachability_encoding):
        weighted_cnf = WCNF()
        # Add soft clauses with false action variables
        for action_var in get_action_var_ids_up_to_time_k(reachability_encoding, reachability_encoding.upper_bound):
            weighted_cnf.append([-action_var], weight=1)
        return weighted_cnf



def make_ind_cnf(reachability_encoding):
    id_pool = reachability_encoding.id_pool
    upper_bound = reachability_encoding.upper_bound
    cnf = CNFPlus()
    # Add basic reachability constraints: I(x) ∧ G(x)
    cnf.extend(reachability_encoding.get_initial_state_for_time(0))
    cnf.extend(reachability_encoding.get_goal_state_for_time(upper_bound))
    v_id = id_pool.id

    for t in range(upper_bound):
        # If the indicator variable is true, the transition predicate is enforced
        # i^t => T(x,x',a)
        transition_cnf = reachability_encoding.get_transition_predicate_for_time(t)
        add_implication_to_cnf(v_id(i(t)), transition_cnf)
        cnf.extend(transition_cnf)
        # If the indicator variable is false, the state is propagated to the next time step
        # ¬i^t => x^t = x^{t+1}
        state_variables = reachability_encoding.get_state_variables_for_time(t)
        state_variables_next = reachability_encoding.get_state_variables_for_time(t + 1)
        for (x, x_next) in zip(state_variables, state_variables_next):
            # x = x_next <=> (x or not x_next) and (not x or x_next)
            cnf.append([--v_id(i(t)), v_id(x), -v_id(x_next)])
            cnf.append([--v_id(i(t)), -v_id(x), v_id(x_next)])

    return cnf


def count_true_indicator_variables(model, id_pool):
    return len(get_true_indicator_variables(model, id_pool))


def get_true_indicator_variables(model, id_pool):
    result = []
    for var in model:
        if var < 0:
            continue
        var_object = id_pool.obj(abs(var))
        if isinstance(var_object, AuxiliaryVariable):
            result.append(var)
    return result


def get_false_indicator_variables(model, id_pool):
    result = []
    for var in model:
        if var > 0:
            continue
        var_object = id_pool.obj(abs(var))
        if isinstance(var_object, AuxiliaryVariable):
            result.append(abs(var))
    return result


def get_disabled_time_steps(model, id_pool):
    disabled_time_steps = []
    for var in get_false_indicator_variables(model, id_pool):
        aux_var = id_pool.obj(abs(var))
        t = int(aux_var.string.split()[1])
        disabled_time_steps.append(t)

    return disabled_time_steps


def print_best_so_far(best_so_far, time):
    print(f"Best so far (value, time): {best_so_far} {time:.2f}")


def i(t):
    return AuxiliaryVariable(f"i {t}")
