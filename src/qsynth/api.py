# Exposing functions only with the relevant options in relevant format for the API.
from .CliffordSynthesis.circuit_utils import compute_cnot_cost, compute_cnotdepth_swaps_as_3cx, \
    compute_cnot_without_swaps_cost, compute_cnot_depth, compute_oneq_gate_count
from qsynth.Synthesizers.cnot_rz_synthesizer import CnotRzSynthesizer
from qsynth.Synthesizers.cnot_synthesizer import CnotSynthesizer
from qsynth.Synthesizers.clifford_synthesizer import CliffordSynthesizer
from qsynth.Synthesizers.disable_unused_qubits_synthesizer import UnusedQubitsDisabled
from .ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import get_used_qubits
from .Subarchitectures.subarchitectures import subarchitecture_mapping
from qsynth.Synthesizers.configs import LayoutSynthesisConfig, CnotSynthesisConfig, CnotRzSynthesisConfig, \
    CliffordSynthesisConfig
from .Utilities.coupling_graph import CouplingGraph
from .layout_synthesis_wrapper import layout_synthesis_wrapper as ls
from .LayoutSynthesis.architecture import platform as pt
from .peephole_synthesis import peephole_synthesis_general
from .CnotSynthesis.cnot_synthesis import coupling_graph_check
from .PeepholeSlicing.circuit_utils import remove_zero_cost_swaps, is_clifford_circuit, \
    check_equivalence_of_clifford_circuits, check_equivalence_of_arbitrary_circuits, is_cnot_circuit, is_cnot_rz_circuit
from .Utilities.result import MappingResult
from typing import Optional
from qiskit.circuit.quantumcircuit import QuantumCircuit
from qsynth.Utilities.print_utils import print_stats


def get_coupling_graph(
        platform: str,
        bidirectional: bool = True
) -> CouplingGraph:
    """
    Return a coupling graph based on the specified platform.
    Parameters:
        platform (str): The name of the platform from which to retrieve the coupling graph.
        bidirectional (bool, optional): If True, the coupling graph is made bidirectional, otherwise it is unidirectional. Defaults to True.

    Returns:
        list[list[int]]: The resulting coupling graph retrieved from the platform.

    Raises:
        ValueError: If `platform` is not a known platform.
    """
    coupling_graph = pt(
        platform=platform,
        bidirectional=bidirectional,
        coupling_graph=None
    )[1]
    return coupling_graph


def make_bidirectional_graph(coupling_graph: CouplingGraph) -> CouplingGraph:
    """
    Takes a coupling graph as input and returns its bidirectional equivalent.
    """
    # Remove duplicates while preserving order
    bidirectional_graph = list(dict.fromkeys((x,y) for x,y in coupling_graph))
    # Add reverse direction
    bidirectional_graph += [(y, x) for x, y in coupling_graph if (y, x) not in bidirectional_graph]
    return sorted([x,y] for x,y in bidirectional_graph)


