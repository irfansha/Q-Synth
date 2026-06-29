# Irfansha Shaik, Aarhus, 12 July 2023.
# Optimize a circuit by Peephole Optimization with cnot synthesis:
# - input: an input circuit
# - output: optimized circuit with cnot slices optimized (reduced CNOT count)
# - different methods as options to optimize the cnot slices
from collections.abc import Callable
from typing import Optional

from qiskit import QuantumCircuit
from qsynth.PeepholeSlicing.circuit_utils import CircuitUtils as cu
from qsynth.PeepholeSlicing.circuit_utils import (
    remove_zero_cost_swaps,
    project_circuit,
    project_coupling_graph,
)
from qsynth.CnotSynthesis.cnot_synthesis import cnot_optimization as cnot_op
from qsynth.CnotSynthesis.cnot_synthesis_sat_qbf import (
    cnot_optimization as cnot_op_sat_qbf,
)
from qsynth.CliffordSynthesis.clifford_synthesis_planning import (
    clifford_optimization as clifford_opt_planning,
)
from qsynth.CliffordSynthesis.clifford_synthesis_sat import (
    clifford_optimization as clifford_opt_sat,
)
from qsynth.CliffordSynthesis.circuit_utils import (
    compare,
    compute_cnot_cost,
    compute_cnot_without_swaps_cost,
    compute_cnot_depth,
    compute_cnotdepth_swaps_as_3cx,
    compute_oneq_gate_count,
)
from qsynth.LayoutSynthesis.architecture import platform as pt
from qsynth.CnotSynthesis.options import Options as op
from qsynth.CnotSynthesis.cnot_synthesis import coupling_graph_check
from qsynth.Synthesizers.synthesizer import Synthesizer
from qsynth.ReachabilitySolver.encodings.cnot_rz_synthesis.cnot_rz_synthesis_reachability import \
    optimize_cnot_rz_circuit_with_reachability_encoding
from qsynth.Utilities.coupling_graph import CouplingGraph
from qsynth.Utilities.print_utils import print_stats
from qsynth.Utilities.result import MappingResult

from pathlib import Path
import os
import time as clock


def set_single_slice_timelimit(
        remaining_time: float, remaining_slices: int, minimum_slice_time: float = 2.0
) -> float:
    # we divide the remaining time with #slices to get per slice time:
    current_slice_time = remaining_time / (remaining_slices)
    # if we have enough time then we give atleast minimum slice-time per slice:
    if remaining_time > minimum_slice_time and current_slice_time < minimum_slice_time:
        current_slice_time = minimum_slice_time
    return current_slice_time


def optimize_single_slice(args, slice, coupling_graph, current_slice_time):
    # by default we assume a instance is not timedout:
    timed_out = False
    # if unused qubits are disabled, then we generate a projected slice:
    if args.disable_unused:
        cur_optimization_slice = project_circuit(
            slice.optimization_slice, slice.projection_map, len(slice.projection_map)
        )
    else:
        cur_optimization_slice = slice.optimization_slice
    if coupling_graph != None and args.disable_unused:
        cur_coupling_graph = project_coupling_graph(
            coupling_graph, slice.projection_map
        )
    else:
        cur_coupling_graph = coupling_graph
    if args.slicing == "cnot":
        if args.planner != None:
            result = cnot_op(
                cur_optimization_slice,
                planner=args.planner,
                time=current_slice_time,
                minimization=args.minimize,
                verbose=args.verbose,
                coupling_graph=cur_coupling_graph,
            )
        elif args.qbf_solver != None or args.sat_solver != None:
            if args.qbf_solver != None:
                solver = args.qbf_solver
            else:
                assert args.sat_solver != None
                solver = args.sat_solver
            result = cnot_op_sat_qbf(
                cur_optimization_slice,
                solver=solver,
                preprocessor="bloqqer",
                time=current_slice_time,
                minimization=args.minimize,
                verbose=args.verbose,
                coupling_graph=cur_coupling_graph,
                search_strategy=args.search_strategy,
                qubit_permute=args.qubit_permute,
                intermediate_files_path=args.intermediate_files_path,
                check=args.check,
                report_timeout=True,
            )
        else:
            print("Choose either a planner, a qbf solver or a sat solver")
            exit(-1)
    elif args.slicing == "cnot_rz":
        assert args.sat_solver != None, "CNOT+Rz synthesis is only available with SAT"
        result = optimize_cnot_rz_circuit_with_reachability_encoding(
            cur_optimization_slice,
            qubit_permutation=args.qubit_permute,
            coupling_graph=cur_coupling_graph,
            metric=args.minimize,
            strategy=args.search_strategy,
            check=args.check,
            timeout=current_slice_time,
            intermediate_files_path=args.intermediate_files_path
        )
    else:
        assert args.slicing == "clifford"
        if args.platform != None:
            # we might need to handle if bidirectional is 2 (via H-CNOT-H):
            assert (
                    args.bidirectional == 1
            ), "we assume every platform is bidirectional for clifford synthesis"

        if args.planner != None:
            # set default encoding:
            if args.encoding == None:
                args.encoding = "gate_optimal"
            result = clifford_opt_planning(
                circuit=cur_optimization_slice,
                planner=args.planner,
                encoding=args.encoding,
                time=current_slice_time,
                # cnot_minimization=args.minimize, TODO: needs to be handled in planning: for now encoding already specifies the optimization criteria
                verbose=args.verbose,
                coupling_graph=cur_coupling_graph,
                check=args.check,
            )
        else:
            # set default encoding:
            if args.encoding == None:
                args.encoding = "simpleaux"
            result = clifford_opt_sat(
                circuit=cur_optimization_slice,
                encoding=args.encoding,
                solver=args.sat_solver,
                nthreads=args.nthreads,
                time=current_slice_time,
                minimization=args.minimize,
                verbose=args.verbose,
                platform=args.platform,
                coupling_graph=cur_coupling_graph,
                gate_ordering=args.gate_ordering,
                search_strategy=args.search_strategy,
                simple_path_restrictions=args.simple_path_restrictions,
                cycle_bound=args.cycle_bound,
                qubit_permute=args.qubit_permute,
                intermediate_files_path=args.intermediate_files_path,
                check=args.check,
            )
    return result.circuit, result.timed_out


