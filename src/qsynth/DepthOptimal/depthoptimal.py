#!/usr/bin/env python3
from typing import Optional

from qiskit import QuantumCircuit
from qsynth.LayoutSynthesis.architecture import platform as parse_platform

from qsynth.DepthOptimal.configs import (
    CONDITIONAL_PLANNING_SYNTHESIZERS,
    synthesizers,
    solvers,
    OPTIMAL_PLANNING_SYNTHESIZERS,
)

from qsynth.DepthOptimal.util.logger import Logger
from qsynth.DepthOptimal.util.circuits import (
    SynthesizerNoSolution,
    make_final_mapping,
    remove_all_non_cx_gates,
    SynthesizerSolution,
    save_circuit,
    save_initial_mapping,
)

from qsynth.DepthOptimal.util.output_checker import (
    connectivity_check,
    equality_check,
)
from qsynth.DepthOptimal.synthesizers.planning.solvers import OPTIMAL
from qsynth.DepthOptimal.synthesizers.planning.synthesizer import (
    PlanningSynthesizer,
)
from qsynth.DepthOptimal.synthesizers.sat.synthesizer import SATSynthesizer
import qsynth.DepthOptimal.synthesizers.planning.solvers as planning

from qsynth.DepthOptimal.platform import Platform

from qsynth.Utilities.result import MappingResult


def do_error_checking(
    solver,
    synthesizer,
    model,
    swap_bound,
    swap_optimal,
    platform_qubits,
    circuit_qubits,
    depth_bound,
) -> None:

    # Check for inconsistent options
    if swap_bound is not None and swap_optimal:
        raise ValueError(
            "Cannot specify both a SWAP bound and SWAP optimization. Choose one at maximum."
        )

    if depth_bound is not None and model != "sat":
        raise ValueError("Can only specify depth-bound with 'sat' model.")

    # Check that the choice of solver and synthesizer/model is consistent
    if isinstance(solver, planning.Solver) and isinstance(
        synthesizer, PlanningSynthesizer
    ):
        is_opt_planner = model in OPTIMAL_PLANNING_SYNTHESIZERS
        if is_opt_planner and solver.solver_class != OPTIMAL:
            available_solvers = [
                solver_str
                for solver_str, solver in solvers.items()
                if isinstance(solver, planning.Solver)
                and solver.solver_class == OPTIMAL
            ]
            raise ValueError(
                f"Model '{model}' requires optimal solver, but solver '{solver}' is not optimal.\n"
                f"Please choose one of the following optimal solvers: {', '.join(available_solvers)}"
            )
        uses_conditionals = model in CONDITIONAL_PLANNING_SYNTHESIZERS
        if uses_conditionals and not solver.accepts_conditional:
            available_solvers = [
                solver_str
                for solver_str, solver in solvers.items()
                if isinstance(solver, planning.Solver) and solver.accepts_conditional
            ]
            raise ValueError(
                f"Model '{model}' uses conditional effects, but solver '{model}' does not support those.\n"
                f"Please choose one of the following conditional solvers: {', '.join(available_solvers)}"
            )
        if isinstance(solver, planning.Solver) and isinstance(
            synthesizer, SATSynthesizer
        ):
            available_solvers = [
                solver_str
                for solver_str, solver in solvers.items()
                if not isinstance(solver, planning.Solver)
            ]
            raise ValueError(
                f"Model '{model}' is a SAT model, but solver '{solver}' is a planning solver.\n"
                f"Please choose one of the following SAT solvers: {', '.join(available_solvers)}"
            )
        if (not isinstance(solver, planning.Solver)) and isinstance(
            synthesizer, PlanningSynthesizer
        ):
            opt_synth = model in OPTIMAL_PLANNING_SYNTHESIZERS
            cond_synth = model in CONDITIONAL_PLANNING_SYNTHESIZERS
            available_solvers = [
                solver_str
                for solver_str, solver in solvers.items()
                if isinstance(solver, planning.Solver)
                and ((not opt_synth) or (solver.solver_class == OPTIMAL))
                and ((not cond_synth) or solver.accepts_conditional)
            ]
            raise ValueError(
                f"Model '{model}' is a planning model, but solver '{solver}' is a SAT solver.\n"
                f"Please choose one of the following planning solvers: {', '.join(available_solvers)}"
            )

        if swap_bound and not isinstance(synthesizer, SATSynthesizer):
            raise ValueError(
                "Cannot specify a SWAP bound with a planning model. Please choose a SAT model."
            )

        if swap_optimal and not isinstance(synthesizer, SATSynthesizer):
            raise ValueError(
                "Cannot specify SWAP optimization with a planning model. Please choose a SAT model."
            )

        if platform_qubits < circuit_qubits:
            raise ValueError(
                f"Circuit has {circuit_qubits} logical qubits, but platform only has {platform_qubits} physical qubits."
            )


