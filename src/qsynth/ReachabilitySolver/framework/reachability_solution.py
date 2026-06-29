from qsynth.ReachabilitySolver.framework.variable import Variable


class ReachabilitySolution:
    """
    Container class to hold the solution to a reachability problem.
    """
    def __init__(self,
                 initial_state: list[Variable],
                 action_sequence: list[list[Variable]],
                 goal_state: list[Variable]
                 ):
        self.initial_state = initial_state
        self.action_sequence = action_sequence
        self.goal_state = goal_state
