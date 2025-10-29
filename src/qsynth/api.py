# Exposing functions only with the relevant options in relevant format for the API.

from .Subarchitectures.subarchitectures import subarchitecture_mapping
from .layout_synthesis_wrapper import layout_synthesis as ls
from .LayoutSynthesis.architecture import platform as pt
from .peephole_synthesis import peephole_synthesis as ps
from .CnotSynthesis.cnot_synthesis_sat_qbf import cnot_optimization
from .CnotSynthesis.cnot_synthesis import coupling_graph_check
from .CliffordSynthesis.clifford_synthesis_sat import clifford_optimization
from qiskit.quantum_info import Clifford
from .PeepholeSlicing.circuit_utils import remove_zero_cost_swaps
from .Utilities.result import MappingResult
import time
from typing import Optional
from qiskit.circuit.quantumcircuit import QuantumCircuit
from qsynth.Utilities.print_utils import print_stats


def get_coupling_graph(
    platform: Optional[str] = None,
    coupling_graph: Optional[list[tuple[int, int]]] = None,
    bidirectional: int = 1,
) -> list[int, int]:
    """
    Return a coupling graph based on the specified platform or a custom coupling graph.
    Parameters:
        platform (Optional[str]): The name of the platform for which the coupling graph is to be retrieved.
                                  If provided, the coupling graph will be extracted for the specified platform.
                                  Defaults to None.
        coupling_graph (Optional[list[int,int]]): A custom coupling graph provided by the user. If specified, the platform
                                         parameter must be None. Defaults to None.
        bidirectional (int, optional): Indicates whether the coupling graph should be bidirectional.
                             Use 1 for bidirectional and 0 for unidirectional. Defaults to 1.

    Returns:
        list[int,int]: The resulting coupling graph, either retrieved based on the platform or constructed from the custom input.

    Raises:
        AssertionError: If both `platform` and `coupling_graph` are provided or if neither is provided.
    """
    # if platform is chosen then coupling graph is extracted:
    if coupling_graph == None and platform != None:
        coupling_graph = pt(
            platform=platform,
            bidirectional=bidirectional,
            coupling_graph=None,
        )[1]
    # if coupling graph is given, we assume it is a custom one:
    elif coupling_graph != None:
        assert (
            platform == None
        ), "If coupling graph is given, platform should not be chosen"
        coupling_graph = pt(
            platform="custom",
            bidirectional=bidirectional,
            coupling_graph=coupling_graph,
        )[1]
    return coupling_graph


