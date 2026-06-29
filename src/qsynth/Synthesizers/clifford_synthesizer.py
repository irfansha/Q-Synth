from dataclasses import dataclass
from typing import Optional
import time as clock

from qiskit import QuantumCircuit

from qsynth.PeepholeSlicing.circuit_utils import remove_zero_cost_swaps
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import add_trailing_swaps
from qsynth.Synthesizers.synthesizer import Synthesizer
from qsynth.Synthesizers.configs import CliffordSynthesisConfig
from qsynth.Utilities.coupling_graph import CouplingGraph
from qsynth.Utilities.result import MappingResult

from qsynth.CliffordSynthesis.clifford_synthesis_planning import clifford_optimization as clifford_optimization_planning
from qsynth.CliffordSynthesis.clifford_synthesis_sat import clifford_optimization as clifford_optimization_sat
from qsynth.CliffordSynthesis.clifford_1q_resynthesis import clifford_1q_optimization_greedy

@dataclass
class CliffordSynthesizer(Synthesizer):
    config: CliffordSynthesisConfig

    def run(self, circuit: QuantumCircuit, coupling_graph: Optional[CouplingGraph], timeout: int | float) -> MappingResult:

        start_time = clock.perf_counter()
        if self.config.model == "planning":
            result = clifford_optimization_planning(
                circuit=circuit,
                encoding=self.config.encoding,
                planner=self.config.solver,
                metric=self.config.metric,
                time=timeout,
                verbose=self.config.verbose,
                coupling_graph=coupling_graph,
            )
        else:
            if self.config.bound_metric is None:
                metric = self.config.metric
            elif self.config.bound_metric == "cx-count":
                metric = "bounded_cx-count_local_cx-depth"
            else: #self.config.bound_metric is "cx-depth"
                metric = "bounded_cx-depth_local_cx-count"

            result = clifford_optimization_sat(
                circuit=circuit,
                solver=self.config.solver,
                minimization=metric,
                time=timeout,
                coupling_graph=coupling_graph,
                verbose=self.config.verbose,
                search_strategy=self.config.search_strategy,
                gate_ordering=self.config.gate_ordering,
                simple_path_restrictions=self.config.simple_path_restrictions,
                cycle_bound=self.config.cycle_bound,
                qubit_permute=self.config.output_qubit_permute,
                intermediate_files_path=self.config.intermediate_files_path,
                check=0,
            )

        # Remove swaps for post processing
        swap_free_circuit, final_mapping = remove_zero_cost_swaps(result.circuit, result.circuit.num_qubits)

        # Post-process 1q gates
        if self.config.postprocess_1q_gates == "greedy":
            swap_free_circuit = clifford_1q_optimization_greedy(swap_free_circuit)
        elif self.config.postprocess_1q_gates == "rigid":
            remaining_time = timeout - (clock.perf_counter() - start_time)
            if remaining_time > 0:
                rigid_result = clifford_optimization_planning(
                    circuit=swap_free_circuit, encoding="rigidcnot", planner="fd-ms",
                    metric="cx-count", time=remaining_time, verbose=self.config.verbose, coupling_graph=None,
                )
                if not rigid_result.no_plan_found:
                    swap_free_circuit = rigid_result.circuit

        add_trailing_swaps(swap_free_circuit, final_mapping)
        result.circuit = swap_free_circuit

        return result

