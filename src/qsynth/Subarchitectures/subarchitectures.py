#!/usr/bin/env python3

from typing import Optional

import time
from .subarchitecture_synthesis import (
    SubarchitectureSynthesis,
    MappingState,
    MappingSolution,
    convert_circuit_to_full_architecture,
)

from qiskit import QuantumCircuit, QuantumRegister

from qsynth.Utilities.result import MappingResult
from qiskit.circuit.library import CXGate

from ..CliffordSynthesis.circuit_utils import compute_cnot_cost, compute_cnotdepth_swaps_as_3cx, \
    compute_depth_swaps_as_3cx
from ..layout_synthesis_wrapper import layout_synthesis_wrapper as layout_synthesis_wrapper


def get_cx_count(circuit: QuantumCircuit) -> int:
    return circuit.count_ops().get("cx", 0)


def get_swap_count(circuit: QuantumCircuit) -> int:
    ops = circuit.count_ops()
    if "swap" in ops.keys():
        return ops["swap"]
    return 0


def get_cx_depth(circuit: QuantumCircuit) -> int:
    num_qubits = circuit.num_qubits
    qubit_name = circuit.qregs[0].name
    new_circuit = QuantumCircuit(QuantumRegister(num_qubits, qubit_name))
    for instr in circuit.data:
        if instr.name == "cx":
            new_circuit.append(instr.operation, instr.qubits)
        elif instr.name == "swap":
            q0 = instr.qubits[0]
            q1 = instr.qubits[1]
            cx_gate = CXGate()
            new_circuit.append(cx_gate, [q0, q1])
            new_circuit.append(cx_gate, [q1, q0])
            new_circuit.append(cx_gate, [q0, q1])
    return new_circuit.depth()


def get_opt_metric_desc(metric: str) -> str:
    match (metric):
        case "cx-count":
            return "CX-gates"
        case "cx-depth":
            return "CX-depth"
        case "depth":
            return "depth"
        case "depth_cx-count":
            return "depth"
        case "cx-depth_cx-count":
            return "CX-depth"
        case _:
            raise ValueError(f"Unexpected metric: {metric}")


def get_opt_val_from_metric(circuit: QuantumCircuit, metric: str) -> int:
    match (metric):
        case "cx-count":
            return compute_cnot_cost(circuit)
        case "cx-depth":
            return compute_cnotdepth_swaps_as_3cx(circuit)
        case "depth":
            return compute_depth_swaps_as_3cx(circuit)
        case "depth_cx-count":
            return compute_depth_swaps_as_3cx(circuit)
        case "cx-depth_cx-count":
            return compute_cnotdepth_swaps_as_3cx(circuit)
        case _:
            raise ValueError(f"Unexpected metric: {metric}")


def select_optimal_among_best(
    metric: str, solutions: list[MappingSolution]
) -> MappingSolution:

    match (metric):
        case "cx-count" | "cx-depth" | "depth":
            # Only single-value optimisation.
            # All solutions are equally good
            return solutions[0]
        case "depth_cx-count" | "cx-depth_cx-count":
            # Double-value optimisation.
            # Find solution with the minimal number of swaps
            best = solutions[0]
            for solution in solutions[1:]:
                if get_cx_count(solution.circuit) < get_cx_count(best.circuit):
                    best = solution
            return best
        case _:
            raise ValueError(f"Unexpected metric: {metric}")