def replace_optimized_slice(args, slice, cur_opt_circuit, num_qubits):
    # set right cost functions based on permutation enabling chosen:
    if args.qubit_permute:
        cnot_cost = compute_cnot_without_swaps_cost
        cnot_depth = compute_cnot_depth
    else:
        cnot_cost = compute_cnot_cost
        cnot_depth = compute_cnotdepth_swaps_as_3cx
    # We assume that the original circuit is already mapped
    # if new optimal circuit is found, we update the existing slice:
    if cur_opt_circuit != None:
        # if qubits disabled eariler, we revert the projection:
        if args.disable_unused:
            cur_opt_circuit = project_circuit(
                cur_opt_circuit, slice.reverse_projection_map, num_qubits
            )
        if args.verbose > 0:
            print_stats(slice.optimization_slice, cur_opt_circuit)
        if args.minimize == "cx-depth" or args.minimize == "bounded_cx-count_local_cx-depth":
            # priority: cx-depth first, then cx-count, then 1q-gate count:
            if compare(slice.optimization_slice, cur_opt_circuit,
                       [cnot_depth, cnot_cost, compute_oneq_gate_count]) == 1:
                slice.optimization_slice = cur_opt_circuit
        elif args.minimize == "cx-count" or args.minimize == "bounded_cx-depth_local_cx-count":
            # priority: cx-count first, then cx-depth, then 1q-gate count:
            if compare(slice.optimization_slice, cur_opt_circuit,
                       [cnot_cost, cnot_depth, compute_oneq_gate_count]) == 1:
                slice.optimization_slice = cur_opt_circuit
        else:
            assert args.minimize == "gate-count"
            # priority: total gate count first, then cx-count, then cx-depth:
            if compare(slice.optimization_slice, cur_opt_circuit, [lambda qc: qc.size(), cnot_cost, cnot_depth]) == 1:
                slice.optimization_slice = cur_opt_circuit
    else:
        # nothing improved:
        if args.verbose > 0:
            print_stats(slice.optimization_slice, slice.optimization_slice)


