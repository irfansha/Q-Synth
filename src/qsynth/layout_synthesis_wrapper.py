#!/usr/bin/env python3

import time
from typing import Optional
from qiskit import QuantumCircuit

from qsynth.Utilities.coupling_graph import CouplingGraph
from qsynth.Utilities.result import MappingResult
from qsynth.layout_config import DEPTH_OPTIMAL_METRICS


def layout_synthesis_wrapper(
    circuit: QuantumCircuit,
    coupling_graph: CouplingGraph,
    metric: str,
    parallel_swaps: bool,
    allow_ancillas: bool,
    search_strategy: str,
    swap_upper_bound: Optional[int],
    initial_mapping: Optional[dict[int, int]],
    relaxed_dependencies: bool,
    cancel_cnots: bool,
    allow_bridges: bool,
    model: str,
    solver: Optional[str],
    intermediate_files_path: str,
    timeout: int,
    verbose: int,
) -> MappingResult:

    # Call the right layout synthesis tool based on optimisation metric
    if metric == "cx-count":
        from qsynth.LayoutSynthesis.layout_synthesis import (
            layout_synthesis as ls,
        )
        from qsynth.ReachabilitySolver.encodings.layout_synthesis.layout_reachability_synthesis import (
            layout_synthesis_using_reachability
        )

        is_reachability_strategy = search_strategy not in ["forward", "backward", "unbounded-forward"]
        options_implemented_for_reachability = (not allow_bridges and not relaxed_dependencies and model == "sat"
                and not initial_mapping and not parallel_swaps)
        if options_implemented_for_reachability and is_reachability_strategy:
            return layout_synthesis_using_reachability(
                circuit=circuit,
                upper_bound=swap_upper_bound,
                platform=None,
                coupling_graph=coupling_graph,
                strategy=search_strategy,
                allow_ancillas=allow_ancillas,
                intermediate_files_path=intermediate_files_path,
                timeout=timeout
            )

        # Call std. layout synthesis
        if search_strategy == "forward":
            start = 0
            end = swap_upper_bound
        else:
            start = swap_upper_bound
            end = 0
        return ls(
            circuit_in=circuit,
            circuit_out=None,
            platform=None,
            model=model,
            solver=solver,
            solver_time=timeout,
            allow_ancillas=allow_ancillas,
            relaxed=relaxed_dependencies,
            bidirectional=1, # TODO: Reintroduce bidirectional parameter if bidirectional=2 is important
            bridge=allow_bridges,
            start=start,
            step=1,
            end=end,
            verbose=verbose,
            cnot_cancel=cancel_cnots,
            parallel_swaps=parallel_swaps,
            aux_files=intermediate_files_path,
            check=0,
            coupling_graph=coupling_graph,
            initial_mapping=initial_mapping,
            search_strategy=search_strategy,
        )

    elif metric in DEPTH_OPTIMAL_METRICS:
        from qsynth.DepthOptimal.depthoptimal import depth_optimal_mapping

        # TODO:
        # Add error-messages and checking for all options not supported
        # by depth-optimal mapping.
        # For example:
        # bidirectional!=1, relaxed, bridge, cardinality, etc.

        return depth_optimal_mapping(
            circuit_in=circuit,
            circuit_out=None,
            output_initial=None,
            platform_name=None,
            coupling_graph=coupling_graph,
            model=model,
            solver_name=solver,
            solver_time=timeout,
            cx_optimal=(metric in ("cx-depth", "cx-depth_cx-count")),
            swap_optimal=(metric in ("depth_cx-count", "cx-depth_cx-count")),
            allow_ancillas=allow_ancillas,
            verbose=verbose,
            swap_bound=None,  # Do not use swap-bound in favor of depth-bound
            depth_bound=None,
        )
    elif metric == "cx-count_cx-depth":
        from qsynth.LayoutSynthesis.layout_synthesis import (
            layout_synthesis as count_optimal_mapping,
        )
        from qsynth.CliffordSynthesis.circuit_utils import (
            compute_cnotdepth_swaps_as_3cx,
        )
        from qsynth.DepthOptimal.depthoptimal import depth_optimal_mapping
        # First perform CNOT count optimal mapping
        if verbose >= 0:
            print("Starting cx-count optimal layout synthesis...")
        # Only setting options through API:
        start_time = time.time()
        intermediate_result = count_optimal_mapping(
                                circuit_in=circuit,
                                circuit_out=None,
                                coupling_graph=coupling_graph,
                                parallel_swaps=parallel_swaps,
                                solver_time=timeout,
                                verbose=verbose,
                                allow_ancillas=allow_ancillas,
                                )
        end_time = time.time()
        swap_count = intermediate_result.circuit.count_ops().get("swap", 0)
        cx_depth = compute_cnotdepth_swaps_as_3cx(intermediate_result.circuit)
        remaining_time = timeout - (end_time - start_time)
        if verbose >= 0:
            print(f"Starting cx-depth optimal layout synthesis...")
        # Then perform cx-depth optimal mapping using the swap count as bound
        return depth_optimal_mapping(
            circuit_in=circuit,
            circuit_out=None,
            output_initial=None,
            coupling_graph=coupling_graph,
            model=model,
            solver_name=solver,
            solver_time=remaining_time,
            cx_optimal=True,
            swap_optimal=False,
            allow_ancillas=allow_ancillas,
            verbose=verbose,
            swap_bound=swap_count,
            depth_bound=cx_depth,
        )
    else:
        raise ValueError(f"Unknown metric: {metric}")