def layout_synthesis(
        circuit: QuantumCircuit,
        coupling_graph: CouplingGraph,
        metric: str = "cx-count",
        secondary_metric: Optional[str] = None,
        parallel_swaps: bool = False,
        subarchitecture: Optional[bool] = None,
        num_ancillary_qubits: Optional[int] = None,
        search_strategy: str = "forward",
        swap_upper_bound: Optional[int] = None,
        initial_mapping: Optional[dict[int, int]] = None,
        relaxed_dependencies: bool = False,
        cancel_cnots: bool = False,
        allow_bridges: bool = False,
        model: str = "sat",
        solver: Optional[str] = None,
        check: bool = False,
        intermediate_files_path: str = "./intermediate_files",
        timeout: int | float = 1800,
        verbose: int = -1,
) -> MappingResult:
    """
    Layout synthesis for a given quantum circuit and coupling graph.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be synthesized.
        coupling_graph (list[tuple[int, int]]): The coupling graph representing
            the connectivity of the quantum hardware.
        metric (str, optional): The optimization metric to use. Options are "cx-count" (number of CNOT gates),
            "cx-depth" (depth of CNOT gates), and "depth" (total circuit depth). The output circuit will be optimal
            considering this metric.
            Defaults to "cx-count".
        secondary_metric (Optional[str], optional): If provided, a second optimization run will optimize this metric
            while bounding the optimal value of the primary metric. Note that "depth" and "cx-depth" cannot be combined
            as primary/secondary metrics.
            Options are "cx-count" (number of CNOT gates), "cx-depth" (depth of CNOT gates).
            Defaults to None.
        parallel_swaps (bool): If True, applies parallel swaps optimizing swap makespan. If False, applies sequential
            swaps optimizing swap count. Only compatible with metric='cx-count'.
            Defaults to False.
        subarchitecture (Optional[bool], optional): If True, performs subarchitecture mapping. If False, performs direct
            mapping. Defaults to False, unless a positive number is given for num_ancillary_qubits.
        num_ancillary_qubits (Optional[int], optional): Specifies the number of ancillary qubits to use, -1 indicates any number of ancillary qubits.
            If subarchitecture mapping is enabled, defaults to 0.
            If subarchitecture mapping is disabled, defaults to -1 (any number of ancillary qubits).
            If a positive number is given, subarchitecture mapping must not be disabled.
        search_strategy (str, optional): The search strategy to use, either "forward" or "backward".
            Defaults to "forward".
        swap_upper_bound (Optional[int], optional): The upper bound on the number of swaps for the
            "backward" search strategy. Must be specified if using "backward". Defaults to None.
        initial_mapping (Optional[list[int]], optional): A predefined initial mapping of qubits. If
            provided, direct synthesis mapping is performed, so subarchitecture mapping must be disabled.
            Giving an initial mapping is only compatible with metric='cx-count'.
            Defaults to None.
        relaxed_dependencies (bool, optional): If True, uses relaxed dependencies. Defaults to False.
        cancel_cnots (bool, optional): If True, allows CNOT gates to be canceled. Defaults to False.
        allow_bridges (bool, optional): If True, allows bridge gates in the mapped circuit. Defaults to False.
        model (str, optional): The model to use for solving the optimization problem. Basic options are "sat" and "planning".
            Defaults to "sat".
        solver (Optional[str], optional): The name of the solver to use.
            For planning models, choose a planner-tool combination. Options are "fd-bjolp" (default), "fd-ms",
            "madagascar", "fd-lmcut", "fdss-sat", "fdss-opt-1", or "fdds-opt-2".
            Note that you must have the chosen planner installed and accessible from your PATH.
            For the SAT model, choose a PySAT solver name (defaults to "cadical195"). See all PySAT solvers at
            https://pysathq.github.io/docs/html/api/solvers.html#pysat.solvers.SolverNames.
        check (bool, optional): If True, checks equivalence between original and mapped circuit while considering the
            initial and final mapping. Also checks that the mapped circuit matches the coupling graph. Defaults to False.
        intermediate_files_path (str, optional): The path in which to place intermediate files.
            Defaults to "./intermediate_files".
        timeout (int | float, optional): The maximum time (in seconds) allowed for the synthesis process.
            Defaults to 1800.
        verbose (int, optional): The verbosity level for logging. Higher values produce more detailed
            output. Options are -1 to 3 (included). Defaults to -1 (silent).
    Returns:
        MappingResult: The result of the layout synthesis, including the optimized circuit and final mapping.
    Raises:
        ValueError: If the parameters given are invalid or incompatible.
        AssertionError: If the equivalence check or coupling graph check is unsuccessful.
    """
    num_physical_qubits = max(max(qi, qj) for qi, qj in coupling_graph) + 1
    if num_physical_qubits < circuit.num_qubits:
        raise ValueError(f"The number of physical qubits must be ≥ than the number of logical qubits.\n"
                         f"Got{num_physical_qubits} physical qubits and {circuit.num_qubits} logical qubits.")

    # Config automatically sets defaults and validates options
    config = LayoutSynthesisConfig(
        metric=metric,
        secondary_metric=secondary_metric,
        parallel_swaps=parallel_swaps,
        subarchitecture=subarchitecture,
        num_ancillary_qubits=num_ancillary_qubits,
        search_strategy=search_strategy,
        swap_upper_bound=swap_upper_bound,
        initial_mapping=initial_mapping,
        relaxed_dependencies=relaxed_dependencies,
        cancel_cnots=cancel_cnots,
        allow_bridges=allow_bridges,
        model=model,
        solver=solver,
        intermediate_files_path=intermediate_files_path,
        timeout=timeout,
        verbose=verbose,
    )

    print_org_circuit(circuit, verbose)

    # For now, convert primary/secondary metric to metric argument
    metric = config.metric
    if secondary_metric is not None:
        metric += f"_{config.secondary_metric}"

    if config.subarchitecture:
        result = subarchitecture_mapping(
            circuit=circuit,
            coupling_graph=coupling_graph,
            metric=metric,
            parallel_swaps=config.parallel_swaps,
            num_ancillary_qubits=config.num_ancillary_qubits,
            search_strategy=config.search_strategy,
            swap_upper_bound=config.swap_upper_bound,
            relaxed_dependencies=config.relaxed_dependencies,
            cancel_cnots=config.cancel_cnots,
            allow_bridges=config.allow_bridges,
            model=config.model,
            solver=config.solver,
            intermediate_files_path=config.intermediate_files_path,
            timeout=config.timeout,
            verbose=config.verbose
        )
    else:
        result = ls(
            circuit=circuit,
            coupling_graph=coupling_graph,
            metric=metric,
            parallel_swaps=config.parallel_swaps,
            allow_ancillas=True if config.num_ancillary_qubits == -1 else False,
            search_strategy=config.search_strategy,
            swap_upper_bound=config.swap_upper_bound,
            initial_mapping=config.initial_mapping,
            relaxed_dependencies=config.relaxed_dependencies,
            cancel_cnots=config.cancel_cnots,
            allow_bridges=config.allow_bridges,
            model=config.model,
            solver=config.solver,
            intermediate_files_path=config.intermediate_files_path,
            timeout=config.timeout,
            verbose=config.verbose,
        )

    print_optimization_complete(verbose)

    if check:
        check_correctness(circuit, result, coupling_graph, verbose)

    print_result_and_stats(circuit, result, verbose)

    return result


# Search strategy based on coupling graph:
def get_search_strategy(circuit, coupling_graph):
    """
    Determines the search strategy based on the coupling graph.
    If coupling graph is provided and the circuit is not compatible, we use 'unbounded-forward' search strategy.
    Else we use 'forward' search strategy.
    """
    if coupling_graph is not None and not check_coupling_graph(
            circuit, coupling_graph, raise_error=False
    ):
        search_strategy = "unbounded-forward"
    else:
        search_strategy = "forward"
    return search_strategy