def peephole_synthesis(
        circuit_in=None,
        encoding="simpleaux",
        slicing="cnot",
        minimize="cx-count",
        model="sat",
        qubit_permute=None,
        gate_ordering=None,
        simple_path_restrictions=None,
        cycle_bound=3,
        disable_unused=True,
        search_strategy="forward",
        solver=None,
        nthreads=1,
        time=600,
        platform=None,
        bidirectional=1,
        intermediate_files_path="./intermediate_files",
        verbose=0,
        check=0,
        coupling_graph=None,
) -> MappingResult:
    # TODO: add descriptions of arguments:
    # --------------------------------------- Creating args separately ---------------------------------------
    args = op()
    args.circuit_in = circuit_in
    args.encoding = encoding
    args.slicing = slicing
    args.verbose = verbose
    args.minimize = minimize
    args.intermediate_files_path = intermediate_files_path
    args.model = model
    args.solver = solver
    args.nthreads = nthreads
    args.qubit_permute = qubit_permute
    args.gate_ordering = gate_ordering
    args.simple_path_restrictions = simple_path_restrictions
    args.cycle_bound = cycle_bound
    args.disable_unused = disable_unused
    args.search_strategy = search_strategy
    # initialize remaining time with all the time allocated:
    args.remaining_time = time
    args.platform = platform
    args.bidirectional = bidirectional
    args.check = check
    # ----------------------------------------------------------------------------------------------------
    # find Benchmarks and Domains,
    peephole_cnotsynthesis_path = os.path.abspath(__file__)
    QSynth_path = Path(peephole_cnotsynthesis_path).parent.parent
    args.benchmarks = os.path.join(QSynth_path, "Benchmarks")

    # if platform is chosen then coupling graph is extracted:
    if coupling_graph == None and args.platform != None:
        coupling_graph = pt(
            platform=args.platform,
            bidirectional=args.bidirectional,
            coupling_graph=None,
        )[1]
    # if coupling graph is given, we assume it is a custom one:
    elif coupling_graph != None:
        assert (
                args.platform == None
        ), "If coupling graph is given, platform should not be chosen"
        coupling_graph = pt(
            platform="custom",
            bidirectional=args.bidirectional,
            coupling_graph=coupling_graph,
        )[1]

    # TODO: avoid different solvers for different solving techniques
    # setting default options for specific solvers:
    args.planner = None
    args.qbf_solver = None
    args.sat_solver = None

    # Setting default solver for chosen solving model:
    if args.model == "planning":
        if args.solver == None:
            args.planner = "fd-ms"
        else:
            assert args.solver in ["fd-ms", "lama", "madagascar"]
            args.planner = args.solver
    elif args.model == "qbf":
        assert (
                args.slicing == "cnot"
        ), "clifford synthesis only available with sat encoding, please use a sat solver"
        if args.solver == None:
            args.qbf_solver = "caqe"
        else:
            assert args.solver == "caqe"
            args.qbf_solver = args.solver
    elif args.model == "sat":
        if args.solver == None:
            args.sat_solver = "pysat-cd"
        else:
            args.sat_solver = args.solver
    else:
        print(
            f"--model, -m: should be 'planning', 'sat', or 'qbf'. Found: '{args.model}'"
        )
        exit(-1)
    # if qubit permutation is chosen, we assume it is only for sat:
    if args.qubit_permute:
        assert (
                args.sat_solver != None
        ), "qubit permutation only available with sat encoding, please use a sat solver or turnoff the permutation option"

    start_time = clock.perf_counter()
    circuit = args.circuit_in
    num_qubits = len(circuit.qubits)
    if args.verbose > 1:
        print("\nOriginal Circuit:")
        print(circuit)

    if not coupling_graph_check(circuit, coupling_graph):
        print("Circuit CNOT gates don't satisfy the coupling graph restrictions")
        print("(Hint: use 'q-synth layout' first)")
        exit(-1)

    # Copy of original circuit:
    circuit_copy = circuit.copy()
    # slicing for CNOT/Clifford synthesis:
    sliced_circuit = cu(circuit_copy, args.slicing)

    total_slices = len(sliced_circuit.slices)
    if args.platform != None:
        if args.slicing == "clifford":
            assert (
                    args.qubit_permute == False
            ), "For now, we do not allow qubit permutation with layout aware (W+R) in clifford synthesis"
        else:
            assert args.slicing in ["cnot", "cnot_rz"]
            if args.qubit_permute:
                assert (
                        total_slices == 1
                ), "We only handle W+R if the circuit has a single slice"

    # set right cost functions based on permutation enabling chosen:
    if args.qubit_permute:
        cnot_cost = compute_cnot_without_swaps_cost
        cnot_depth = compute_cnot_depth
    else:
        cnot_cost = compute_cnot_cost
        cnot_depth = compute_cnotdepth_swaps_as_3cx

    # Sorting slices to prioritize easy slices first,
    # first with less used qubits and then with cnot count or depth according to the minimization criteria:
    slices_order = list(range(len(sliced_circuit.slices)))
    if (
            args.minimize == "cx-depth"
            or args.minimize == "bounded_cx-depth_local_cx-count"
            or args.minimize == "bounded_cx-count_local_cx-depth"
    ):
        # for local CNOT count optimization, the hardness is still determined by the scene or depth of the slice:
        # we prioritize depth before cnot count:
        sorted_slices_order = sorted(
            slices_order,
            key=lambda k: (
                -len(sliced_circuit.slices[k].unused_qubits_optimization_slice),
                cnot_depth(sliced_circuit.slices[k].optimization_slice),
                cnot_cost(sliced_circuit.slices[k].optimization_slice),
            ),
        )
    else:
        assert args.minimize == "cx-count" or args.minimize == "gate-count"
        # we prioritize count before cnot depth:
        sorted_slices_order = sorted(
            slices_order,
            key=lambda k: (
                -len(sliced_circuit.slices[k].unused_qubits_optimization_slice),
                cnot_cost(sliced_circuit.slices[k].optimization_slice),
                cnot_depth(sliced_circuit.slices[k].optimization_slice),
            ),
        )
    # print(sorted_slices_order)

    current_slice_count = 0
    timed_out_slices = []
    for slice_id in sorted_slices_order:
        current_slice_time = set_single_slice_timelimit(
            remaining_time=args.remaining_time,
            remaining_slices=(total_slices - current_slice_count),
        )
        if args.remaining_time < 0.001:
            print("Timed out, remaining time less than 0.001s")
            break
        current_slice_count = current_slice_count + 1
        slice = sliced_circuit.slices[slice_id]
        # print("\n",slice.non_optimization_slice)
        max_num_characters_in_slice_number = len(str(total_slices))
        if args.verbose >= 0:
            print(
                f"({str(current_slice_count).rjust(max_num_characters_in_slice_number)}/{total_slices}) solving slice {str(slice_id + 1).rjust(max_num_characters_in_slice_number)} with {round(current_slice_time, 2)}s timelimit"
            )
            # print(slice.optimization_slice)
        # optimize and add the optimization slice:
        num_cx_gates = cnot_cost(slice.optimization_slice)
        cx_depth = cnot_depth(slice.optimization_slice)
        # We only optimize a circuit if it has more than 0 cx-count:
        if args.minimize == "cx-count" and num_cx_gates <= 1:
            cur_opt_circuit = None
        elif args.minimize == "cx-depth" and cx_depth <= 1:
            cur_opt_circuit = None
        else:
            start_run_time = clock.perf_counter()
            cur_opt_circuit, timed_out = optimize_single_slice(
                args=args,
                slice=slice,
                coupling_graph=coupling_graph,
                current_slice_time=current_slice_time,
            )
            if timed_out:
                timed_out_slices.append(slice_id)
            solving_time = clock.perf_counter() - start_run_time
            args.remaining_time = args.remaining_time - solving_time
        replace_optimized_slice(
            args=args,
            slice=slice,
            cur_opt_circuit=cur_opt_circuit,
            num_qubits=num_qubits,
        )

    timed_out = False
    number_of_timedout_slices = len(timed_out_slices)
    if number_of_timedout_slices > 0:
        if args.verbose >= 0:
            print(
                f"Running {number_of_timedout_slices} timed-out slices with remaining time"
            )
        current_slice_count = 0
        for timed_out_slice_id in timed_out_slices:
            if args.remaining_time < 0.001:
                timed_out = True
                if args.verbose >= 0:
                    print("Timed out, remaining time less than 0.001s")
                break
            current_slice_count = current_slice_count + 1
            # number of spaces needed for printing the slice number:
            num_spaces = len(str(number_of_timedout_slices))
            if args.verbose >= 0:
                print(
                    f"({str(current_slice_count).rjust(num_spaces)}/{number_of_timedout_slices}) solving timedout slice {str(timed_out_slice_id + 1).rjust(num_spaces)} with {round(args.remaining_time, 2)}s timelimit"
                )
            slice = sliced_circuit.slices[timed_out_slice_id]
            start_run_time = clock.perf_counter()
            cur_opt_circuit, _ = optimize_single_slice(
                args=args,
                slice=slice,
                coupling_graph=coupling_graph,
                current_slice_time=args.remaining_time,
            )
            solving_time = clock.perf_counter() - start_run_time
            args.remaining_time = args.remaining_time - solving_time
            replace_optimized_slice(
                args=args,
                slice=slice,
                cur_opt_circuit=cur_opt_circuit,
                num_qubits=num_qubits,
            )

    # composing optimal circuit with optimized circuits:
    opt_circuit = QuantumCircuit(num_qubits)
    for slice in sliced_circuit.slices:
        opt_circuit = opt_circuit.compose(slice.non_optimization_slice)
        opt_circuit = opt_circuit.compose(slice.optimization_slice)

    if args.qubit_permute:
        # we remove zero-cost swaps, mapping can change with swap removal:
        opt_circuit, post_mapping = remove_zero_cost_swaps(opt_circuit, num_qubits)
        result = MappingResult(
            circuit=opt_circuit,
            final_mapping=post_mapping,
            timed_out=timed_out,
        )
        if args.verbose > 1:
            print("\nOptimized Circuit:")
            print(opt_circuit)
            print(
                "\nQubit permutation dictionary to be applied on original measurements:"
            )
            print(post_mapping)
    else:
        result = MappingResult(circuit=opt_circuit, timed_out=timed_out)
        if args.verbose > 1:
            print("\nOptimized Circuit:")
            print(opt_circuit)

    total_time = clock.perf_counter() - start_time
    if args.verbose >= 0:
        print(f"Time taken: {total_time}")
        print("Full circuit stats:")
        print_stats(circuit, result.circuit)

    return result


