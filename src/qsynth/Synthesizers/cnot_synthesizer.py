from dataclasses import dataclass
from typing import Optional

from qiskit import QuantumCircuit

from qsynth.CnotSynthesis.cnot_synthesis import cnot_optimization as cnot_optimization_planning
from qsynth.CnotSynthesis.cnot_synthesis_sat_qbf import cnot_optimization as cnot_optimization_sat_qbf
from qsynth.Synthesizers.synthesizer import Synthesizer
from qsynth.Synthesizers.configs import CnotSynthesisConfig
from qsynth.Utilities.coupling_graph import CouplingGraph
from qsynth.Utilities.result import MappingResult


@dataclass
class CnotSynthesizer(Synthesizer):
    config: CnotSynthesisConfig

    def run(self, circuit: QuantumCircuit, coupling_graph: Optional[CouplingGraph], timeout: int | float) -> MappingResult:
        metric = get_metric_from_optimization_and_bound_metric(self.config.metric, self.config.bound_metric)

        if self.config.model == "planning":
            result = cnot_optimization_planning(
                circuit=circuit,
                planner=self.config.solver,
                time=timeout,
                minimization=metric,
                verbose=self.config.verbose,
                coupling_graph=coupling_graph,
            )
        else:
            result = cnot_optimization_sat_qbf(
                circuit=circuit,
                minimization=metric,
                qubit_permute=self.config.output_qubit_permute,
                search_strategy=self.config.search_strategy,
                solver=self.config.solver,
                time=timeout,
                coupling_graph=coupling_graph,
                intermediate_files_path=self.config.intermediate_files_path,
                verbose=self.config.verbose,
            )
        return result


def get_metric_from_optimization_and_bound_metric(optimization_metric, bound_metric):
    if bound_metric is None:
        return optimization_metric
    elif bound_metric == "cx-depth":
        return "bounded_cx-depth_local_cx-count"
    else:
        return "bounded_cx-count_local_cx-depth"