def cnot_synthesis(
        circuit: QuantumCircuit,
        metric: str = "cx-depth",
        bound_metric: Optional[str] = None,
        coupling_graph: Optional[CouplingGraph] = None,
        output_qubit_permute: bool = False,
        search_strategy: str = "forward",
        model: str = "sat",
        solver: Optional[str] = None,
        check: bool = False,
        intermediate_files_path: str = "./intermediate_files",
        timeout: int | float = 1800,
        verbose: int = -1,
) -> MappingResult:
    """
    Perform CNOT (count/depth) optimization on a given quantum circuit consisting only of CNOT and SWAP gates.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized. The circuit should only contain CNOT and
            SWAP gates.
        metric (str, optional): The optimization metric to use. Options are "cx-depth" (depth of CNOT gates)
            and "cx-count" (number of CNOT gates). Defaults to "cx-depth".
        bound_metric (Optional[str], optional): If specified, the optimization will be bounded by this metric. For
            instance bounding "cx-count" while optimizing for "cx-depth" will return a circuit with the minimal CNOT
            depth while not increasing the CNOT count. Options are "cx-count" and "cx-depth". Defaults to None.
        coupling_graph (Optional[list[tuple[int, int]]], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. The input circuit must be compatible with the graph. Defaults to None.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the optimized circuit.
            Defaults to False.
        search_strategy (str, optional): The optimization strategy to use. Basic options are "forward" and "backward".
            Other options are reachability-based strategies: "k-step", "inc", "going-up", "going-down", "binary",
            and "maxsat".
            Defaults to "forward".
        model (str, optional): The model to use for optimization. Options are "planning", "qbf", and "sat".
            Defaults to "sat".
        solver (Optional[str], optional): The solver to use for optimization. For model="sat" options are "cd"
            (CaDiCal binary), or any PySAT solver with "pysat-[pysat_solver_name]". Defaults to "pysat-cd19" for SAT solving.
            For model="planning" options are "fd-ms" (FastDownward using merge-and-shrink, default), "lama" or "madagascar".
            For model="qbf" the only option is "caqe" which uses the CAQE solver with the Bloqqer preprocessor.
        check (bool, optional): If True, checks equivalence between original and mapped circuit while considering the
            final mapping of qubits. Also checks that the mapped circuit matches the coupling graph if such is provided.
            Defaults to False.
        intermediate_files_path (str, optional): The path in which to place intermediate files.
            Defaults to "./intermediate_files".
        timeout (int | float, optional): The maximum time (in seconds) allowed for the optimization process.
            Defaults to 1800.
        verbose (int, optional): The verbosity level for logging. -1 for silent. Higher values produce
            more detailed output. Defaults to -1.
    Returns:
        MappingResult: The result of the CNOT optimization, including the optimized circuit and final mapping.
    Raises:
        ValueError: If the provided arguments are invalid or incompatible.
    Notes:
        - If "output_qubit_permute" is enabled, zero-cost swaps are removed from the optimized
          circuit. The result will contain the final mapping of the logical qubits.
    """
    if not is_cnot_circuit(circuit):
        raise ValueError(f"The input circuit may only contain CNOT and SWAP gates.")

    if search_strategy=="forward":
        search_strategy = get_search_strategy(circuit, coupling_graph)

    # Config automatically sets defaults and validates
    config = CnotSynthesisConfig(
        metric=metric,
        bound_metric=bound_metric,
        output_qubit_permute=output_qubit_permute,
        search_strategy=search_strategy,
        model=model,
        solver=solver,
        intermediate_files_path=intermediate_files_path,
        verbose=verbose,
    )

    print_org_circuit(circuit, verbose)

    result = CnotSynthesizer(config).run(circuit, coupling_graph, timeout)

    print_optimization_complete(verbose)

    # if qubit permute is enabled, we remove zero-cost swaps:
    if config.output_qubit_permute:
        result = handle_zero_cost_swaps(result, circuit.num_qubits)

    if check:
        check_correctness(circuit, result, coupling_graph, verbose)

    print_result_and_stats(circuit, result, verbose)

    return result


