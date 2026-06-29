from typing import Optional

from qiskit import QuantumCircuit

from qsynth.PeepholeSlicing.circuit_utils import project_circuit, project_coupling_graph
from qsynth.Synthesizers.synthesizer import Synthesizer
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import get_used_qubits
from qsynth.Utilities.coupling_graph import CouplingGraph
from qsynth.Utilities.result import MappingResult


class UnusedQubitsDisabled(Synthesizer):
    def __init__(self, synthesizer: Synthesizer):
        self.synthesizer = synthesizer

    def run(self, circuit: QuantumCircuit, coupling_graph: Optional[CouplingGraph],
            timeout: int | float) -> MappingResult:
        projection_map = {old_index: new_index
                          for new_index, old_index
                          in enumerate(sorted(get_used_qubits(circuit)))}
        projected_circuit = project_circuit(circuit, projection_map, len(projection_map))
        projected_coupling_graph = project_coupling_graph(coupling_graph, projection_map) if coupling_graph is not None else None

        result = self.synthesizer.run(projected_circuit, projected_coupling_graph, timeout)

        reverse_projection_map = {new_index: old_index for old_index, new_index in projection_map.items()}
        result.circuit = project_circuit(result.circuit, reverse_projection_map, circuit.num_qubits)
        result.initial_mapping = {reverse_projection_map.get(k, k): reverse_projection_map.get(v, v)
                                  for k, v in result.initial_mapping.items()}
        result.final_mapping = {reverse_projection_map.get(k, k): reverse_projection_map.get(v, v)
                                for k, v in result.final_mapping.items()}
        for i in range(circuit.num_qubits):
            result.initial_mapping.setdefault(i, i)
            result.final_mapping.setdefault(i, i)
        return result
