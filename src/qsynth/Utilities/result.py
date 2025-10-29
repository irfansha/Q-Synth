# result class for quantum circuit initial mapping final mapping
from dataclasses import dataclass
from qiskit import QuantumCircuit


@dataclass
class MappingResult:
    """
    Class to hold the results of a mapping operation.

    Attributes:
        circuit (QuantumCircuit): quantum circuit after mapping.
        final_mapping (dict): final mapping of qubits to physical qubits.
        optimal_result (bool): The optimal value achieved by the mapping.
        swap_count (int): The number of swaps performed during the mapping.
        opt_val (int): The optimal value of the metric used for mapping, mainly for tests.
        timed_out (bool): Indicates if the mapping operation timed out.
    """

    circuit: QuantumCircuit
    initial_mapping: dict[int, int]
    final_mapping: dict[int, int]
    optimal_result: bool
    swap_count: int
    opt_val: int
    timed_out: bool

    def __str__(self):
        return f"MappingResult(circuit={self.circuit}, initial_mapping={self.initial_mapping}, final_mapping={self.final_mapping}, opt_val={self.opt_val}, swap_count={self.swap_count})"

    def __repr__(self):
        return self.__str__()

    def __init__(
        self,
        circuit,
        initial_mapping=None,
        final_mapping=None,
        optimal_result=None,
        swap_count=None,
        opt_val=None,
        timed_out=False,
    ):
        self.circuit = circuit
        self.initial_mapping = initial_mapping
        self.final_mapping = final_mapping
        self.optimal_result = optimal_result
        self.swap_count = swap_count
        self.opt_val = opt_val
        self.timed_out = timed_out