def cnot_peephole_synthesis(
        circuit: QuantumCircuit,
        metric: str = "cx-depth",
        bound_metric: Optional[str] = None,
        coupling_graph: Optional[CouplingGraph] = None,
        output_qubit_permute: bool = False,
        search_strategy: str = "forward",
        disable_unused_qubits: bool = True,
        model: str = "sat",
        solver: Optional[str] = None,
        check: bool = False,
        intermediate_files_path: str = "./intermediate_files",
        timeout: int | float = 1800,
        verbose: int = -1,
) -> MappingResult:
    """
    Perform CNOT (count/depth) optimization on a given quantum circuit using peephole synthesis. The circuit gets sliced
    into CNOT subcircuits which are synthesized individually and put back together.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        metric (str, optional): The optimization metric to use. Options are "cx-depth" (depth of CNOT gates)
            and "cx-count" (number of CNOT gates). Defaults to "cx-depth".
        bound_metric (Optional[str], optional): If specified, the optimization will be bounded by this metric. For
            instance bounding "cx-count" while optimizing for "cx-depth" will return a circuit with the minimal CNOT
            depth while not increasing the CNOT count. Options are "cx-count" and "cx-depth". Defaults to None.
        coupling_graph (Optional[list[tuple[int, int]]], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. The input circuit must be compatible with the graph. Defaults to None.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the optimized circuit.
            Peephole synthesis is not compatible with both allowing output qubit permutation and specifying a coupling graph.
            Defaults to False.
        search_strategy (str, optional): The optimization strategy to use. Basic options are "forward" and "backward".
            Other options are reachability-based strategies: "k-step", "inc", "going-up", "going-down", "binary",
            and "maxsat".
            Defaults to "forward".
        disable_unused_qubits (bool, optional): If True, unused qubits are disabled when synthesizing subcircuits.
            Improves solving time but may result in suboptimal solutions. Defaults to True.
        model (str, optional): The model to use for optimization. Options are "planning", "qbf", and "sat".
            Defaults to "sat".
        solver (Optional[str], optional): The solver to use for optimization. For model="sat" options are "cd"
            (CaDiCal binary), or any PySAT solver with "pysat-[pysat_solver_name]". Defaults to "pysat-cd19" for SAT solving.
            For model="planning" options are "fd-ms" (FastDownward using merge-and-shrink, default), "lama" or "madagascar".
            For model="qbf" the only option is "caqe" which uses the CAQE solver with the Bloqqer preprocessor.
        check (bool, optional): If True, checks equivalence between original and mapped circuit while considering the
            final mapping of qubits. Also checks that the mapped circuit matches the coupling graph if such is provided.
            Defaults to False.
        intermediate_files_path (str, optional): The path in which to place intermediate files.
            Defaults to "./intermediate_files".
        timeout (int | float, optional): The maximum time (in seconds) allowed for the optimization process.
            Defaults to 1800.
        verbose (int, optional): The verbosity level for logging. -1 for silent. Higher values produce
            more detailed output. Defaults to -1.
    Returns:
        MappingResult: The result of the CNOT optimization, including the optimized circuit and final mapping.
    Raises:
        ValueError: If the provided arguments are invalid or incompatible.
    Notes:
        - If "output_qubit_permute" is enabled, zero-cost swaps are removed from the optimized
          circuit. The result will contain the final mapping of the logical qubits.
    """
    if not coupling_graph_check(circuit, coupling_graph):
        raise ValueError(f"The input circuit must be compatible with the provided coupling graph.")

    if coupling_graph is not None and output_qubit_permute:
        raise ValueError(f"Peephole synthesis does not support running with both layout restrictions and qubit permutation (W+R).")

    # Config automatically sets defaults and validates options
    config = CnotSynthesisConfig(
        metric=metric,
        bound_metric=bound_metric,
        output_qubit_permute=output_qubit_permute,
        search_strategy=search_strategy,
        model=model,
        solver=solver,
        intermediate_files_path=intermediate_files_path,
        verbose=verbose,
    )

    slice_hardness, slice_quality = get_slice_hardness_and_slice_quality_functions(config.metric,
                                                                                   config.bound_metric,
                                                                                   config.output_qubit_permute)

    cnot_synthesizer = CnotSynthesizer(config)

    if disable_unused_qubits:
        cnot_synthesizer = UnusedQubitsDisabled(cnot_synthesizer)

    print_org_circuit(circuit, verbose)

    result = peephole_synthesis_general(
        circuit=circuit,
        synthesizer=cnot_synthesizer,
        slicing="cnot",
        slice_hardness=slice_hardness,
        slice_quality=slice_quality,
        timeout=timeout,
        output_qubit_permute=output_qubit_permute,
        coupling_graph=coupling_graph,
        verbose=verbose
    )

    print_optimization_complete(verbose)

    if check:
        check_correctness(circuit, result, coupling_graph, verbose)

    print_result_and_stats(circuit, result, verbose)

    return result