# TODO: check input and output circuit equivalence
def layout_synthesis(
    circuit: QuantumCircuit,
    coupling_graph: list[tuple[int, int]],
    metric: str = "cx-count",
    subarchitecture: bool = False,
    parallel_swaps: bool = False,
    num_ancillary_qubits: Optional[int] = None,
    search_strategy: str = "forward",
    swap_upper_bound: Optional[int] = None,
    initial_mapping: Optional[dict[int, int]] = None,
    timeout: int = 1800,
    verbose: int = 0,
) -> MappingResult:
    """
    Layout synthesis for a given quantum circuit and coupling graph.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be synthesized.
        coupling_graph (list[tuple[int, int]]): The coupling graph representing
            the connectivity of the quantum hardware. Defaults to None.
        metric (str, optional): The optimization metric to use. Options are "cx-count", "cx-depth".
            Defaults to "cx-count".
        parallel_swaps (bool): If True, applies parallel swaps optimizing swap makespan. If False, applies sequential swaps optimizing swap count.
            and allows any number of ancillary qubits. If False, allows parallel swaps and disables ancillary qubits.
            Defaults to False.
        subarchitecture (bool, optional): If True, performs subarchitecture mapping. Defaults to False.
        num_ancillary_qubits (int): Specifies the number of ancillary qubits to use, -1 indicates any number of ancillary qubits.
            if subarchitecture mapping is enabled defaults to 0.
            if subarchitecture mapping is disabled, defaults to -1(any number of ancillary qubits).
        search_strategy (str, optional): The search strategy to use, either "forward" or "backward".
            Defaults to "forward".
        swap_upper_bound (Optional[int], optional): The upper bound on the number of swaps for the
            "backward" search strategy. Must be specified if using "backward". Defaults to None.
        initial_mapping (Optional[list[int]], optional): A predefined initial mapping of qubits. If
            provided, direct synthesis mapping is performed, and subarchitecture mapping is disabled.
            Defaults to None.
        timeout (int, optional): The maximum time (in seconds) allowed for the synthesis process.
            Defaults to 1800.
        verbose (int, optional): The verbosity level for logging. Higher values produce more detailed
            output. -1 for silent. Defaults to 0.
    Returns:
        MappingResult: The result of the layout synthesis, including the optimized circuit and final mapping.
    Raises:
        AssertionError: If the "backward" search strategy is selected but `swap_upper_bound` is not
            specified.
        ValueError: If the optimized circuit is not compatible with the given coupling graph.
    Notes:
        - If `coupling_graph` is provided, the function verifies that the optimized circuit is
          compatible with the graph.
        - The `subarchitecture` option is ignored if `initial_mapping` is provided.
        - If `metric` is set to "cx-depth", any provided `initial_mapping` is ignored.
    """
    # if initial mapping is given, we only run direct synthesis mapping:
    if initial_mapping is not None:
        subarchitecture = False
        if verbose > 0:
            print(
                "Warning: Initial mapping is provided, so subarchitecture mapping is disabled."
            )
    if subarchitecture and num_ancillary_qubits == None:
        num_ancillary_qubits = 0
        if verbose >= 0:
            print(
                "Warning: With subarchitectures, num_ancillary_qubits is set to 0 by default."
            )
    # setting parallel swaps depending on optimal synthesis option:
    if num_ancillary_qubits == 0:
        allow_ancillas = False
    else:
        allow_ancillas = True
        if num_ancillary_qubits != None and not subarchitecture:
            subarchitecture = True
            if verbose >= 0:
                print(
                    "Warning: For positive number of ancillary qubits, 'subarchitecture' is enabled."
                )
    if search_strategy == "forward":
        # for forward search strategy, we start with zero. There is no upper bound:
        start = 0
    else:
        assert search_strategy == "backward"
        # for backward search strategy, we need to specify the upper bound:
        assert (
            swap_upper_bound is not None
        ), "Upper bound for backward search must be specified"
        start = swap_upper_bound
    # if metric cx-depth we do not allow custom initial mapping :
    if metric == "cx-depth":
        initial_mapping = None
        if verbose > 0:
            print(
                "Warning: cx-depth metric is chosen, so initial mapping is ignored and set to None."
            )
    if subarchitecture:
        result = subarchitecture_mapping(
            circuit_in=circuit,
            coupling_graph=coupling_graph,
            metric=metric,
            parallel_swaps=parallel_swaps,
            solver_time=timeout,
            verbose=verbose,
            layout_synthesis_method=ls,
            num_ancillary_qubits=num_ancillary_qubits,
        )
    else:
        result = ls(
            circuit_in=circuit,
            coupling_graph=coupling_graph,
            metric=metric,
            parallel_swaps=parallel_swaps,
            solver_time=timeout,
            verbose=verbose,
            allow_ancillas=allow_ancillas,
            initial_mapping=initial_mapping,
            search_strategy=search_strategy,
            start=start,
        )
    # if coupling graph is given, we check if the circuit is compatible with it:
    if coupling_graph is not None and result is not None:
        # check if the optimized circuit is compatible with the coupling graph:
        check_coupling_graph(result.circuit, coupling_graph)
    return result


