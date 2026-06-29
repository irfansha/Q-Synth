from dataclasses import dataclass
from typing import Optional

from qiskit import QuantumCircuit

from qsynth.Synthesizers.cnot_synthesizer import get_metric_from_optimization_and_bound_metric
from qsynth.Synthesizers.synthesizer import Synthesizer
from qsynth.ReachabilitySolver.encodings.cnot_rz_synthesis.cnot_rz_synthesis_reachability import \
    optimize_cnot_rz_circuit_with_reachability_encoding
from qsynth.Synthesizers.configs import CnotRzSynthesisConfig
from qsynth.Utilities.coupling_graph import CouplingGraph
from qsynth.Utilities.result import MappingResult


@dataclass
class CnotRzSynthesizer(Synthesizer):
    config: CnotRzSynthesisConfig

    def run(self, circuit: QuantumCircuit, coupling_graph: Optional[CouplingGraph], timeout: int | float) -> MappingResult:
        metric = get_metric_from_optimization_and_bound_metric(self.config.metric, self.config.bound_metric)

        result =  optimize_cnot_rz_circuit_with_reachability_encoding(
            circuit=circuit,
            coupling_graph=coupling_graph,
            qubit_permutation=self.config.output_qubit_permute,
            metric=metric,
            strategy=self.config.search_strategy,
            timeout=timeout,
            check=True
        )
        return result