def peephole_synthesis_general(
        circuit: QuantumCircuit,
        synthesizer: Synthesizer,
        slicing: str,
        slice_hardness: Callable[[QuantumCircuit], tuple],
        slice_quality: Callable[[QuantumCircuit], tuple],
        timeout: int,
        output_qubit_permute: bool,
        coupling_graph: Optional[CouplingGraph],
        verbose: int = -1,
) -> MappingResult:
    """
    Slices the circuit into subcircuits according to the "slicing" argument, and optimizes each subcircuit with the
    provided synthesizer function. Assumes that slices can be synthesized independently, so synthesis that both allows
    output qubit permutation and coupling graph restrictions (W+R) is not supported.
    Args:
        circuit (QuantumCircuit): The quantum circuit to synthesize.
        synthesizer: A Synthesizer object used to synthesize each subcircuit.
        slicing: Decides what gate set to slice the circuit for. Options are "cnot", "cnot_rz", and "clifford".
        slice_hardness: A cost function used to determine the order in which to solve the slices (low to high).
        slice_quality: A cost function used to determine if an optimized slice is better than the original slice
            (lower is better).
        timeout: The total timeout for the peephole synthesis.
        output_qubit_permute:
        coupling_graph (Optional[CouplingGraph]): The (optional) coupling graph on which to synthesize the quantum circuit.
        verbose (int, optional): The verbosity level for logging. Higher values produce more detailed
            output. Options are -1 to 3 (included). Defaults to -1 (silent).
    Returns:
        MappingResult containing the optimized circuit, initial and final mappings, and booleans indicating whether
        the synthesis succeeded, timed out or failed.
    """
    start_time = clock.perf_counter()
    if verbose > 1:
        print("\nOriginal Circuit:")
        print(circuit)

    circuit_copy = circuit.copy()
    sliced_circuit = cu(circuit_copy, slicing)

    total_slices = len(sliced_circuit.slices)

    # Sorting slices to prioritize easy slices first,
    slices_order = list(range(len(sliced_circuit.slices)))
    sorted_slices_order = sorted(
        slices_order,
        key=lambda k: slice_hardness(sliced_circuit.slices[k].optimization_slice)
    )

    remaining_time = timeout
    current_slice_count = 0
    timed_out_slices = []
    for slice_id in sorted_slices_order:
        current_slice_time = set_single_slice_timelimit(
            remaining_time=remaining_time,
            remaining_slices=(total_slices - current_slice_count),
        )
        if remaining_time < 0.001:
            print("Timed out, remaining time less than 0.001s")
            break
        current_slice_count += 1
        slice = sliced_circuit.slices[slice_id]
        max_num_characters_in_slice_number = len(str(total_slices))
        if verbose >= 0:
            print(
                f"({str(current_slice_count).rjust(max_num_characters_in_slice_number)}/{total_slices}) solving slice {str(slice_id + 1).rjust(max_num_characters_in_slice_number)} with {round(current_slice_time, 2)}s timelimit"
            )

        # Skip if slice is empty
        if len(slice.optimization_slice.data) == 0:
            continue
        # Run synthesis
        start_run_time = clock.perf_counter()

        result = synthesizer.run(slice.optimization_slice, coupling_graph, current_slice_time)

        if result.timed_out:
            timed_out_slices.append(slice_id)

        solving_time = clock.perf_counter() - start_run_time
        remaining_time = remaining_time - solving_time

        # Replace slice if optimized is better
        if slice_quality(result.circuit) < slice_quality(slice.optimization_slice):
            slice.optimization_slice = result.circuit

    timed_out = False
    number_of_timedout_slices = len(timed_out_slices)
    if number_of_timedout_slices > 0 and verbose >= 0:
        print(
            f"Running {number_of_timedout_slices} timed-out slices with remaining time"
        )
    current_slice_count = 0
    for timed_out_slice_id in timed_out_slices:
        if remaining_time < 0.001:
            timed_out = True
            if verbose >= 0:
                print("Timed out, remaining time less than 0.001s")
            break
        current_slice_count += 1
        # number of spaces needed for printing the slice number:
        num_spaces = len(str(number_of_timedout_slices))
        if verbose >= 0:
            print(
                f"({str(current_slice_count).rjust(num_spaces)}/{number_of_timedout_slices}) solving timedout slice {str(timed_out_slice_id + 1).rjust(num_spaces)} with {round(remaining_time, 2)}s timelimit"
            )
        slice = sliced_circuit.slices[timed_out_slice_id]

        # Run synthesis
        start_run_time = clock.perf_counter()

        result = synthesizer.run(slice.optimization_slice, coupling_graph, remaining_time)

        if result.timed_out:
            timed_out_slices.append(timed_out_slice_id)

        solving_time = clock.perf_counter() - start_run_time
        remaining_time = remaining_time - solving_time

        # Replace slice if optimized is better
        if slice_quality(result.circuit) < slice_quality(slice.optimization_slice):
            slice.optimization_slice = result.circuit

    # Composing optimized circuit from slices:
    opt_circuit = QuantumCircuit(circuit.num_qubits)
    for slice in sliced_circuit.slices:
        opt_circuit.compose(slice.non_optimization_slice, inplace=True)
        opt_circuit.compose(slice.optimization_slice, inplace=True)

    if output_qubit_permute:
        # we remove zero-cost swaps, mapping can change with swap removal:
        opt_circuit, post_mapping = remove_zero_cost_swaps(opt_circuit, circuit.num_qubits)
        result = MappingResult(
            circuit=opt_circuit,
            final_mapping=post_mapping,
            timed_out=timed_out,
        )
        #if verbose > 1:
        #    print("\nOptimized Circuit:")
        #    print(opt_circuit)
        #    print(
        #        "\nQubit permutation dictionary to be applied on original measurements:"
        #    )
        #    print(post_mapping)
    else:
        result = MappingResult(circuit=opt_circuit, timed_out=timed_out)
        #if verbose > 1:
        #    print("\nOptimized Circuit:")
        #    print(opt_circuit)

    total_time = clock.perf_counter() - start_time
    if verbose >= 0:
        print(f"Time taken: {total_time:.2f}")
        #print("Full circuit stats:")
        #print_stats(circuit, result.circuit)

    return result


