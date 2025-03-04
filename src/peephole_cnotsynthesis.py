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
)
from src.CnotSynthesis.cnot_synthesis import cnot_optimization as cnot_op_planning
from src.CnotSynthesis.cnot_synthesis_sat_qbf import (
    cnot_optimization as cnot_op_sat_qbf,
)
from src.CnotSynthesis.circuit_utils.clifford_circuit_utils import (
    compute_cost,
    compute_cnot_cost,
    compute_cnot_depth,
    compute_depth_swaps_as_3cx,
    compute_cnotdepth_swaps_as_3cx,
    compute_and_print_costs,
)
from src.LayoutSynthesis.architecture import platform as pt
from src.CnotSynthesis.options import Options as op
from src.CnotSynthesis.cnot_synthesis import coupling_graph_check

from pathlib import Path
import os
import time as clock


def peephole_cnotsynthesis(
    circuit_in=None,
    circuit_out=None,
    minimize="gates",
    model="sat",
    qubit_permute=None,
    solver=None,
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
    args.verbose = verbose
    args.minimize = minimize
    args.intermediate_files_path = intermediate_files_path
    args.model = model
    args.solver = solver
    args.qubit_permute = qubit_permute
    args.time = time
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
        coupling_graph = pt(args.platform, args.bidirectional, None)[1]
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
        if args.solver == None:
            args.qbf_solver = "caqe"
        else:
            assert args.solver == "caqe"
            args.qbf_solver = args.solver
    elif args.model == "sat":
        if args.solver == None:
            args.sat_solver = "cadical"
        else:
            assert args.solver == "cd"
            args.sat_solver = "cadical"
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
    if args.verbose > 0:
        print("\nOriginal Circuit:")
        print(circuit)

    if not coupling_graph_check(circuit, coupling_graph):
        print("Circuit CNOT gates don't satisfy the coupling graph restrictions")
        print("(Hint: use 'q-synth layout' first)")
        exit(-1)

    # Copy of original circuit:
    circuit_copy = circuit.copy()
    # slicing for CNOT synthesis:
    sliced_circuit = cu(circuit_copy, "cnot", args.check)

    opt_circuit = QuantumCircuit(num_qubits)

    total_slices = len(sliced_circuit.slices)
    for slice_id in range(total_slices):
        slice = sliced_circuit.slices[slice_id]
        if args.verbose >= 0:
            print(f"Solving slice {slice_id+1} of {total_slices} ...")
            print(slice.optimization_slice)
        # optimize and add the optimization slice:
        _, num_cx_gates = compute_cost(slice.optimization_slice)
        # We only optimize a circuit if it has more than 0 gates:
        if num_cx_gates < 1:
            cur_opt_circuit = None
        else:
            if args.planner != None:
                cur_opt_circuit = cnot_op_planning(
                    slice.optimization_slice,
                    planner=args.planner,
                    time=args.time,
                    minimization=args.minimize,
                    verbose=args.verbose,
                    coupling_graph=coupling_graph,
                )
            elif args.qbf_solver != None or args.sat_solver != None:
                if args.qbf_solver != None:
                    solver = args.qbf_solver
                else:
                    assert args.sat_solver != None
                    solver = args.sat_solver
                cur_opt_circuit = cnot_op_sat_qbf(
                    slice.optimization_slice,
                    solver=solver,
                    preprocessor="bloqqer",
                    time=args.time,
                    minimization=args.minimize,
                    verbose=args.verbose,
                    coupling_graph=coupling_graph,
                    optimal_search="f",
                    qubit_permute=args.qubit_permute,
                    intermediate_files_path=args.intermediate_files_path,
                    check=args.check,
                )
            else:
                print("Choose either a planner, a qbf solver or a sat solver")
                exit(-1)

        # We assume that the orginial circuit is already mapped
        if cur_opt_circuit == None:
            # if no plan found, then append the original slice:
            opt_circuit = opt_circuit.compose(slice.optimization_slice)
        else:
            initial_cost, initial_cx_gates, final_cost, final_cx_gates = (
                compute_and_print_costs(
                    slice.optimization_slice,
                    cur_opt_circuit,
                    cnot_minimization=args.minimize,
                    verbose=0,
                )
            )
            # if we allow qubit permutation, swaps do not count:
            if args.qubit_permute:
                initial_cx_gates = compute_cnot_cost(slice.optimization_slice)
                final_cx_gates = compute_cnot_cost(cur_opt_circuit)
            # only for depth minimization, the depth is prioritised first:
            if args.minimize == "depth" and compute_depth_swaps_as_3cx(
                slice.optimization_slice
            ) > compute_depth_swaps_as_3cx(cur_opt_circuit):
                opt_circuit = opt_circuit.compose(cur_opt_circuit)
            # if final cnot gates are less than initial:
            elif final_cx_gates < initial_cx_gates:
                opt_circuit = opt_circuit.compose(cur_opt_circuit)
            # else we append the original cnot slice, new circuit is worse than the original:
            elif final_cx_gates == initial_cx_gates and final_cost < initial_cost:
                opt_circuit = opt_circuit.compose(cur_opt_circuit)
            else:
                opt_circuit = opt_circuit.compose(slice.optimization_slice)
        # simply append the non cnot slice:
        opt_circuit = opt_circuit.compose(slice.non_optimization_slice)

    if args.qubit_permute:
        # we remove zero-cost swaps, mapping can change with swap removal:
        opt_circuit, post_mapping = remove_zero_cost_swaps(opt_circuit, num_qubits)
        if args.verbose > 0:
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
        if args.verbose > 0:
            print("\nOptimized Circuit:")
            print(opt_circuit)

    total_time = clock.perf_counter() - start_time
    if args.verbose > 0:
        print(f"\nTime taken: {total_time}")

    print("\nReporting change in metrics (original -> optimized):")
    print(f"\tDepth : {circuit.depth()} -> {opt_circuit.depth()}")
    print(
        f"\tCNOT depth: {compute_cnot_depth(circuit)} -> {compute_cnot_depth(opt_circuit)}"
    )
    print(
        f"\tNo. of CNOTs: {compute_cnot_cost(circuit)} -> {compute_cnot_cost(opt_circuit)}"
    )
    print("\nMetrics when SWAP gates are considered as 3 CNOTs:")
    print(
        f"\tDepth : {compute_depth_swaps_as_3cx(circuit, args.check, args.verbose)} -> {compute_depth_swaps_as_3cx(opt_circuit, args.check, args.verbose)}"
    )
    print(
        f"\tCNOT depth: {compute_cnotdepth_swaps_as_3cx(circuit)} -> {compute_cnotdepth_swaps_as_3cx(opt_circuit)}"
    )
    print(
        f"\tNo. of CNOTs: {compute_cost(circuit)[1]} -> {compute_cost(opt_circuit)[1]}"
    )

    if args.circuit_out != None:
        qasm2.dump(opt_circuit, args.circuit_out)

    return opt_circuit
