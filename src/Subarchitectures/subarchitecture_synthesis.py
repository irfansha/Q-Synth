from src.Subarchitectures.subarchitecture_utils import (
    connected_subarchitectures,
    eliminate_isomorphism_hybrid,
    maximal_subarchitectures,
)

from qiskit import QuantumCircuit
import rustworkx as rx

from dataclasses import dataclass


@dataclass
class MappingSolution:
    circuit: QuantumCircuit
    architecture: rx.PyGraph


@dataclass
class MappingState:
    solutions: list[MappingSolution]
    opt_val: int


def convert_circuit_to_full_architecture(
    circuit: QuantumCircuit, subarchitecture: rx.PyGraph, full_size: int
):
    """
    Converts input circuit into a new quantum circuit which has the desired number of qubits
    while preserving correspondence between qubits in sub-architecture and qubits in full architecture.
    """
    qubit_list = list(subarchitecture.nodes())
    qubit_list.sort()
    out = QuantumCircuit(full_size)
    out.compose(circuit, inplace=True, qubits=qubit_list)
    return out


class SubarchitectureSynthesis:

    def compute_subarchitectures(self):
        self.subarchitecture_size = self.req_qubits + self.fixed_ancillaries
        self.all_subarchitectures = connected_subarchitectures(
            self.platform, self.subarchitecture_size
        )
        self.non_isomorphic_subarchitectures = eliminate_isomorphism_hybrid(
            self.all_subarchitectures
        )
        self.maximal_subarchitectures = maximal_subarchitectures(
            self.non_isomorphic_subarchitectures
        )

    def order_subarchitectures(self):

        # Use edge-count as base measure for quality
        def edge_count(subarch: rx.PyGraph) -> int:
            return len(subarch.edge_list())

        self.maximal_subarchitectures = sorted(
            self.maximal_subarchitectures, key=edge_count, reverse=True
        )

    def __init__(
        self,
        required_qubits: int,
        coupling_graph: list[list[int]],
        fixed_ancillaries: int = 0,
    ):

        self.req_qubits = required_qubits
        self.coupling_map = coupling_graph
        self.fixed_ancillaries = fixed_ancillaries

        # Built internal platform representation
        self.platform = rx.PyGraph()
        self.platform.add_nodes_from(range(max(map(max, coupling_graph)) + 1))
        self.platform.add_edges_from_no_data(list(map(tuple, coupling_graph)))

        self.full_architecture_size = len(self.platform.nodes())
        print(f"Full arch size: {self.full_architecture_size}")

        # Compute sub-architectures
        self.compute_subarchitectures()