def check_options(model: str, solver: str, metric: str):

    from qsynth.layout_config import (
        DEPTH_OPTIMAL_SOLVERS,
        SWAP_OPTIMAL_SOLVERS,
        PLANNING_SOLVERS,
        SAT_SOLVERS,
        DEPTH_OPTIMAL_METRICS,
        SWAP_OPTIMAL_METRICS,
        DEPTH_OPTIMAL_MODELS,
        SWAP_OPTIMAL_MODELS,
        PLANNING_MODELS,
        SAT_MODELS,
        CONDITIONAL_PLANNERS,
        CONDITIONAL_MODELS,
    )

    # Check compatibility of metric and model
    if metric in DEPTH_OPTIMAL_METRICS and model not in DEPTH_OPTIMAL_MODELS:
        raise ValueError(
            f"Model '{model}' is not supported for depth-metric '{metric}'.\n"
            f" Please use different metric or a model in {DEPTH_OPTIMAL_MODELS}"
        )

    if metric in SWAP_OPTIMAL_METRICS and model not in SWAP_OPTIMAL_MODELS:
        raise ValueError(
            f"Model '{model}' is not supported for count-metric '{metric}'.\n"
            f" Please use different metric or a model in {SWAP_OPTIMAL_MODELS}"
        )

    # Check compatibility of metric and solver
    if metric in SWAP_OPTIMAL_METRICS and solver not in SWAP_OPTIMAL_SOLVERS:
        raise ValueError(
            f"Solver '{solver}' is not supported for count-metric '{metric}'.\n"
            f" Please use one of the following solvers: {SWAP_OPTIMAL_SOLVERS}"
        )

    if metric in DEPTH_OPTIMAL_SOLVERS and solver not in DEPTH_OPTIMAL_SOLVERS:
        raise ValueError(
            f"Solver '{solver}' is not supported for depth-metric '{metric}'.\n"
            f" Please use one of the following solvers: {DEPTH_OPTIMAL_SOLVERS}"
        )

    # Check compatibility of model and solver (planning vs sat)
    if model in PLANNING_MODELS and solver not in PLANNING_SOLVERS:
        raise ValueError(
            f"Solver '{solver}' is not supported for planning model '{model}'.\n"
            f" Please use one of the following solvers: {PLANNING_SOLVERS}"
            "(the valid planners also depend on the choice of metric)"
        )

    if model in SAT_MODELS and solver not in SAT_SOLVERS:
        raise ValueError(
            f"Solver '{solver}' is not supported for 'sat'-based solving.\n"
            f" Please use one of the following solvers: {SAT_SOLVERS}"
        )

    # Check compatibility of conditional planning models and solvers
    if model in CONDITIONAL_MODELS and solver not in CONDITIONAL_PLANNERS:
        raise ValueError(
            f"Model '{model}' uses conditional effects, but Solver '{solver}' doesn't support it.\n"
            f" Please use one of the conditional planning solvers: {CONDITIONAL_PLANNERS}"
        )
