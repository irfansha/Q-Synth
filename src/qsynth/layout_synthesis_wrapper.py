#!/usr/bin/env python3

from typing import Optional
from qiskit import QuantumCircuit


def layout_synthesis(
    circuit_in,
    circuit_out=None,
    platform=None,
    model="sat",
    solver=None,
    solver_time=1800,
    allow_ancillas=True,
    relaxed=0,
    bidirectional=1,
    bridge=0,
    start=None,
    step=1,
    end=None,
    check=0,
    verbose=1,
    cnot_cancel=0,
    cardinality=1,
    parallel_swaps=0,
    aux_files="./intermediate_files",
    metric="cx-count",
    coupling_graph=None,
    initial_mapping: Optional[dict[int, int]] = None,
    search_strategy: str = "forward",
) -> Optional[tuple[QuantumCircuit, int]]:

    # Resolve default planner when needed
    if model == "planning":
        match metric:
            case "cx-count":
                model = "local"
            case "cx-depth" | "depth" | "depth_cx-count" | "cx-depth_cx-count":
                model = "cond_cost_opt"

    # Select default compatible solver unless specified by user
    if solver is None:
        match model:
            case "sat":
                solver = "cd19"
            case "global" | "local" | "lifted" | "cost_opt" | "lc_incr":
                solver = "fd-bjolp"
            case "cond_cost_opt":
                solver = "fd-ms"
            case _:
                # NOTE: Removed early-termination here
                pass

    # Perform error-checking for incompatible options
    try:
        check_options(model, solver, metric)
    except ValueError as e:
        print(f"Error: {e}")
        return None

    # If initial mapping is specified, only use CNOT count optimization:
    if initial_mapping is not None:
        if metric != "cx-count":
            print(
                "Warning: Initial mapping is specified, but metric is not 'cx-count'. "
                "Using 'cx-count' metric for layout synthesis."
            )
        metric = "cx-count"
    # If search strategy is backwards, we only do CNOT count optimization:
    if search_strategy == "backwards":
        if metric != "cx-count":
            print(
                "Warning: Search strategy is 'backwards', but metric is not 'cx-count'. "
                "Using 'cx-count' metric for layout synthesis."
            )
        metric = "cx-count"

    # Call the right layout synthesis tool based on optimisation metric
    # TODO: Replace this match-case with if-statement using layout-config.py
    match metric:

        case "cx-count":
            from qsynth.LayoutSynthesis.layout_synthesis import (
                layout_synthesis as ls,
            )

            # Call std. layout synthesis
            return ls(
                circuit_in=circuit_in,
                circuit_out=circuit_out,
                platform=platform,
                model=model,
                solver=solver,
                solver_time=solver_time,
                allow_ancillas=allow_ancillas,
                relaxed=relaxed,
                bidirectional=bidirectional,
                bridge=bridge,
                start=start,
                step=step,
                end=end,
                verbose=verbose,
                cnot_cancel=cnot_cancel,
                cardinality=cardinality,
                parallel_swaps=parallel_swaps,
                aux_files=aux_files,
                check=check,
                coupling_graph=coupling_graph,
                initial_mapping=initial_mapping,
                search_strategy=search_strategy,
            )

        case "cx-depth" | "depth" | "depth_cx-count" | "cx-depth_cx-count":
            from qsynth.DepthOptimal.depthoptimal import depth_optimal_mapping

            # TODO:
            # Add error-messages and checking for all options not supported
            # by depth-optimal mapping.
            # For example:
            # bidirectional!=1, relaxed, bridge, cardinality, etc.

            return depth_optimal_mapping(
                circuit_in=circuit_in,
                circuit_out=circuit_out,
                output_initial=None,
                platform_name=platform,
                coupling_graph=coupling_graph,
                model=model,
                solver_name=solver,
                solver_time=solver_time,
                cx_optimal=(metric in ("cx-depth", "cx-depth_cx-count")),
                swap_optimal=(metric in ("depth_cx-count", "cx-depth_cx-count")),
                allow_ancillas=allow_ancillas,
                verbose=verbose,
                swap_bound=None,  # Do not use swap-bound in favor of depth-bound
                depth_bound=end,
            )

        case _:
            print("Error: Please specify an optimisation metric")
            return None


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
            f" Please use different --metric or a --model in {DEPTH_OPTIMAL_MODELS}"
        )

    if metric in SWAP_OPTIMAL_METRICS and model not in SWAP_OPTIMAL_MODELS:
        raise ValueError(
            f"Model '{model}' is not supported for count-metric '{metric}'.\n"
            f" Please use different --metric or a --model in {SWAP_OPTIMAL_MODELS}"
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
            "(the valid planners also depend on the --metric)"
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
