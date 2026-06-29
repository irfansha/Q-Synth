
from abc import ABC, abstractmethod
from typing import Optional

from qiskit import QuantumCircuit

from qsynth.Utilities.coupling_graph import CouplingGraph
from qsynth.Utilities.result import MappingResult


class Synthesizer(ABC):
    @abstractmethod
    def run(self, circuit: QuantumCircuit, coupling_graph: Optional[CouplingGraph], timeout: int | float) -> MappingResult:
        pass
