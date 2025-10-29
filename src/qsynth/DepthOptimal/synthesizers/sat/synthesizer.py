from abc import ABC, abstractmethod
from qiskit import QuantumCircuit

from typing import Optional, Union

from qsynth.DepthOptimal.platform import Platform

from qsynth.DepthOptimal.util.logger import Logger
from qsynth.DepthOptimal.util.circuits import (
    LogicalQubit,
    PhysicalQubit,
    SynthesizerOutput,
)

import pysat.solvers

Solver = (
    pysat.solvers.Glucose42
    | pysat.solvers.MapleCM
    | pysat.solvers.Cadical153
    | pysat.solvers.MapleChrono
    | pysat.solvers.Minisat22
    | pysat.solvers.Cadical195
)


class SATSynthesizer(ABC):
    description: str = "No description."

    @abstractmethod
    def parse_solution(
        self,
        original_circuit: QuantumCircuit,
        platform: Platform,
        solver_solution: list[str],
    ) -> tuple[QuantumCircuit, dict[LogicalQubit, PhysicalQubit]]:
        pass

    @abstractmethod
    def synthesize(
        self,
        logical_circuit: QuantumCircuit,
        platform: Platform,
        solver: Solver,
        time_limit_s: int,
        logger: Logger,
        cx_optimal: bool = False,
        swap_optimal: bool = False,
        ancillaries: bool = False,
        swap_bound: Optional[int] = None,
    ) -> SynthesizerOutput:
        """
        Layout synthesis.

        Args
        ----
        - logical_circuit (`QuantumCircuit`): Logical circuit.
        - platform (`Platform`): The target platform.
        - solver (`Solver`): The underlying solver.

        Returns
        --------
        - `QuantumCircuit`: Physical circuit.
        - `dict[LogicalQubit, PhysicalQubit]`: Initial mapping of logical qubits to physical qubits.
        - `float`: Time taken to synthesize the physical circuit.
        """
        pass