def cnot_rz_synthesis(
        circuit: QuantumCircuit,
        metric: str = "cx-depth",
        bound_metric: Optional[str] = None,
        coupling_graph: Optional[CouplingGraph] = None,
        output_qubit_permute: bool = False,
        search_strategy: str = "forward",
        check: bool = False,
        intermediate_files_path: str = "./intermediate_files",
        timeout: int | float = 1800,
        verbose: int = -1,
) -> MappingResult:
    """
    Perform CNOT (count/depth) optimization on a given quantum circuit with only {CNOT, SWAP, Rz, Z, T,
    S, Tdg, Sdg} gates.

    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        metric (str, optional): The optimization metric to use. Options are "cx-depth" (depth of CNOT gates)
            and "cx-count" (number of CNOT gates). Defaults to "cx-depth".
        bound_metric (Optional[str], optional): If specified, the optimization will be bounded by this metric. For
            instance bounding "cx-count" while optimizing for "cx-depth" will return a circuit with the minimal CNOT
            depth while not increasing the CNOT count. Options are "cx-count" and "cx-depth". Defaults to None.
        coupling_graph (Optional[CouplingGraph], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. The input circuit must be compatible with the graph. Defaults to None.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the output
            circuit. Defaults to False.
        search_strategy (str, optional): The optimization strategy to use. Options are "forward", "backward", "binary", and "maxsat".
            Defaults to "forward".
        check (bool, optional): If True, checks equivalence between original and mapped circuit while considering the
            final mapping of qubits. Also checks that the mapped circuit matches the coupling graph if such is provided.
            Defaults to False.
        intermediate_files_path (str, optional): The path in which to place intermediate files.
            Defaults to "./intermediate_files".
        timeout (int | float, optional): The maximum time (in seconds) allowed for the optimization process.
            Defaults to 1800.
        verbose (int, optional): The verbosity level for logging. -1 for silent. Higher values produce
            more detailed output. Defaults to -1.
    Returns:
        MappingResult: The result of the CNOT optimization, including the optimized circuit and
        final mapping.
    Raises:
        ValueError: If the optimized circuit is not compatible with the given coupling graph.
    Notes:
        - If `output_qubit_permute` is enabled, zero-cost swaps are removed from the optimized
          circuit.
    """
    if not is_cnot_rz_circuit(circuit):
        raise ValueError("The input circuit may only contain CNOT or Rz gates: {CNOT, SWAP, Rz, Z, T, S, Tdg, Sdg}.")

    if not coupling_graph_check(circuit, coupling_graph):
        raise ValueError(f"The input circuit must be compatible with the provided coupling graph.")

    # Automatically sets defaults and validates options
    config = CnotRzSynthesisConfig(
        metric=metric,
        bound_metric=bound_metric,
        output_qubit_permute=output_qubit_permute,
        search_strategy=search_strategy,
        intermediate_files_path=intermediate_files_path,
        verbose=verbose,
    )

    print_org_circuit(circuit, verbose)

    result = CnotRzSynthesizer(config).run(circuit, coupling_graph, timeout)

    print_optimization_complete(verbose)

    # if qubit permute is enabled, we remove zero-cost swaps:
    if output_qubit_permute:
        result = handle_zero_cost_swaps(result, circuit.num_qubits)

    # check equivalence of the original and optimized circuit
    if check:
        check_correctness(circuit, result, coupling_graph, verbose)

    print_result_and_stats(circuit, result, verbose)

    return result


def cnot_rz_peephole_synthesis(
        circuit: QuantumCircuit,
        metric: str = "cx-depth",
        bound_metric: Optional[str] = None,
        coupling_graph: Optional[CouplingGraph] = None,
        output_qubit_permute: bool = False,
        search_strategy: str = "forward",
        disable_unused_qubits: bool = True,
        check: bool = False,
        intermediate_files_path: str = "./intermediate_files",
        timeout: int | float = 1800,
        verbose: int = -1,
) -> MappingResult:
    """
    Perform CNOT+Rz (count/depth) optimization on a given quantum circuit using peephole synthesis. The circuit gets sliced
    into CNOT+Rz subcircuits which are synthesized individually and put back together.

    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        metric (str, optional): The optimization metric to use. Options are "cx-depth" (depth of CNOT gates)
            and "cx-count" (number of CNOT gates). Defaults to "cx-depth".
        bound_metric (Optional[str], optional): If specified, the optimization will be bounded by this metric. For
            instance bounding "cx-count" while optimizing for "cx-depth" will return a circuit with the minimal CNOT
            depth while not increasing the CNOT count. Options are "cx-count" and "cx-depth". Defaults to None.
        coupling_graph (Optional[CouplingGraph], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. The input circuit must be compatible with the graph. Defaults to None.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the output
            circuit. Defaults to False.
        search_strategy (str, optional): The optimization strategy to use. Options are "forward", "backward", "binary", and "maxsat".
            Defaults to "forward".
        disable_unused_qubits (bool, optional): If True, unused qubits are disabled when synthesizing subcircuits.
            Improves solving time but may result in suboptimal solutions. Defaults to True.
        check (bool, optional): If True, checks equivalence between original and mapped circuit while considering the
            final mapping of qubits. Also checks that the mapped circuit matches the coupling graph if such is provided.
            Defaults to False.
        intermediate_files_path (str, optional): The path in which to place intermediate files.
            Defaults to "./intermediate_files".
        timeout (int | float, optional): The maximum time (in seconds) allowed for the optimization process.
            Defaults to 1800.
        verbose (int, optional): The verbosity level for logging. -1 for silent. Higher values produce
            more detailed output. Defaults to -1.
    Returns:
        MappingResult: The result of the CNOT optimization, including the optimized circuit and
        final mapping.
    Raises:
        ValueError: If the optimized circuit is not compatible with the given coupling graph.
    Notes:
        - If `output_qubit_permute` is enabled, zero-cost swaps are removed from the optimized
          circuit.
    """
    if not coupling_graph_check(circuit, coupling_graph):
        raise ValueError(f"The input circuit must be compatible with the provided coupling graph.")

    if coupling_graph is not None and output_qubit_permute:
        raise ValueError(f"Peephole synthesis does not support running with both layout restrictions and qubit permutation (W+R).")

    # Config automatically sets defaults and validates options
    config = CnotRzSynthesisConfig(
        metric=metric,
        bound_metric=bound_metric,
        output_qubit_permute=output_qubit_permute,
        search_strategy=search_strategy,
        intermediate_files_path=intermediate_files_path,
        verbose=verbose,
    )

    slice_hardness, slice_quality = get_slice_hardness_and_slice_quality_functions(config.metric,
                                                                                   config.bound_metric,
                                                                                   config.output_qubit_permute)

    cnot_rz_synthesizer = CnotRzSynthesizer(config)

    if disable_unused_qubits:
        cnot_rz_synthesizer = UnusedQubitsDisabled(cnot_rz_synthesizer)

    print_org_circuit(circuit, verbose)

    result = peephole_synthesis_general(
        circuit=circuit,
        synthesizer=cnot_rz_synthesizer,
        slicing="cnot_rz",
        slice_hardness=slice_hardness,
        slice_quality=slice_quality,
        timeout=timeout,
        output_qubit_permute=output_qubit_permute,
        coupling_graph=coupling_graph,
        verbose=verbose
    )

    print_optimization_complete(verbose)

    if check:
        check_correctness(circuit, result, coupling_graph, verbose)

    print_result_and_stats(circuit, result, verbose)

    return result