def cnot_synthesis(
    circuit: QuantumCircuit,
    metric: str = "cx-depth",
    coupling_graph: Optional[list[tuple[int, int]]] = None,
    timeout: int = 1800,
    output_qubit_permute: bool = False,
    verbose: int = 0,
) -> MappingResult:
    """
    Perform CNOT (count/depth) optimization on a given quantum circuit with only CNOT gates.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        metric (str, optional): The optimization metric to use. Options are "cx-depth", "cx-count",
            "cx-depth_cx-count", or "cx-count_cx-depth". Defaults to "cx-depth".
        coupling_graph (Optional[list[tuple[int, int]]], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. Defaults to None.
        timeout (int, optional): The maximum time (in seconds) allowed for the optimization process.
            Defaults to 1800.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the output
            circuit. Defaults to False.
        verbose (int, optional): The verbosity level for logging. -1 for silent. Higher values produce
            more detailed output. Defaults to 0.
    Returns:
        MappingResult: The result of the CNOT optimization, including the optimized circuit and
        final mapping.
    Raises:
        ValueError: If the optimized circuit is not compatible with the given coupling graph.
    Notes:
        - If `coupling_graph` is provided, the function verifies that the optimized circuit is
          compatible with the graph.
        - If `output_qubit_permute` is enabled, zero-cost swaps are removed from the optimized
          circuit.
    """
    if verbose > 0:
        print("Original circuit:")
        print(circuit)
    # set search strategy based on coupling graph:
    search_strategy = get_search_strategy(circuit, coupling_graph)
    # set main and second metric for optimization:
    main_metric, second_metric = set_metrics(metric, verbose)
    result = cnot_optimization(
        circuit=circuit,
        solver="pysat-cd19",
        minimization=main_metric,
        time=timeout,
        coupling_graph=coupling_graph,
        verbose=verbose,
        search_strategy=search_strategy,
        gate_ordering=True,
        qubit_permute=output_qubit_permute,
        check=0,
    )
    # if double optimization metric, we apply second minimization:
    if metric == "cx-depth_cx-count" or metric == "cx-count_cx-depth":
        if metric == "cx-depth_cx-count":
            if verbose > -1:
                print("Optimized cx-depth, now optimizing local cx-count...")
        else:
            if verbose > -1:
                print("Optimized cx-count, now optimizing local cx-depth...")
        result = cnot_optimization(
            circuit=result.circuit,
            solver="pysat-cd19",
            minimization=second_metric,
            time=timeout,
            coupling_graph=coupling_graph,
            verbose=verbose,
            search_strategy=search_strategy,
            gate_ordering=True,
            qubit_permute=output_qubit_permute,
            check=0,
        )
    if verbose > -1:
        print(f"Optimization complete.")
    # check equivalence of the original and optimized circuit before removing zero-cost swaps:
    equivalence_check(circuit, result.circuit, verbose)
    # if qubit permute is enabled, we remove zero-cost swaps:
    if output_qubit_permute:
        result = handle_zero_cost_swaps(result, circuit.num_qubits)
    if coupling_graph is not None:
        # check if the optimized circuit is compatible with the coupling graph:
        check_coupling_graph(result.circuit, coupling_graph)
        if verbose > 0:
            print("Coupling graph check passed.")
    if verbose > 0:
        print("Optimized circuit:")
        print(result.circuit)
        print("Final mapping:")
        print(result.final_mapping)
    if verbose >= 0:
        print("Change in circuit stats:")
        print_stats(circuit, result.circuit)
    return result


