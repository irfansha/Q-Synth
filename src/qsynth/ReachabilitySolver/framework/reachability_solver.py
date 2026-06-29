from abc import abstractmethod, ABC
from typing import Optional

from qsynth.ReachabilitySolver.framework.reachability_encoding import ReachabilityEncoding
from qsynth.ReachabilitySolver.framework.reachability_solution import ReachabilitySolution


class ReachabilitySolver(ABC):
    """
    Interface for reachability solvers.
    """

    @abstractmethod
    def solve(self, reachability_encoding: ReachabilityEncoding) -> Optional[ReachabilitySolution]:
        """
        Solves a specified reachability problem by encoding it to SAT using the class' solving strategy.
        Args:
            reachability_encoding: A ReachabilityEncoding instance specifying the problem to be solved. The encoding
            contains predicates in CNF for the initial state, state transitions, and for the goal state.

        Returns:
            None if no solution is found else a ReachabilitySolution containing the solution.
        """
        pass