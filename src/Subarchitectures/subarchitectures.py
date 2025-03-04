#!/usr/bin/env python3

from typing import Optional

import time
from src.Subarchitectures.subarchitecture_synthesis import (
    SubarchitectureSynthesis,
    MappingState,
    MappingSolution,
    convert_circuit_to_full_architecture,
)

from qiskit import QuantumCircuit, QuantumRegister
from src.LayoutSynthesis.architecture import platform as parse_platform


def get_cx_count(circuit: QuantumCircuit) -> int:
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
    return new_circuit.depth()


def get_opt_metric_desc(metric: str) -> str:
    match (metric):
        case "cx-count":
            return "CX-gates"
        case "cx-depth":
            return "CX-depth"
        case "depth":
            return "depth"
        case "depth-cx-count":
            return "depth"
        case "cx-depth-cx-count":
            return "CX-depth"
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
        case "depth-cx-count" | "cx-depth-cx-count":
            # Double-value optimisation.
            # Find solution with the minimal number of swaps
            best = solutions[0]
            for solution in solutions[1:]:
                if get_cx_count(solution.circuit) < get_cx_count(best.circuit):
                    best = solution
            return best


def subarchitecture_mapping(
    circuit_in=None,
    circuit_out=None,
    platform="malbourne",
    model="sat",
    solver=None,
    solver_time=1800,
    num_ancillary_qubits=0,
    relaxed=0,
    bidirectional=1,
    bridge=0,
    start=0,
    step=1,
    end=None,
    verbose=0,
    cnot_cancel=0,
    cardinality=1,
    parallel_swaps=0,
    aux_files="./intermediate_files",
    check=0,
    metric="cx-count",
    layout_synthesis_method=None,
) -> Optional[tuple[QuantumCircuit, int]]:

    # Layout synthesis tool injection is required
    if layout_synthesis_method is None:
        print("Error: Layout synthesis tool is not supplied.")
        return

    # Assume a bidirectional platform
    if not bidirectional == 1:
        print("Error: Subarchitectures assume a bidirectional platform.")
        return

    # Step size 1 required for progressive bounding
    if not step == 1:
        print("Error: Subarchitectures assume a step size of 1.")
        return

    # Parse circuit from file
    try:
        input_circuit = QuantumCircuit.from_qasm_file(circuit_in)
    except FileNotFoundError:
        print(f"Error: circuit_in file '{circuit_in}' not found")
        return None

    # Parse full platform to extract coupling graph
    (coupling_graph, _, _, _, _, num_physical_qubits) = parse_platform(
        platform=platform, bidirectional=True, coupling_graph=None, verbose=verbose
    )

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
    subarchitecture_time_start = time.perf_counter()
    sb = SubarchitectureSynthesis(
        len(input_circuit.qubits), coupling_graph, num_ancillary_qubits
    )
    subarchitecture_time = time.perf_counter() - subarchitecture_time_start

    if verbose > -1:
        print(
            f"Selected {len(sb.maximal_subarchitectures)} maximal subarchitectures from {len(sb.all_subarchitectures)} candidates"
        )
        print(f"Subarchitecture computation done in {subarchitecture_time}s")

    # Perform layout synthesis for each sub-architecture
    state = MappingState(solutions=list(), opt_val=None if end is None else end)
    mapping_time_start = time.perf_counter()
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

        # Perform layout synthesis
        solve_time_start = time.perf_counter()
        synthesis_result = layout_synthesis_method(
            circuit_in,
            circuit_out,
            platform="custom",
            bidirectional=1,
            model=model,
            allow_ancillas=True,
            relaxed=relaxed,
            cnot_cancel=cnot_cancel,
            bridge=bridge,
            solver_time=(solver_time - (time.perf_counter() - solve_time_start)),
            solver=solver,
            cardinality=cardinality,
            start=start,
            step=1,
            end=bound,
            parallel_swaps=parallel_swaps,
            aux_files=aux_files,
            check=check,
            verbose=0,
            metric=metric,
            coupling_graph=edge_list,
        )
        circuit, opt_val = (
            synthesis_result if synthesis_result is not None else (None, None)
        )
        solve_time = time.perf_counter() - solve_time_start

        # Check if mapping was successful
        if circuit is None:
            print("Mapping not found for current sub-architecture.")
            continue

        if verbose > 0:
            opt_desc = get_opt_metric_desc(metric)
            print(f"Found mapping with {opt_val} {opt_desc} in {solve_time}s.")

        # Make the current solution
        solution = MappingSolution(circuit=circuit, architecture=subarch)

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

    mapping_time = time.perf_counter() - mapping_time_start
    if verbose > -1:
        print(f"{mapping_time}s elapsed.")

    # Check if any mapping was found
    if not state.solutions:
        print("Mapping could not be found.")
        return None

    print(
        f"Completed mapping of {circuit_in}."
        f" Found {len(state.solutions)} solutions."
    )
    print("Running post-processing.")

    # Running post-processing to select best architecture
    solution = select_optimal_among_best(metric, state.solutions)
    print(
        "Best solution has "
        f"{get_cx_count(solution.circuit)} swaps "
        f"and {get_cx_depth(solution.circuit)} cx-depth."
    )

    # Convert circuit into full architecture
    mapped_circuit = convert_circuit_to_full_architecture(
        solution.circuit, solution.architecture, sb.full_architecture_size
    )

    if verbose > 0:
        print("Final circuit mapped onto full architecture:")
        print(mapped_circuit)

    # Perform testing of final circuit
    if check:
        # TODO: Implement testing
        pass

    # Return the final circuit
    return mapped_circuit, state.opt_val