def clifford_synthesis(
    circuit: QuantumCircuit,
    metric: str = "cx-depth",
    coupling_graph: Optional[list[tuple[int, int]]] = None,
    timeout: int = 1800,
    output_qubit_permute: bool = False,
    verbose: int = 0,
) -> MappingResult:
    """
    Perform Clifford (cx-count/cx-depth) optimization on a given Clifford quantum circuit.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        metric (str, optional): The optimization metric to use. Options are "cx-depth", "cx-count",
            "cx-depth_cx-count", or "cx-count_cx-depth". Defaults to "cx-depth".
        coupling_graph (list[tuple[int, int]], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. Defaults to None.
        timeout (int, optional): The maximum time (in seconds) allowed for the optimization process.
            Defaults to 1800.
        output_qubit_permute (bool, optional): If True, allows final qubit permutation in the output
            circuit. Defaults to False.
        verbose (int, optional): The verbosity level for logging. -1 for silent. Higher values produce
            more detailed output. Defaults to 0.
    Returns:
        MappingResult: The result of the Clifford optimization, including the optimized circuit and
        final mapping.
    Raises:
        ValueError: If the optimized circuit is not compatible with the given coupling graph.
    Notes:
        - If `coupling_graph` is provided, the function verifies that the optimized circuit is
          compatible with the graph.
        - If `output_qubit_permute` is enabled, zero-cost swaps are removed from the optimized
          circuit.
    """
    if verbose > 0:
        print("Original circuit:")
        print(circuit)
    # set search strategy based on coupling graph:
    search_strategy = get_search_strategy(circuit, coupling_graph)
    # set main and second metric for optimization:
    main_metric, second_metric = set_metrics(metric, verbose)
    result = clifford_optimization(
        circuit=circuit,
        solver="pysat-cd19",
        minimization=main_metric,
        time=timeout,
        coupling_graph=coupling_graph,
        verbose=verbose,
        search_strategy=search_strategy,
        gate_ordering=True,
        qubit_permute=output_qubit_permute,
        check=0,
    )
    # if double optimization metric, we apply second minimization:
    if metric == "cx-depth_cx-count" or metric == "cx-count_cx-depth":
        if metric == "cx-depth_cx-count":
            if verbose > -1:
                print("Optimized cx-depth, now optimizing local cx-count...")
        else:
            if verbose > -1:
                print("Optimized cx-count, now optimizing local cx-depth...")
        result = clifford_optimization(
            circuit=result.circuit,
            solver="pysat-cd19",
            minimization=second_metric,
            time=timeout,
            coupling_graph=coupling_graph,
            verbose=verbose,
            search_strategy=search_strategy,
            gate_ordering=True,
            qubit_permute=output_qubit_permute,
            check=0,
        )
    if verbose > -1:
        print(f"Optimization complete.")
    # check equivalence of the original and optimized circuit before removing zero-cost swaps:
    equivalence_check(circuit, result.circuit, verbose)
    # if qubit permute is enabled, we remove zero-cost swaps:
    if output_qubit_permute:
        result = handle_zero_cost_swaps(result, circuit.num_qubits)
    if coupling_graph is not None:
        # check if the optimized circuit is compatible with the coupling graph:
        check_coupling_graph(result.circuit, coupling_graph)
        if verbose > 0:
            print("Coupling graph check passed.")
    if verbose > 0:
        print("Optimized circuit:")
        print(result.circuit)
        print("Final mapping:")
        print(result.final_mapping)
    if verbose >= 0:
        print("Change in circuit stats:")
        print_stats(circuit, result.circuit)
    return result