def clifford_synthesis(
        circuit: QuantumCircuit,
        metric: str = "cx-depth",
        bound_metric: Optional[str] = None,
        coupling_graph: Optional[CouplingGraph] = None,
        output_qubit_permute: bool = False,
        postprocess_1q_gates: Optional[str] = "greedy",
        gate_ordering: bool = True,
        simple_path_restrictions: bool = False,
        cycle_bound: int = 3,
        search_strategy: str = "forward",
        model: Optional[str] = "sat",
        solver: Optional[str] = None,
        check: bool = False,
        intermediate_files_path: str = "./intermediate_files",
        timeout: int | float = 1800,
        verbose: int = -1,
) -> MappingResult:
    """
    Perform Clifford (cx-count/cx-depth) optimization on a given Clifford quantum circuit.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        metric (str, optional): The optimization metric to use. For SAT, options are "cx-depth" (depth of CNOT gates)
            and "cx-count" (number of CNOT gates). For planning, options are "cx-count" or "cx-count_1q-count" (minimizing
            1-qubit gate count while guaranteeing optimal number of CNOT gates). Defaults to "cx-depth".
        bound_metric (Optional[str], optional): If specified, the optimization will be bounded by this metric. For
            instance bounding "cx-count" while optimizing for "cx-depth" will return a circuit with the minimal CNOT
            depth while not increasing the CNOT count. Options are "cx-count" and "cx-depth". This option requires
            that the model is SAT. Defaults to None.
        coupling_graph (Optional[CouplingGraph], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. Defaults to None.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the output
            circuit. Defaults to False.
        postprocess_1q_gates (Optional[str], optional): Post-processing mode for 1-qubit gates.
            Options are "greedy" (rewrite rules, linear time), "rigid" (planning-based with fixed CNOT
            structure, uses remaining timeout), or None (no post-processing). Defaults to "greedy".
        gate_ordering (bool, optional): If True, parallel gate ordering is fixed. SAT-only. Not compatible
            with 'backward' search strategy. Defaults to True.
        simple_path_restrictions (bool, optional): If True, only simple paths across layers are allowed.
            SAT-only. Defaults to False.
        cycle_bound (int, optional): Number of layers to break cycles with simple path restrictions.
            SAT-only. Defaults to 3.
        search_strategy (str, optional): The optimization strategy to use. SAT-only.
            Options are "forward" and "backward". Defaults to "forward".
        model (str, optional): The optimization model to use, either "sat" or "planning". Defaults to "sat".
        solver (Optional[str], optional): The solver to use. For SAT: any PySAT solver (defaults to "pysat-cd19").
            For planning: a planner name (defaults to "fd-ms"). Defaults to None.
        check (bool, optional): If True, checks equivalence and coupling graph compatibility. Defaults to False.
        intermediate_files_path (str, optional): Path for intermediate files. SAT-only.
            Defaults to "./intermediate_files".
        timeout (int | float, optional): Maximum time (in seconds) for the optimization. Defaults to 1800.
        verbose (int, optional): Verbosity level. -1 for silent. Defaults to -1.
    Returns:
        MappingResult: The result of the Clifford optimization, including the optimized circuit and final mapping.
    Raises:
        ValueError: If the parameters are invalid or incompatible.
        AssertionError: If the equivalence check or coupling graph check fails.
    """
    if not is_clifford_circuit(circuit):
        raise ValueError(f"The input circuit may only contain Clifford gates.")

    if search_strategy=="forward":
        search_strategy = get_search_strategy(circuit, coupling_graph)
        
    config = CliffordSynthesisConfig(
        metric=metric,
        bound_metric=bound_metric,
        output_qubit_permute=output_qubit_permute,
        postprocess_1q_gates=postprocess_1q_gates,
        gate_ordering=gate_ordering,
        simple_path_restrictions=simple_path_restrictions,
        cycle_bound=cycle_bound,
        search_strategy=search_strategy,
        model=model,
        solver=solver,
        intermediate_files_path=intermediate_files_path,
        verbose=verbose
    )

    print_org_circuit(circuit, verbose)

    result = CliffordSynthesizer(config).run(circuit, coupling_graph, timeout)

    print_optimization_complete(verbose)

    # if qubit permute is enabled, we remove zero-cost swaps:
    if output_qubit_permute:
        result = handle_zero_cost_swaps(result, circuit.num_qubits)

    if check:
        check_correctness(circuit, result, coupling_graph, verbose)

    print_result_and_stats(circuit, result, verbose)

    return result


