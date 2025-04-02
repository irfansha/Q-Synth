# Irfansha Shaik, Aarhus, 12 July 2023.

# Optimize a circuit by Peephole Optimization with cnot synthesis:
# - input: an input circuit
# - output: optimized circuit with cnot slices optimized (reduced CNOT count)
# - different methods as options to optimize the cnot slices


from typing import Optional
from qiskit import QuantumCircuit, qasm2
from src.PeepholeSlicing.circuit_utils import CircuitUtils as cu
from src.PeepholeSlicing.circuit_utils import (
    remove_zero_cost_swaps,
    equivalence_check_with_map,
    project_circuit,
    project_coupling_graph,
)
from src.CnotSynthesis.cnot_synthesis import cnot_optimization as cnot_op
from src.CnotSynthesis.cnot_synthesis_sat_qbf import (
    cnot_optimization as cnot_op_sat_qbf,
)
from src.CliffordSynthesis.clifford_synthesis_planning import (
    clifford_optimization as clifford_opt_planning,
)
from src.CliffordSynthesis.clifford_synthesis_sat import (
    clifford_optimization as clifford_opt_sat,
)
from src.CliffordSynthesis.circuit_utils import (
    compute_cnot_cost,
    compute_cnot_without_swaps_cost,
    compute_cnot_depth,
    compute_depth_swaps_as_3cx,
    compute_cnotdepth_swaps_as_3cx,
)
from src.LayoutSynthesis.architecture import platform as pt
from src.CnotSynthesis.options import Options as op
from src.CnotSynthesis.cnot_synthesis import coupling_graph_check
from src.Utilities.print_utils import print_stats

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
            cur_opt_circuit = cnot_op(
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
            cur_opt_circuit = cnot_op_sat_qbf(
                cur_optimization_slice,
                solver=solver,
                preprocessor="bloqqer",
                time=current_slice_time,
                minimization=args.minimize,
                verbose=args.verbose,
                coupling_graph=cur_coupling_graph,
                optimal_search=args.optimal_search,
                qubit_permute=args.qubit_permute,
                intermediate_files_path=args.intermediate_files_path,
                check=args.check,
            )
        else:
            print("Choose either a planner, a qbf solver or a sat solver")
            exit(-1)
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
            cur_opt_circuit = clifford_opt_planning(
                circuit=cur_optimization_slice,
                planner=args.planner,
                encoding=args.encoding,
                time=current_slice_time,
                cnot_minimization=args.minimize,
                verbose=args.verbose,
                coupling_graph=cur_coupling_graph,
                check=args.check,
            )
        else:
            # set default encoding:
            if args.encoding == None:
                args.encoding = "simpleaux"
            cur_opt_circuit, timed_out = clifford_opt_sat(
                circuit=cur_optimization_slice,
                encoding=args.encoding,
                solver=args.solver,
                nthreads=args.nthreads,
                time=current_slice_time,
                minimization=args.minimize,
                verbose=args.verbose,
                platform=args.platform,
                coupling_graph=cur_coupling_graph,
                gate_ordering=args.gate_ordering,
                optimal_search=args.optimal_search,
                simple_path_restrictions=args.simple_path_restrictions,
                cycle_bound=args.cycle_bound,
                qubit_permute=args.qubit_permute,
                intermediate_files_path=args.intermediate_files_path,
                check=args.check,
                report_timeout=True,
            )
    return cur_opt_circuit, timed_out


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
        initial_cx_gates = cnot_cost(slice.optimization_slice)
        final_cx_gates = cnot_cost(cur_opt_circuit)
        initial_cx_depth = cnot_depth(slice.optimization_slice)
        final_cx_depth = cnot_depth(cur_opt_circuit)
        print_stats(slice.optimization_slice, cur_opt_circuit)
        if args.minimize == "depth":
            if (final_cx_depth < initial_cx_depth) or (
                final_cx_depth == initial_cx_depth
                and (final_cx_gates < initial_cx_gates)
            ):
                # updating the existing slice with optimal one:
                slice.optimization_slice = cur_opt_circuit
        else:
            assert args.minimize == "gates"
            if (final_cx_gates < initial_cx_gates) or (
                final_cx_gates == initial_cx_gates
                and (final_cx_depth < initial_cx_depth)
            ):
                # updating the existing slice with optimal one:
                slice.optimization_slice = cur_opt_circuit
    else:
        # nothing improved:
        print_stats(slice.optimization_slice, slice.optimization_slice)


def peephole_synthesis(
    circuit_in=None,
    circuit_out=None,
    encoding="simpleaux",
    slicing="cnot",
    minimize="gates",
    model="sat",
    qubit_permute=None,
    gate_ordering=None,
    simple_path_restrictions=None,
    cycle_bound=3,
    disable_unused=True,
    optimal_search="f",
    solver=None,
    nthreads=1,
    time=600,
    platform=None,
    bidirectional=1,
    intermediate_files_path="./intermediate_files",
    verbose=0,
    check=0,
) -> Optional[QuantumCircuit]:

    # TODO: add descriptions of arguments:
    # --------------------------------------- Creating args separately ---------------------------------------
    args = op()
    args.circuit_in = circuit_in
    args.circuit_out = circuit_out
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
    args.optimal_search = optimal_search
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
    if args.platform:
        coupling_graph = pt(
            platform=args.platform,
            bidirectional=args.bidirectional,
            coupling_graph=None,
        )[1]
    else:
        coupling_graph = None

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
            args.sat_solver = "cd"
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
    circuit = QuantumCircuit.from_qasm_file(args.circuit_in)
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
    sliced_circuit = cu(circuit_copy, args.slicing, args.check)

    total_slices = len(sliced_circuit.slices)
    if args.platform != None:
        if args.slicing == "clifford":
            assert (
                args.qubit_permute == False
            ), "For now, we do not allow qubit permutation with layout aware (W+R) in clifford synthesis"
        else:
            assert args.slicing == "cnot"
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
    if args.minimize == "depth":
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
        assert args.minimize == "gates"
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
        if args.verbose >= 0:
            print(
                f"\nSolving slice {slice_id+1}:  {current_slice_count} of {total_slices} ... with {round(current_slice_time,2)}s timelimit"
            )
            # print(slice.optimization_slice)
        # optimize and add the optimization slice:
        num_cx_gates = cnot_cost(slice.optimization_slice)
        cx_depth = cnot_depth(slice.optimization_slice)
        # We only optimize a circuit if it has more than 0 gates:
        if args.minimize == "gates" and num_cx_gates <= 1:
            cur_opt_circuit = None
        elif args.minimize == "depth" and cx_depth <= 1:
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

    number_of_timedout_slices = len(timed_out_slices)
    if number_of_timedout_slices > 0:
        print(
            f"Running {number_of_timedout_slices} timed-out slices with remaining time"
        )
        current_slice_count = 0
        for timed_out_slice_id in timed_out_slices:
            if args.remaining_time < 0.001:
                print("Timed out, remaining time less than 0.001s")
                break
            current_slice_count = current_slice_count + 1
            if args.verbose >= 0:
                print(
                    f"\nSolving timedout slice {timed_out_slice_id+1}:  {current_slice_count} of {number_of_timedout_slices} ... with {round(args.remaining_time,2)}s timelimit"
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
        if args.verbose > 1:
            print("\nOptimized Circuit:")
            print(opt_circuit)
            print("\nOriginal circuit Measurements:")
            print(sliced_circuit.circuit_measurements)
            print(
                "\nQubit permutation dictionary to be applied on original measurements:"
            )
            print(post_mapping)
        # checking equivalence using the post mapping:
        if args.check:
            print(
                "\nChecking Equivalence between original (without measurements) and permuted optimized circuit"
            )
            equivalence_check_with_map(
                sliced_circuit.measurementless_circuit,
                opt_circuit,
                post_mapping,
                verbose=args.verbose,
            )
    else:
        # If original circuit has measurements, we add to the optimized circuit as well:
        if sliced_circuit.circuit_measurements != None:
            opt_circuit = opt_circuit.compose(sliced_circuit.circuit_measurements)
        if args.verbose > 1:
            print("\nOptimized Circuit:")
            print(opt_circuit)

    total_time = clock.perf_counter() - start_time
    if args.verbose > 0:
        print(f"\nTime taken: {total_time}")
    print("Full circuit stats:")
    print_stats(circuit, opt_circuit)
    if args.circuit_out != None:
        qasm2.dump(opt_circuit, args.circuit_out)
    return opt_circuit