def peephole_synthesis(
    circuit: QuantumCircuit,
    coupling_graph: Optional[list[tuple[int, int]]] = None,
    slicing: str = "clifford",
    metric: str = "cx-depth",
    timeout: int = 1800,
    verbose: int = 0,
) -> MappingResult:
    """
    Perform peephole synthesis optimization on a given quantum circuit.
    Args:
        circuit (QuantumCircuit): The input quantum circuit to be optimized.
        coupling_graph (list[tuple[int, int]], optional): The coupling graph representing
            the connectivity of the quantum hardware. If provided, the optimized circuit will be
            compatible with this graph. Defaults to None.
        slicing (str, optional): The slicing method to use, either "clifford" or "cnot".
            Defaults to "clifford".
        metric (str, optional): The optimization metric to use. Options are "cx-depth", "cx-count",
            "cx-depth_cx-count", or "cx-count_cx-depth". Defaults to "cx-depth".
        timeout (int, optional): The maximum time (in seconds) allowed for the optimization process.
            Defaults to 1800.
        verbose (int, optional): The verbosity level for logging. -1 for silent. Higher values produce
            more detailed output. Defaults to 0.
    Returns:
        MappingResult: The result of the peephole synthesis optimization, including the optimized
        circuit and final mapping.
    Raises:
        ValueError: If the optimized circuit is not compatible with the given coupling graph.
    Notes:
        - If `coupling_graph` is provided, the function verifies that the optimized circuit is
          compatible with the graph.
        - The optimization is performed in two stages if a combined metric is specified:
          first optimizing the main metric, followed by local optimization of the secondary metric.
    """
    assert (
        slicing == "clifford" or slicing == "cnot"
    ), "Slicing should be either 'clifford' or 'cnot'."
    if verbose > 0:
        print("Original circuit:")
        print(circuit)

    # set main and second metric for optimization:
    main_metric, second_metric = set_metrics(metric, verbose)
    if verbose > -1:
        print(f"First optimizing {main_metric} for {slicing} slices...")

    start_time = time.perf_counter()
    result = ps(
        circuit_in=circuit,
        slicing=slicing,
        minimize=main_metric,
        model="sat",
        qubit_permute=False,
        search_strategy="forward",
        gate_ordering=True,
        disable_unused=True,
        solver="pysat-cd19",
        time=timeout,
        platform=None,
        verbose=verbose,
        coupling_graph=coupling_graph,
        check=1,
    )
    main_metric_time = time.perf_counter() - start_time

    remaining_time = timeout - main_metric_time

    # if double optimization metric, we apply second minimization:
    if metric == "cx-depth_cx-count" or metric == "cx-count_cx-depth":
        if metric == "cx-depth_cx-count":
            if verbose > -1:
                print("Optimized cx-depth, now optimizing local cx-count...")
        else:
            if verbose > -1:
                print("Optimized cx-count, now optimizing local cx-depth...")
        result = ps(
            circuit_in=result.circuit,
            slicing=slicing,
            minimize=second_metric,
            model="sat",
            qubit_permute=False,
            search_strategy="forward",
            gate_ordering=True,
            disable_unused=True,
            solver="pysat-cd19",
            time=remaining_time,
            platform=None,
            verbose=verbose,
            coupling_graph=coupling_graph,
            check=1,
        )

    if coupling_graph is not None:
        # check if the optimized circuit is compatible with the coupling graph:
        check_coupling_graph(result.circuit, coupling_graph)
        if verbose > 0:
            print("Coupling graph check passed.")
    if verbose > -1:
        print(f"Optimization complete.")
    if verbose > 0:
        print("Optimized circuit:")
        print(result.circuit)
        print("Final mapping:")
        print(result.final_mapping)
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
def equivalence_check(org_circuit, opt_circuit, verbose):
    org_clifford_matrix = Clifford(org_circuit)
    opt_circuit_clifford = Clifford(opt_circuit)
    assert org_clifford_matrix == opt_circuit_clifford
    if verbose > 0:
        print("Optimized circuit is equivalent to the original circuit")


# Search strategy based on coupling graph:
def get_search_strategy(circuit, coupling_graph):
    """
    Determines the search strategy based on the coupling graph.
    If coupling graph is None, we use 'forward' search strategy.
    If coupling graph is provided, we use 'unbounded-forward' search strategy.
    """
    if coupling_graph is not None and not check_coupling_graph(
        circuit, coupling_graph, raise_error=False
    ):
        search_strategy = "unbounded-forward"
    else:
        search_strategy = "forward"
    return search_strategy


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
        assert metric == "cx-depth" or metric == "cx-count", (
            "Metric should be either 'cx-depth', 'cx-count', "
            "'cx-depth_cx-count' or 'cx-count_cx-depth'."
        )
        main_metric = metric
        second_metric = None
        if verbose > -1:
            print(f"Optimizing {main_metric} ...")
    return main_metric, second_metric