def subarchitecture_mapping(
    circuit: QuantumCircuit,
    coupling_graph: list[list[int]],
    metric: str,
    parallel_swaps: bool,
    num_ancillary_qubits: int,
    search_strategy: str,
    swap_upper_bound: Optional[int],
    relaxed_dependencies: bool,
    cancel_cnots: bool,
    allow_bridges: bool,
    model: str,
    solver: Optional[str],
    intermediate_files_path: str,
    timeout: int,
    verbose: int,
) -> MappingResult:

    input_circuit = circuit

    num_physical_qubits = max(max(q1, q2) for q1, q2 in coupling_graph) + 1

    # Clamp number of ancillary qubits to be within valid range
    if (
        num_ancillary_qubits < 0
        or len(input_circuit.qubits) + num_ancillary_qubits > num_physical_qubits
    ):
        num_ancillary_qubits = num_physical_qubits - len(input_circuit.qubits)
        if verbose > 0:
            print(
                f"Limiting number of ancillary qubits to {num_ancillary_qubits}. Using full architecture."
            )

    # Prepare sub-architectures
    if verbose > 0:
        subarchitecture_time_start = time.perf_counter()
    sb = SubarchitectureSynthesis(
        len(input_circuit.qubits), coupling_graph, num_ancillary_qubits
    )
    if verbose > 0:
        subarchitecture_time = time.perf_counter() - subarchitecture_time_start

    if verbose > -1:
        print(
            f"Selected {len(sb.maximal_subarchitectures)} maximal subarchitectures from {len(sb.all_subarchitectures)} candidates"
        )
    if verbose > 0:
        print(f"Subarchitecture computation done in {subarchitecture_time}s")
        mapping_time_start = time.perf_counter()

    # Perform layout synthesis for each sub-architecture
    state = MappingState(solutions=list(), opt_val=None)
    for i, subarch in enumerate(sb.maximal_subarchitectures):

        if verbose > 0:
            print(
                f"Running layout-synthesis {i+1} of {len(sb.maximal_subarchitectures)}"
            )

        # Compute  graph of subarchitecture
        edge_list = list(map(list, subarch.edge_list()))

        if verbose > 0:
            qubit_map = dict(
                [(l, subarch.nodes()[l]) for edge in edge_list for l in edge]
            )
            print(f"Using sub-architecture mapping: {qubit_map}")

        # Limiting the search using upper bound only for sat
        if state.opt_val is not None and model == "sat":
            bound = state.opt_val
        else:
            bound = None

        if bound==0:
            break
        
        # Perform layout synthesis
        solve_time_start = time.perf_counter()
        synthesis_result = layout_synthesis_wrapper(
            circuit=input_circuit,
            coupling_graph=edge_list,
            model=model,
            allow_ancillas=True,
            relaxed_dependencies=bool(relaxed_dependencies),
            cancel_cnots=bool(cancel_cnots),
            allow_bridges=bool(allow_bridges),
            timeout=int(timeout - (time.perf_counter() - solve_time_start)),
            solver=solver,
            swap_upper_bound=swap_upper_bound,
            parallel_swaps=bool(parallel_swaps),
            intermediate_files_path=intermediate_files_path,
            verbose=verbose,
            metric=metric,
            search_strategy=search_strategy,
            initial_mapping=None
        )
        # circuit, opt_val = (
        #    synthesis_result if synthesis_result is not None else (None, None)
        # )
        circuit = synthesis_result.circuit if synthesis_result else None
        opt_val = get_opt_val_from_metric(circuit, metric) if circuit else None
        solve_time = time.perf_counter() - solve_time_start

        # Check if mapping was successful
        if circuit is None:
            if verbose > 0:
                print("Mapping not found for current sub-architecture.")
            continue

        if verbose > 0:
            opt_desc = get_opt_metric_desc(metric)
            print(f"Found mapping with {opt_val} {opt_desc} in {solve_time}s.")

        # Make the current solution
        solution = MappingSolution(
            circuit=circuit,
            architecture=subarch,
            initial_mapping=synthesis_result.initial_mapping,
            final_mapping=synthesis_result.final_mapping,
        )

        # Extract and update current results based on opt_val
        if state.opt_val is not None and opt_val > state.opt_val:
            # Solution exceeds bound
            continue

        if not state.solutions or state.opt_val is None or opt_val == state.opt_val:
            state.solutions.append(solution)
            state.opt_val = opt_val
        elif opt_val < state.opt_val:
            state.solutions = [solution]
            state.opt_val = opt_val

        # We do *not* terminate early on opt_val = 0.
        # This is because we wish to find all optimal solutions

    if verbose > 0:
        mapping_time = time.perf_counter() - mapping_time_start
        print(f"{mapping_time}s elapsed.")

    # Check if any mapping was found
    if not state.solutions:
        if verbose > -1:
            print("Mapping could not be found.")
        return None

    if verbose > -1:
        print(f"Completed mapping." f" Found {len(state.solutions)} solutions.")

    # Running post-processing to select best architecture
    solution = select_optimal_among_best(metric, state.solutions)
    if verbose > -1:
        print(
            "Best solution has "
            f"{get_swap_count(solution.circuit)} swaps "
            f"and {get_cx_depth(solution.circuit)} cx-depth."
        )

    # Convert circuit into full architecture
    mapped_circuit, initial_mapping, final_mapping = (
        convert_circuit_to_full_architecture(
            solution.circuit,
            solution.architecture,
            sb.full_architecture_size,
            solution.initial_mapping,
            solution.final_mapping,
        )
    )
    if verbose > 0:
        print("Final circuit mapped onto full architecture:")
        print(mapped_circuit)

    mapped_result = MappingResult(
        circuit=mapped_circuit,
        initial_mapping=initial_mapping,
        final_mapping=final_mapping,
    )
    # Return the final circuit
    return mapped_result
