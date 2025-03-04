import os

from abc import ABC, abstractmethod
import time
from typing import Callable, Optional
from qiskit import QuantumCircuit, QuantumRegister

from src.DepthOptimal.platform import Platform

from src.DepthOptimal.synthesizers.planning.solvers import (
    Solver,
    SolverTimeout,
    SolverNoSolution,
    SolverSolution,
)
from src.DepthOptimal.util.logger import Logger
from src.DepthOptimal.util.pddl import PDDLInstance
from src.DepthOptimal.util.circuits import (
    SynthesizerOutput,
    count_swaps,
    gate_line_dependency_mapping,
    LogicalQubit,
    PhysicalQubit,
    remove_all_non_cx_gates,
    reinsert_unary_gates,
    with_swaps_as_cnots,
    SynthesizerTimeout,
    SynthesizerNoSolution,
    SynthesizerSolution,
)

JUNK_FILES = [
    "output.sas",
    "execution.details",
    "GroundedDomain.pddl",
    "GroundedProblem.pddl",
    "output.lifted",
    *[f"quantum-circuit.{i:03}.cnf" for i in range(1000)],
]


class PlanningSynthesizer(ABC):
    description: str = "No description."
    is_optimal: bool
    uses_conditional_effects: bool

    @abstractmethod
    def create_instance(
        self,
        circuit: QuantumCircuit,
        platform: Platform,
        **kwargs,
    ) -> PDDLInstance:
        pass

    @abstractmethod
    def parse_solution(
        self,
        original_circuit: QuantumCircuit,
        platform: Platform,
        solver_solution: list[str],
    ) -> tuple[QuantumCircuit, dict[LogicalQubit, PhysicalQubit]]:
        pass

    def parse_solution_grounded(
        self,
        original_circuit: QuantumCircuit,
        platform: Platform,
        solver_solution: list[str],
    ) -> tuple[QuantumCircuit, dict[LogicalQubit, PhysicalQubit]]:
        """
        Parse the solver solution of the layout synthesis problem for grounded encodings.

        This implementation requires:
        - all unary gates actions are named `apply_gate_g{id}(q{id}, ...)`
        - all CX gates actions are named `apply_cx_g{id}(q_control{id}, q_target{id}, ...)`
        - all swap actions are named `swap(?, ?, q_control{id}, q_target{id}, ...)`
        - no other actions matter in how the physical circuit is constructed

        """
        initial_mapping = {}
        physical_circuit = QuantumCircuit(QuantumRegister(platform.qubits, "p"))
        gate_logical_mapping = gate_line_dependency_mapping(original_circuit)

        def add_to_initial_mapping_if_not_present(
            logical_qubit: LogicalQubit, physical_qubit: PhysicalQubit
        ):
            initial_mapping_key_ids = [l.id for l in initial_mapping.keys()]
            if logical_qubit.id not in initial_mapping_key_ids:
                initial_mapping[logical_qubit] = physical_qubit

        def get_gate_id(action: str) -> int:
            if not action.startswith("apply_"):
                raise ValueError(f"'{action}' is not a gate action")

            gate_name_with_arguments = action.split("_")[-1]
            gate_name = gate_name_with_arguments.split("(")[0]
            return int(gate_name[1:])

        def add_single_gate_qubit(id: int, qubit: int):
            op = original_circuit.data[id].operation
            physical_circuit.append(op, [qubit])

            logical_qubit = gate_logical_mapping[id][1][0]
            add_to_initial_mapping_if_not_present(
                LogicalQubit(logical_qubit), PhysicalQubit(current_phys_map[qubit])
            )

        def add_cx_gate_qubits(id: int, control: int, target: int):
            physical_circuit.cx(control, target)

            logical_control = gate_logical_mapping[id][1][0]
            logical_target = gate_logical_mapping[id][1][1]
            add_to_initial_mapping_if_not_present(
                LogicalQubit(logical_control), PhysicalQubit(current_phys_map[control])
            )
            add_to_initial_mapping_if_not_present(
                LogicalQubit(logical_target), PhysicalQubit(current_phys_map[target])
            )

        current_phys_map = {i: i for i in range(platform.qubits)}
        for action in solver_solution:
            arguments = action.split("(")[1].split(")")[0].split(",")
            if action.startswith("apply"):
                gate_id = get_gate_id(action)
                is_cx = action.startswith("apply_cx")
                if is_cx:
                    control = int(arguments[0][1:])
                    target = int(arguments[1][1:])
                    add_cx_gate_qubits(gate_id, control, target)
                else:
                    qubit = int(arguments[0][1:])
                    add_single_gate_qubit(gate_id, qubit)

            elif action.startswith("swap") and "dummy" not in action:
                control = int(arguments[2][1:])
                target = int(arguments[3][1:])

                physical_circuit.swap(control, target)

                tmp = current_phys_map[control]
                current_phys_map[control] = current_phys_map[target]
                current_phys_map[target] = tmp

        num_lqubits = original_circuit.num_qubits
        if len(initial_mapping) != num_lqubits:
            mapping_string = ", ".join(
                f"{l} => {p}" for l, p in initial_mapping.items()
            )
            raise ValueError(
                f"Mapping '{mapping_string}' does not have the same number of qubits as the original circuit"
            )

        return physical_circuit, initial_mapping

    def parse_solution_lifted(
        self,
        original_circuit: QuantumCircuit,
        platform: Platform,
        solver_solution: list[str],
    ) -> tuple[QuantumCircuit, dict[LogicalQubit, PhysicalQubit]]:
        """
        Parse the solver solution of the layout synthesis problem for lifted encodings.

        This implementation requires:
        - all unary gates actions are named `apply_unary_[gate + input](?, q{id}, g{id}, ...)`
        - all CX gates actions are named `apply_cx_[gate + input]_[gate + input](?, ?, q_control{id}, q_target{id}, g{id}, ...)`
        - all swap actions are named `swap(?, ?, q_control{id}, q_target{id}, ...)` or `swap_input(?, l_target{id}, q_control{id}, q_target{id}, ...)`
        - no other actions matter in how the physical circuit is constructed

        """

        initial_mapping = {}
        physical_circuit = QuantumCircuit(QuantumRegister(platform.qubits, "p"))
        gate_logical_mapping = gate_line_dependency_mapping(original_circuit)

        def add_to_initial_mapping_if_not_present(
            logical_qubit: LogicalQubit, physical_qubit: PhysicalQubit
        ):
            initial_mapping_key_ids = [l.id for l in initial_mapping.keys()]
            if logical_qubit.id not in initial_mapping_key_ids:
                initial_mapping[logical_qubit] = physical_qubit

        def add_single_gate_qubit(id: int, qubit: int):
            op = original_circuit.data[id].operation
            physical_circuit.append(op, [qubit])

            logical_qubit = gate_logical_mapping[id][1][0]
            add_to_initial_mapping_if_not_present(
                LogicalQubit(logical_qubit), PhysicalQubit(current_phys_map[qubit])
            )

        def add_cx_gate_qubits(id: int, control: int, target: int):
            physical_circuit.cx(control, target)

            logical_control = gate_logical_mapping[id][1][0]
            logical_target = gate_logical_mapping[id][1][1]
            add_to_initial_mapping_if_not_present(
                LogicalQubit(logical_control), PhysicalQubit(current_phys_map[control])
            )
            add_to_initial_mapping_if_not_present(
                LogicalQubit(logical_target), PhysicalQubit(current_phys_map[target])
            )

        current_phys_map = {i: i for i in range(platform.qubits)}
        for action in solver_solution:
            arguments = action.split("(")[1].split(")")[0].split(",")
            if action.startswith("apply"):
                is_cx = action.startswith("apply_cx")
                if is_cx:
                    gate_id = int(arguments[4][1:])
                    control = int(arguments[2][1:])
                    target = int(arguments[3][1:])
                    add_cx_gate_qubits(gate_id, control, target)
                else:
                    gate_id = int(arguments[2][1:])
                    qubit = int(arguments[1][1:])
                    add_single_gate_qubit(gate_id, qubit)

            elif action.startswith("swap") and "dummy" not in action:
                control = int(arguments[2][1:])
                target = int(arguments[3][1:])

                physical_circuit.swap(control, target)

                tmp = current_phys_map[control]
                current_phys_map[control] = current_phys_map[target]
                current_phys_map[target] = tmp

        num_lqubits = original_circuit.num_qubits
        if len(initial_mapping) != num_lqubits:
            mapping_string = ", ".join(
                f"{l} => {p}" for l, p in initial_mapping.items()
            )
            raise ValueError(
                f"Mapping '{mapping_string}' does not have the same number of qubits as the original circuit"
            )

        return physical_circuit, initial_mapping

    @abstractmethod
    def synthesize(
        self,
        logical_circuit: QuantumCircuit,
        platform: Platform,
        solver: Solver,
        time_limit_s: int,
        logger: Logger,
        cx_optimal: bool = False,
        depth_bound: Optional[int] = None,
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

    def synthesize_optimal(
        self,
        logical_circuit: QuantumCircuit,
        platform: Platform,
        solver: Solver,
        time_limit_s: int,
        logger: Logger,
        min_plan_length: int,
        max_plan_length: int,
        min_layers: int,
        max_layers: int,
        cnot_optimal: bool,
    ) -> SynthesizerOutput:

        remove_intermediate_files()

        circuit = (
            remove_all_non_cx_gates(logical_circuit)
            if cnot_optimal
            else logical_circuit
        )
        before = time.time()
        instance = self.create_instance(circuit, platform)
        domain, problem = instance.compile()
        solution, solver_time = solver.solve(
            domain,
            problem,
            time_limit_s,
            min_plan_length,
            max_plan_length,
            min_layers,
            max_layers,
        )
        after = time.time()
        total_time = after - before
        time_breakdown = (total_time, solver_time, None)

        match solution:
            case SolverTimeout():
                return SynthesizerTimeout()
            case SolverNoSolution():
                return SynthesizerNoSolution()
            case SolverSolution(actions):
                physical_circuit, initial_mapping = self.parse_solution(
                    circuit, platform, actions
                )

                if cnot_optimal:
                    physical_circuit = reinsert_unary_gates(
                        logical_circuit,
                        physical_circuit,
                        initial_mapping,
                        ancillaries=False,
                    )

                physical_circuit_with_cnots_as_swap = with_swaps_as_cnots(
                    physical_circuit, register_name="p"
                )
                depth = physical_circuit_with_cnots_as_swap.depth()
                physical_with_only_cnots = remove_all_non_cx_gates(
                    physical_circuit_with_cnots_as_swap
                )
                cx_depth = physical_with_only_cnots.depth()
                swaps = count_swaps(physical_circuit)
                return SynthesizerSolution(
                    physical_circuit,
                    initial_mapping,
                    time_breakdown,
                    depth,
                    cx_depth,
                    swaps,
                )
            case _:
                raise ValueError(f"Unexpected solution: {solution}")

    def synthesize_incremental(
        self,
        logical_circuit: QuantumCircuit,
        platform: Platform,
        solver: Solver,
        time_limit_s: int,
        logger: Logger,
        min_plan_length_lambda: Callable[[int], int],
        max_plan_length_lambda: Callable[[int], int],
        min_layers_lambda: Callable[[int], int],
        max_layers_lambda: Callable[[int], int],
        cnot_optimal: bool,
        depth_bound: Optional[int] = None,
    ) -> SynthesizerOutput:

        remove_intermediate_files()

        circuit = (
            remove_all_non_cx_gates(logical_circuit)
            if cnot_optimal
            else logical_circuit
        )

        circuit_depth = circuit.depth()
        max_depth = 4 * circuit_depth + 2
        if depth_bound is not None:
            max_depth = min(max_depth, depth_bound)

        solver_time = 0
        before = time.time()
        logger.log(1, "Searching: ", end="")
        for depth in range(circuit_depth, max_depth, 1):
            logger.log(1, f"depth {depth}, ", end="", flush=True)
            instance = self.create_instance(circuit, platform, maximum_depth=depth)
            domain, problem = instance.compile()

            time_left = int(time_limit_s - solver_time)
            min_plan_length = min_plan_length_lambda(depth)
            max_plan_length = max_plan_length_lambda(depth)
            min_layers = min_layers_lambda(depth)
            max_layers = max_layers_lambda(depth)

            solution, time_taken = solver.solve(
                domain,
                problem,
                time_left,
                min_plan_length,
                max_plan_length,
                min_layers,
                max_layers,
            )
            solver_time += time_taken
            after = time.time()
            total_time = after - before
            time_breakdown = (total_time, solver_time, None)

            match solution:
                case SolverTimeout():
                    logger.log(1, "")
                    return SynthesizerTimeout()
                case SolverNoSolution():
                    continue
                case SolverSolution(actions):
                    logger.log(1, "")
                    physical_circuit, initial_mapping = self.parse_solution(
                        circuit, platform, actions
                    )

                    if cnot_optimal:
                        physical_circuit = reinsert_unary_gates(
                            logical_circuit,
                            physical_circuit,
                            initial_mapping,
                            ancillaries=False,
                        )

                    physical_circuit_with_cnots_as_swap = with_swaps_as_cnots(
                        physical_circuit, register_name="p"
                    )
                    depth = physical_circuit_with_cnots_as_swap.depth()
                    physical_with_only_cnots = remove_all_non_cx_gates(
                        physical_circuit_with_cnots_as_swap
                    )
                    cx_depth = physical_with_only_cnots.depth()
                    swaps = count_swaps(physical_circuit)
                    return SynthesizerSolution(
                        physical_circuit,
                        initial_mapping,
                        time_breakdown,
                        depth,
                        cx_depth,
                        swaps,
                    )
                case _:
                    raise ValueError(f"Unexpected solution: {solution}")
        return SynthesizerNoSolution()


def remove_intermediate_files():
    for file in JUNK_FILES:
        file_exists = os.path.exists(file)
        if file_exists:
            os.remove(file)