def clifford_peephole_synthesis(
        circuit: QuantumCircuit,
        metric: str = "cx-depth",
        bound_metric: Optional[str] = None,
        coupling_graph: Optional[CouplingGraph] = None,
        output_qubit_permute: bool = False,
        postprocess_1q_gates: Optional[str] = "greedy",
        disable_unused_qubits: bool = True,
        gate_ordering: bool = True,
        simple_path_restrictions: bool = False,
        cycle_bound: int = 3,
        search_strategy: str = "forward",
        model: Optional[str] = "sat",
        solver: Optional[str] = None,
        check: bool = False,
        intermediate_files_path: str = "./intermediate_files",
        timeout: int | float = 1800,
        verbose: int = -1,
) -> MappingResult:
    """
    Perform Clifford (cx-count/cx-depth) optimization on a given Clifford quantum circuit using peephole synthesis.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        metric (str, optional): The optimization metric to use. For SAT, options are "cx-depth" (depth of CNOT gates)
            and "cx-count" (number of CNOT gates). For planning, options are "cx-count" or "cx-count_1q-count" (minimizing
            1-qubit gate count while guaranteeing optimal number of CNOT gates). Defaults to "cx-depth".
        bound_metric (Optional[str], optional): If specified, the optimization will be bounded by this metric. For
            instance bounding "cx-count" while optimizing for "cx-depth" will return a circuit with the minimal CNOT
            depth while not increasing the CNOT count. Options are "cx-count" and "cx-depth". This option requires
            that the model is SAT. Defaults to None.
        coupling_graph (Optional[CouplingGraph], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. Defaults to None.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the output
            circuit. Defaults to False.
        postprocess_1q_gates (Optional[str], optional): Post-processing mode for 1-qubit gates, applied per slice.
            Options are "greedy" (rewrite rules, linear time), "rigid" (planning-based with fixed CNOT
            structure, uses remaining slice timeout), or None (no post-processing). Defaults to "greedy".
        disable_unused_qubits (bool, optional): If True, unused qubits are disabled when synthesizing subcircuits.
            Improves solving time but may result in suboptimal solutions. Defaults to True.
        gate_ordering (bool, optional): If True, parallel gate ordering is fixed. SAT-only. Not compatible
            with 'backward' search strategy. Defaults to True.
        simple_path_restrictions (bool, optional): If True, only simple paths across layers are allowed.
            SAT-only. Defaults to False.
        cycle_bound (int, optional): Number of layers to break cycles with simple path restrictions.
            SAT-only. Defaults to 3.
        search_strategy (str, optional): The optimization strategy to use. SAT-only.
            Options are "forward" and "backward". Defaults to "forward".
        model (str, optional): The optimization model to use, either "sat" or "planning". Defaults to "sat".
        solver (Optional[str], optional): The solver to use. For SAT: any PySAT solver (defaults to "pysat-cd19").
            For planning: a planner name (defaults to "fd-ms"). Defaults to None.
        check (bool, optional): If True, checks equivalence and coupling graph compatibility. Defaults to False.
        intermediate_files_path (str, optional): Path for intermediate files. SAT-only.
            Defaults to "./intermediate_files".
        timeout (int | float, optional): Maximum time (in seconds) for the optimization. Defaults to 1800.
        verbose (int, optional): Verbosity level. -1 for silent. Defaults to -1.
    Returns:
        MappingResult: The result of the Clifford optimization, including the optimized circuit and final mapping.
    Raises:
        ValueError: If the parameters are invalid or incompatible.
        AssertionError: If the equivalence check or coupling graph check fails.
    """
    if not coupling_graph_check(circuit, coupling_graph):
        raise ValueError(f"The input circuit must be compatible with the provided coupling graph.")

    if coupling_graph is not None and output_qubit_permute:
        raise ValueError(f"Peephole synthesis does not support running with both layout restrictions and qubit permutation (W+R).")

    # Config automatically sets defaults and validates options
    config = CliffordSynthesisConfig(
        metric=metric,
        bound_metric=bound_metric,
        output_qubit_permute=output_qubit_permute,
        postprocess_1q_gates=postprocess_1q_gates,
        gate_ordering=gate_ordering,
        simple_path_restrictions=simple_path_restrictions,
        cycle_bound=cycle_bound,
        search_strategy=search_strategy,
        model=model,
        solver=solver,
        intermediate_files_path=intermediate_files_path,
        verbose=verbose
    )

    slice_hardness, slice_quality = get_slice_hardness_and_slice_quality_functions(config.metric,
                                                                                   config.bound_metric,
                                                                                   config.output_qubit_permute)

    clifford_synthesizer = CliffordSynthesizer(config)

    if disable_unused_qubits:
        clifford_synthesizer = UnusedQubitsDisabled(clifford_synthesizer)

    print_org_circuit(circuit, verbose)

    result = peephole_synthesis_general(
        circuit=circuit,
        synthesizer=clifford_synthesizer,
        slicing="clifford",
        slice_hardness=slice_hardness,
        slice_quality=slice_quality,
        timeout=timeout,
        output_qubit_permute=output_qubit_permute,
        coupling_graph=coupling_graph,
        verbose=verbose
    )

    print_optimization_complete(verbose)

    if check:
        check_correctness(circuit, result, coupling_graph, verbose)

    print_result_and_stats(circuit, result, verbose)

    return result


#########################################################################################################
# Helper Functions:
#########################################################################################################


# handle zero-cost swaps and mapping:
def handle_zero_cost_swaps(result, num_qubits):
    """
    Removes zero-cost swaps from the circuit and returns updated result optimized circuit
    along with the final mapping.
    """
    opt_circuit, post_mapping = remove_zero_cost_swaps(result.circuit, num_qubits)
    result.circuit = opt_circuit
    result.final_mapping = post_mapping
    return result


