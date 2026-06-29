import os

from pysat.card import CardEnc
from pysat.formula import CNFPlus

from qsynth.ReachabilitySolver.framework.reachability_encoding import Variable
from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution


def get_reachability_solution_from_model(goal_time, reachability_encoding, model, disabled_time_steps = None):
    """
    Returns a ReachabilitySolution instance from a satisfying assignment to a SAT encoding of the reachability problem.
    Args:
        goal_time: The time step in which the goal state is reached.
        reachability_encoding: The ReachabilityEncoding of the reachability problem.
        model: The satisfying assignment.
        disabled_time_steps: A list of time steps not used in the satisfying assignment.

    Returns:
        A ReachabilitySolution instance.
    """
    action_prefixes = reachability_encoding.get_variable_names_for_solution_view()
    id_pool = reachability_encoding.id_pool
    initial_state = get_state_at_time_t_from_model(0, action_prefixes, model, id_pool)
    action_sequence = get_action_sequence_from_model(action_prefixes, model, id_pool, disabled_time_steps)
    goal_state = get_state_at_time_t_from_model(goal_time, action_prefixes, model, id_pool)
    return ReachabilitySolution(initial_state, action_sequence, goal_state)


def get_action_sequence_from_model(action_prefixes, model, id_pool, disabled_time_steps):
    """
    Returns a list of lists of the true action variables at each time step in a satisfying assignment.
    Args:
        action_prefixes: A list of prefixes that are used to determine the action variables.
        model: The satisfying assignment.
        id_pool: The IDPool used for the ReachabilityEncoding.
        disabled_time_steps: A list of time steps not used in the satisfying assignment.
    """
    action_dict = {}
    if disabled_time_steps is None:
        disabled_time_steps = []
    for var in model:
        if var < 0:
            continue
        var_object = id_pool.obj(abs(var))
        if not isinstance(var_object, Variable):
            continue
        name = var_object.name
        if name in action_prefixes:
            t = var_object.time_step
            if t in disabled_time_steps:
                continue
            if t not in action_dict:
                action_dict[t] = [var_object]
            else:
                action_dict[t].append(var_object)

    action_sequence = []
    for t in sorted(action_dict.keys()):
        action_sequence.append(action_dict[t])

    return action_sequence


def get_state_at_time_t_from_model(t, action_prefixes, model, id_pool):
    """
    Returns a list of the true state variables at time t in a satisfying assignment.
    Args:
        t: The time step from which the state variables are retrieved.
        action_prefixes: A list of prefixes of action variables that are used to determine the state variables.
        model: The satisfying assignment.
        id_pool: The IDPool used for the ReachabilityEncoding.
    """
    state_variables = []
    for var in model:
        if var < 0:
            continue
        var_object = id_pool.obj(abs(var))
        # Skip auxiliary solver variables
        if not isinstance(var_object, Variable):
            continue
        if var_object.time_step == t and var_object.name not in action_prefixes:
            state_variables.append(var_object)
    return state_variables


def get_action_var_ids_up_to_time_k(reachability_encoding, k):
    """
    Returns a set containing the id's of all action variables for all time steps from 0 (inclusive) to k (exclusive).
    """
    id_pool = reachability_encoding.id_pool
    action_vars = set()
    for t in range(k):
        action_vars = action_vars.union(set(reachability_encoding.get_action_variables_for_time(t)))
    action_var_ids = set(id_pool.id(var) for var in action_vars)
    return action_var_ids


def bound_number_of_action_variables_to_time_t(reachability_encoding, t):
    """
    Returns an AtMost(k) clause on the number of action variables across all time steps up to time t, k being the
    action variable bound specified in the reachability encoding.
    """
    bound = reachability_encoding.action_variable_bound
    id_pool = reachability_encoding.id_pool
    action_var_ids = get_action_var_ids_up_to_time_k(reachability_encoding, t)
    atmost_clause = CardEnc.atmost(lits=action_var_ids, bound=bound, vpool=id_pool)
    return atmost_clause


def add_implication_to_cnf(assumption_var_id: int, cnf: CNFPlus):
    for clause in cnf.clauses:
        clause += [-assumption_var_id]


def write_intermediate_solution(encoding, solution, intermediate_solution_path):
    mapping_result = encoding.decode_reachability_solution(solution)
    tmp_path = intermediate_solution_path + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(mapping_result.to_json())
    os.replace(tmp_path, intermediate_solution_path)




class AuxiliaryVariable:
    """
    Unique class for auxiliary variables to avoid clashing with encoding variables
    """
    def __init__(self, string):
        self.string = string

    def __eq__(self, other):
        if isinstance(other, AuxiliaryVariable):
            return self.string == other.string
        return False

    def __hash__(self):
        return hash(self.string)
