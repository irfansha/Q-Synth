from abc import ABC, abstractmethod

from pysat.formula import IDPool, CNFPlus

from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution
from qsynth.ReachabilitySolver.framework.variable import Variable


class ReachabilityEncoding(ABC):
    """
    Interface for reachability encodings. Variables must be of class Variable as the name and time step of variables
    are used to construct the ReachabilitySolution returned from a ReachabilitySolver. Variables should be translated
    into ID's using the encoding's IDPool, as a ReachabilitySolver may add additional variables.
    """

    def __init__(self, upper_bound, action_variable_bound=None):
        self.id_pool = IDPool(start_from=1)
        self.upper_bound = upper_bound
        self.action_variable_bound = action_variable_bound

    @abstractmethod
    def get_initial_state_for_time(self, t) -> CNFPlus:
        """
        Returns a CNF formula specifying the initial state for time t.
        """
        pass

    @abstractmethod
    def get_goal_state_for_time(self, t) -> CNFPlus:
        """
        Returns a CNF formula specifying the goal state for time t.
        """
        pass

    @abstractmethod
    def get_transition_predicate_for_time(self, t) -> CNFPlus:
        """
        Returns a CNF formula specifying the allowed state transitions from time t to t+1.
        """
        pass

    @abstractmethod
    def get_state_variables_for_time(self, t) -> list[Variable]:
        """
        Returns a list of all state variables for time t.
        """
        pass

    @abstractmethod
    def get_action_variables_for_time(self, t) -> list[Variable]:
        """
        Returns a list of all action variables for time t.
        """
        pass

    @abstractmethod
    def get_variable_names_for_solution_view(self) -> list[str]:
        """
        Returns the names of variables to include in the ReachabilitySolution's action_sequence. Not all variables
        are necessary to decode a solution, so this method acts as a filter for simplifying the ReachabilitySolution.
        """
        pass

    @abstractmethod
    def decode_reachability_solution(self, reachability_solution: ReachabilitySolution):
        """
        Takes a solution to the reachability problem encoded in this class and decodes it.
        Args:
            reachability_solution: A ReachabilitySolution instance containing a satisfying assignment.
        """
        pass