def check_correctness(org_circuit: QuantumCircuit, result: MappingResult, coupling_graph: Optional[CouplingGraph], verbose: int):
    """
    Checks if the org_circuit is equivalent to the result circuit while considering the result's initial and final
    mappings. If a coupling graph is provided, the function checks that the result circuit is compatible with the graph.
    Raises:
        AssertionError: If the equivalence check or coupling graph check fails.
    """
    check_coupling_graph(result.circuit, coupling_graph)
    check_equivalence(org_circuit, result.circuit, result.final_mapping, result.initial_mapping, verbose=verbose)
    if verbose > 0:
        print("Equivalence check and coupling graph check passed.")


# check if the circuit is compatible with the coupling graph:
def check_coupling_graph(circuit, coupling_graph, raise_error=True):
    """
    Checks if the circuit is compatible with the given coupling graph.
    Raises ValueError if not compatible.
    """
    if not coupling_graph_check(circuit, coupling_graph):
        if not raise_error:
            return False
        else:
            raise ValueError(
                """The optimized circuit is not compatible with the coupling graph.
                Likely timeout occurred during optimization and returned original circuit."""
            )
    else:
        return True


# Check equivalence of the original and optimized circuit:
def check_equivalence(
        org_circuit: QuantumCircuit,
        opt_circuit: QuantumCircuit,
        final_mapping: Optional[dict[int,int]] = None,
        initial_mapping: Optional[dict[int,int]] = None,
        verbose: int = 0
):
    """
    Checks if org_circuit is equivalent to opt_circuit while considering the given qubit_mappings from qubits in
    org_circuit to qubits in opt_circuit. If the circuits are Clifford circuits, the equivalence check is done by
    comparing their respective Clifford matrices. Else, the comparison is done using MQT's QCEC.
    Raises:
        AssertionError: if org_circuit is not equivalent to opt_circuit (qubit mappings considered).
    """
    if final_mapping is None:
        final_mapping = {i: i for i in range(org_circuit.num_qubits)}
    if is_clifford_circuit(org_circuit) and is_clifford_circuit(opt_circuit) and initial_mapping is None:
        check_equivalence_of_clifford_circuits(org_circuit, opt_circuit, final_mapping, verbose)
    else:
        check_equivalence_of_arbitrary_circuits(org_circuit, opt_circuit, final_mapping, initial_mapping, verbose)


# function to set main and second metric for optimization:
def set_metrics(metric, verbose):
    # if metric is bounded, we first apply cx-depth and then cx-count minimization:
    if metric == "cx-depth_cx-count":
        main_metric = "cx-depth"
        second_metric = "bounded_cx-depth_local_cx-count"
        if verbose > -1:
            print("First optimizing cx-depth...")
    elif metric == "cx-count_cx-depth":
        main_metric = "cx-count"
        second_metric = "bounded_cx-count_local_cx-depth"
        if verbose > -1:
            print("First optimizing cx-count...")
    else:
        assert metric == "cx-depth" or metric == "cx-count" or metric == "gate-count" or metric == "cx-count_near-optimal", (
            "Metric should be either 'cx-depth', 'cx-count', "
            "'cx-depth_cx-count' or 'cx-count_cx-depth'."
        )
        main_metric = metric
        second_metric = None
        if verbose > -1:
            print(f"Optimizing {main_metric} ...")
    return main_metric, second_metric


def print_org_circuit(circuit, verbose):
    if verbose > 0:
        print("Original circuit:")
        print(circuit)


def print_optimization_complete(verbose):
    if verbose > -1:
        print(f"Optimization complete.")


def print_result_and_stats(org_circuit, result, verbose):
    if verbose > 0:
        print("Optimized circuit:")
        print(result.circuit)
        print("Final mapping:")
        print(result.final_mapping)
    if verbose >= 0:
        print("Change in circuit stats:")
        print_stats(org_circuit, result.circuit)


def get_slice_hardness_and_slice_quality_functions(optimization_metric: str, bound_metric: Optional[str], output_qubit_permute: bool):
    # Set cost functions based on whether permutations are allowed
    cnot_count = compute_cnot_without_swaps_cost if output_qubit_permute else compute_cnot_cost
    cnot_depth = compute_cnot_depth if output_qubit_permute else compute_cnotdepth_swaps_as_3cx

    if bound_metric is not None or optimization_metric == "cx-depth":
        slice_hardness = lambda qc: (len(get_used_qubits(qc)),
                                     cnot_depth(qc),
                                     cnot_count(qc))
    elif optimization_metric in ["cx-count", "cx-count_1q-count"]:
        slice_hardness = lambda qc: (len(get_used_qubits(qc)),
                                     cnot_count(qc),
                                     cnot_depth(qc))
    else:
        raise ValueError(f"Unknown metric: {optimization_metric}")



    if optimization_metric == "cx-count":
        slice_quality = lambda qc: (cnot_count(qc), cnot_depth(qc))
    elif optimization_metric == "cx-depth":
        slice_quality = lambda qc: (cnot_depth(qc), cnot_count(qc))
    elif optimization_metric == "cx-count_1q-count":
        slice_quality = lambda qc: (cnot_count(qc), compute_oneq_gate_count(qc), cnot_depth(qc))
    else:
        raise ValueError(f"Unknown metric: {optimization_metric}")
    return slice_hardness, slice_quality