def depth_optimal_mapping(
    circuit_in,
    circuit_out=None,
    platform_name="melbourne",
    coupling_graph=None,
    model="sat",
    solver_name=None,
    solver_time=1800,
    output_initial=None,
    cx_optimal=True,
    swap_optimal=True,
    allow_ancillas=True,
    verbose=0,
    swap_bound=None,
    depth_bound=None,
    check=False,
) -> Optional[tuple[QuantumCircuit, int]]:

    # Parse inputs
    try:
        synthesizer = synthesizers[model]
    except KeyError:
        print(
            f"Error: Synthesizer '{model}' is not supported for depth-optimal layout synthesis."
        )
        return None

    try:
        solver = solvers[solver_name]()
    except KeyError:
        print(
            f"Error: Solver '{solver_name}' is not supported for depth-optimal layout synthesis."
        )
        return None

    # Parse platform with optional coupling_graph
    (platform, _, _, _, _, num_pqubits) = parse_platform(
        platform=platform_name,
        bidirectional=True,
        coupling_graph=coupling_graph,
        verbose=verbose,
    )
    # Convert platform to Platform object
    platform = Platform(
        name=platform_name,
        qubits=num_pqubits,
        connectivity_graph={tuple(e) for e in platform},
    )

    # we assume that the input circuit is a Qiskit QuantumCircuit
    input_circuit = circuit_in
    # Compute stripped circuit
    input_circuit_only_cx = remove_all_non_cx_gates(input_circuit)

    # Set logger level
    logger = Logger(verbose + 1)

    # Perform comptability checking to ensure
    # that arguments provided are valid options for Depth Optimal Synthesis
    try:
        do_error_checking(
            solver=solver,
            synthesizer=synthesizer,
            model=model,
            swap_bound=swap_bound,
            swap_optimal=swap_optimal,
            platform_qubits=num_pqubits,
            circuit_qubits=input_circuit.num_qubits,
            depth_bound=depth_bound,
        )
    except ValueError as e:
        print(f"Error: Incompatible argument(s) specified:\n{e}")
        return None

    # Print information
    # if verbose >= 0:
    #   print(f"Input circuit: {circuit_in}")
    if verbose > 0:
        print(input_circuit)

    if verbose > 0:
        print(
            f"Depth: {input_circuit.depth()}, CX-depth: {input_circuit_only_cx.depth()}"
        )
        print(f"Platform: {platform.name}")
        print(f"Synthesizer: '{model}' : {synthesizer.description}")
        print("Solver: ", end="")
        if isinstance(solver, planning.Solver):
            print(
                f"'{solver_name}' ({'optimal' if solver.solver_class==OPTIMAL else 'satisfying'}): {solver.description}"
            )
        else:
            print(f"'{solver_name}' from the pysat library.")

    # Start layout synthesis
    if verbose > 0:
        print(
            f"Synthesizing ({'CX-depth' if cx_optimal else 'depth'}-optimal{' and local SWAP-optimal' if swap_optimal else ''}{f' with SWAP bound {swap_bound}' if swap_bound else ''}{', allowing ancillary SWAPs' if allow_ancillas else ''})",
            flush=True,
        )

    match synthesizer, solver:
        case PlanningSynthesizer(), planning.Solver():
            output = synthesizer.synthesize(
                input_circuit,
                platform,
                solver,
                int(solver_time),
                logger,
                cx_optimal=cx_optimal,
            )
        case SATSynthesizer(), _ if not isinstance(solver, planning.Solver):
            output = synthesizer.synthesize(
                input_circuit,
                platform,
                solver,
                solver_time,
                logger,
                cx_optimal=cx_optimal,
                swap_optimal=swap_optimal,
                ancillaries=allow_ancillas,
                swap_bound=swap_bound,
                depth_bound=depth_bound,
            )
        case _:
            print(
                f"Error: Invalid synthesizer-solver combination: '{model}' on '{solver_name}'."
            )
            return None

    if verbose >= 1:
        print(output)

    # Convert output back into circuit
    match output:
        case SynthesizerSolution():

            # Proceed to handle output circuit
            should_output_circuit = circuit_out is not None
            should_output_initial_mapping = output_initial is not None

            if should_output_circuit or should_output_initial_mapping:

                if verbose >= 0:
                    print("Saving information:")

                if should_output_circuit:
                    save_circuit(output.circuit, circuit_out)

                    if verbose >= 0:
                        print(f"Saved synthesized circuit at '{circuit_out}'")

                    if should_output_initial_mapping:
                        save_initial_mapping(output.initial_mapping, output_initial)

                        if verbose >= 0:
                            print(
                                f"Saved initial mapping of synthesized circuit at '{output_initial}'"
                            )

            if verbose >= 0:
                print(
                    f"Completed mapping with {output.swaps} swaps and {output.cx_depth} cx-depth."
                )
            if verbose > 0:
                print(output.report_time())

            if check:
                if verbose >= 0:
                    print("Validation:")

                # Check connectivity
                correct_connectivity = connectivity_check(output.circuit, platform)
                if verbose >= 0:
                    if correct_connectivity:
                        print(
                            "✓ Output circuit obeys connectivity of platform (Proprietary Checker)"
                        )
                    else:
                        print(
                            "✗ Output circuit does not obey connectivity of platform (Proprietary Checker)"
                        )
                        raise Exception("Connectivity check failed")

                # Check equality
                correct_output = equality_check(
                    input_circuit,
                    output.circuit,
                    output.initial_mapping,
                    allow_ancillas,
                )
                if verbose >= 0:
                    if correct_output:
                        print(
                            "✓ Input and output circuits are equivalent (Proprietary Checker)"
                        )
                    else:
                        print(
                            "✗ Input and output circuits are not equivalent (Proprietary Checker)"
                        )
                        raise Exception("Equality check failed")
            # Get the optimisation value
            opt_val = 0
            match (cx_optimal, swap_optimal):
                # TODO:
                # Return multiple optimisation values
                # when optimising for both depth and swap count
                case False, False:  # depth
                    opt_val = output.depth
                case False, True:  # depth_cx-count
                    opt_val = output.depth
                case True, False:  # cx-depth
                    opt_val = output.cx_depth
                case True, True:  # cx-depth_cx-count
                    opt_val = output.cx_depth

            # Return output circuit and optimisation value
            output_mapping = make_final_mapping(
                circuit=output.circuit,
                initial_mapping=output.initial_mapping,
                ancillaries=allow_ancillas,
            )
            # Convert to int->int
            initial_mapping = {k.id: v.id for k, v in output.initial_mapping.items()}
            output_mapping = {k.id: v.id for k, v in output_mapping.items()}
            mapped_result = MappingResult(
                circuit=output.circuit,
                opt_val=opt_val,
                initial_mapping=initial_mapping,
                final_mapping=output_mapping,
            )
            return mapped_result

        case SynthesizerNoSolution():
            if verbose > -1:
                print("No mapping found.")
            return None
        case _:
            print("Error: synthesizer solution not recognized.")
            exit(-1)