def peephole_synthesis_1q_rewrite(circuit: QuantumCircuit, use_cz_gate: bool = False) -> MappingResult:
    from qsynth.CliffordSynthesis.clifford_1q_resynthesis import (
        clifford_1q_optimization_greedy,
    )
    # Copy of original circuit:
    circuit_copy = circuit.copy()
    # slicing for CNOT/Clifford synthesis:
    sliced_circuit = cu(circuit=circuit_copy, slice_type="clifford")
    for slice in sliced_circuit.slices:
        optimized_slice = clifford_1q_optimization_greedy(
            slice.optimization_slice, use_cz_gate=use_cz_gate
        )
        slice.optimization_slice = optimized_slice

    # composing optimal circuit with optimized circuits:
    opt_circuit = QuantumCircuit(len(circuit_copy.qubits))
    for slice in sliced_circuit.slices:
        opt_circuit = opt_circuit.compose(slice.non_optimization_slice)
        opt_circuit = opt_circuit.compose(slice.optimization_slice)
    # We do not have initial permutation, So one-to-one mapping is applied:
    initial_mapping = {i: i for i in range(len(circuit_copy.qubits))}
    # We do not have qubit permutation here:
    final_mapping = {i: i for i in range(len(circuit_copy.qubits))}

    result = MappingResult(circuit=opt_circuit, initial_mapping=initial_mapping, final_mapping=final_mapping)
    return result
