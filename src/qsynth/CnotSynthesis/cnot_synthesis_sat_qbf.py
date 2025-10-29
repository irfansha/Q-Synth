#! /usr/bin/env python3

# Irfansha Shaik, 31.01.2024, Aarhus

# Optimize a cnot circuit by synthesis:
# - input: an input cnot circuit
# - goal: transform stabilizer X matric to goal matrix by CNOT operations
# - output: minimal number of gates (other metrics are a todo)

import os
import time as clock
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford
from qsynth.CliffordSynthesis.circuit_utils import (
    extract_circuit,
    compute_and_print_costs,
    compute_cnotdepth_swaps_as_3cx,
    compute_cnot_cost,
    compute_cnot_without_swaps_cost,
    compute_cnot_depth,
)
from qsynth.CnotSynthesis.options import Options as op
from qsynth.CnotSynthesis.cnot_synthesis import equivalence_check
from qsynth.CnotSynthesis.encodings.lifted_qbf import LiftedQbf
from qsynth.CnotSynthesis.encodings.grounded_sat import GroundedSat
from qsynth.Utilities.run_solvers import RunSolvers
from qsynth.CnotSynthesis.encodings.extract_plan import ExtractPlan
from qsynth.CnotSynthesis.cnot_synthesis import coupling_graph_check
from qsynth.Utilities.result import MappingResult


# solve using a planner:
def solve_cnot_synth(matrix, options, num_qubits):
    solver = RunSolvers(options)

    # If a QBF solver is called then lifted encoding is used:
    if options.solver == "caqe":
        encoder = LiftedQbf(matrix, options, num_qubits)
        start_run_time = clock.perf_counter()
        solver.run_caqe()
    else:
        # if a sat solver is called then we use the grounded encoding:
        encoder = GroundedSat(matrix, options, num_qubits)
        start_run_time = clock.perf_counter()
        if options.solver == "cd":
            solver.run_cadical()
        else:
            assert options.solver.startswith("pysat-")
            solver.run_pysat_solvers()
    solving_time = clock.perf_counter() - start_run_time
    if options.verbose > 1:
        print("Solving time: " + str(solving_time))

    options.remaining_time = options.remaining_time - solving_time
    if options.verbose > 1:
        print("Remaining time: " + str(options.remaining_time))

    if solver.sat == -1:
        if options.verbose > 1:
            print("Timed out")
        return None, True
    elif solver.sat == 0:
        if options.verbose > 1:
            print("No plan found")
        return None, False
    elif solver.sat == 1:
        if options.verbose > 1:
            print("Plan found")
        extract_plan = ExtractPlan(options=options, solver=solver)
        # Extract the plan:
        if (
            options.minimization == "cx-depth"
            or "local_cx-count" in options.minimization
            or options.minimization == "bounded_cx-count_local_cx-depth"
        ):
            extract_plan.extract_depth_optimal_plan(encoder)
        else:
            assert options.minimization == "cx-count"
            extract_plan.extract_cnot_optimal_plan(encoder)
        return extract_plan.plan, False


# Solve cnot_synth problem with a planner, and print the result
def cnot_synth_main(matrix, options, num_qubits):
    if options.verbose > 1:
        print(f"Using {options.encoding} encoding,", end=" ")
    if options.verbose > 1:
        print(f"Using Solver {options.solver}")
    if options.verbose > 1:
        print(f" for plan length {options.plan_length}")
    if options.verbose > 1 and options.coupling_graph:
        print(f"Mapping to Coupling graph:\n {options.coupling_graph}")
    plan, timed_out = solve_cnot_synth(matrix, options, num_qubits)
    if plan == None:
        # empty:
        return None, None, timed_out
    plan_length = len(plan)
    opt_circuit, _ = extract_circuit(plan, plan_length, options, num_qubits)
    # print(f"\nSolved in {plan_length} steps")
    return plan_length, opt_circuit, timed_out


# get right bound based on qubit permute option and metric:
def compute_bound(circuit, metric, qubit_permute):
    if metric == "cx-count":
        # if qubit permute allows, we ignore swaps:
        if qubit_permute:
            bound = compute_cnot_without_swaps_cost(circuit)
        else:
            bound = compute_cnot_cost(circuit)
    elif metric == "cx-depth":
        if qubit_permute:
            bound = compute_cnot_depth(circuit)
        else:
            bound = compute_cnotdepth_swaps_as_3cx(circuit)
    return bound


def set_options(
    encoding,
    solver,
    preprocessor,
    time,
    minimization,
    verbose,
    coupling_graph,
    plan_length,
    search_strategy,
    gate_ordering,
    qubit_permute,
    intermediate_files_path,
    check,
    cardinality,
):
    options = op()
    options.verbose = verbose
    options.encoding = encoding
    options.solver = solver
    options.preprocessor = preprocessor
    options.time = time
    options.remaining_time = time
    options.coupling_graph = coupling_graph
    options.minimization = minimization
    options.plan_length = plan_length
    options.search_strategy = search_strategy
    options.gate_ordering = gate_ordering
    options.qubit_permute = qubit_permute
    options.check = check
    options.cardinality = cardinality

    # find Benchmarks and Domains,
    aux_files = intermediate_files_path

    # we use intermediate directory for intermediate files:
    os.makedirs(aux_files, exist_ok=True)
    options.qcir_out = os.path.join(aux_files, "out.qcir")
    options.qdimacs_out = os.path.join(aux_files, "out.qdimacs")
    options.dimacs_out = os.path.join(aux_files, "out.dimacs")
    options.preprocessor_out = os.path.join(aux_files, "preprocessed_out.qdimacs")
    options.solver_out = os.path.join(aux_files, "out.txt")
    return options


# Returns a more optimal circuit if found or returns the original circuit:
def cnot_optimization(
    circuit,
    encoding="lifted",
    solver="cd",
    preprocessor=None,
    time=1800,
    minimization="cx-count",
    verbose=0,
    coupling_graph=None,
    plan_length=None,
    search_strategy="forward",
    gate_ordering=None,
    qubit_permute=False,
    intermediate_files_path="intermediate_files",
    check=0,
    report_timeout=False,
    cardinality=1,
):
    # if coupling graph is not None, we set platform to custom:
    if coupling_graph is not None:
        platform = "custom"
    options = set_options(
        encoding,
        solver,
        preprocessor,
        time,
        minimization,
        verbose,
        coupling_graph,
        plan_length,
        search_strategy,
        gate_ordering,
        qubit_permute,
        intermediate_files_path,
        check,
        cardinality,
    )
    # we give the complete clifford matrix, we only next destabilizer X matrix for cnot synthesis:
    matrix = Clifford(circuit)
    num_qubits = len(circuit.qubits)

    if minimization == "cx-count":
        bound = compute_bound(circuit, "cx-count", qubit_permute)
        if verbose > 1:
            print("Original number of CNOTs : ", bound)
    elif minimization == "cx-depth":
        bound = compute_bound(circuit, "cx-depth", qubit_permute)
        if verbose > 1:
            print("Original circuit CNOT depth : ", bound)
    else:
        assert (
            "local_cx-count" in minimization
            or minimization == "bounded_cx-count_local_cx-depth"
        ), ("Unknown minimization metric: " + minimization)
        if "local_cx-count" in minimization:
            assert "bounded_cx-depth" in minimization
            # the bound here is on cx-count, we do not optimize cx-depth:
            bound = compute_bound(circuit, "cx-count", qubit_permute)
            # we first fix depth for the plan length::
            options.plan_length = compute_bound(circuit, "cx-depth", qubit_permute)
            if verbose > 1:
                print("Original circuit CNOT count (for local optimization) : ", bound)
        else:
            assert minimization == "bounded_cx-count_local_cx-depth"
            # the bound here is on cx-depth, we do not optimize cx-count:
            bound = compute_bound(circuit, "cx-depth", qubit_permute)
            # we first fix local cx-count:
            options.local_cxcount_bound = compute_bound(
                circuit, "cx-count", qubit_permute
            )
        # we set the optimal search to "backward":
        options.search_strategy = "backward"
        # If depth is fixed then we do not need to disable gate ordering:
        if "fixed-bounded_cx-depth" not in minimization:
            options.gate_ordering = False
        else:
            options.gate_ordering = True

    # initializing optimal circuit with original circuit:
    opt_circuit = circuit
    start_time = clock.perf_counter()
    # forward search:
    if options.search_strategy == "forward":
        for cur_plan_length in range(bound):
            # update plan length:
            options.plan_length = cur_plan_length
            _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
            # we stop if solution is found:
            if cur_opt_circuit != None:
                if verbose > 0:
                    print("Optimal solution found")
                opt_circuit = cur_opt_circuit
                break
            elif timed_out:
                if verbose > 1:
                    print("Timed out, search stopped")
                break
    elif options.search_strategy == "unbounded-forward":
        cur_plan_length = 0
        while 1:
            # update plan length:
            options.plan_length = cur_plan_length
            _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
            # we stop if solution is found:
            if cur_opt_circuit != None:
                if verbose > 0:
                    print("Optimal solution found")
                opt_circuit = cur_opt_circuit
                break
            elif timed_out:
                if verbose > 1:
                    print("Timed out, search stopped")
                break
            else:
                # else we increase the plan length:
                cur_plan_length += 1
    # backward search:
    elif options.search_strategy == "backward":
        while bound > 0:
            # update plan length:
            if "local_cx-count" in minimization:
                assert "bounded_cx-depth" in minimization
                # we update local CNOT bound:
                options.local_cxcount_bound = bound - 1
                if verbose > 1:
                    print("Local CNOT count bound: ", options.local_cxcount_bound)
            else:
                options.plan_length = bound - 1
            _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
            # we stop if no solution is found:
            if not cur_opt_circuit:
                if verbose > 0:
                    print(f"Optimal solution found")
                break
            elif timed_out:
                if verbose > 1:
                    print("Timed out, search stopped")
                break
            else:
                if "local_cx-count" in minimization:
                    assert "bounded_cx-depth" in minimization
                    bound = compute_bound(cur_opt_circuit, "cx-count", qubit_permute)
                    # we set the plan length to the current bound i.e. cx-depth:
                    options.plan_length = compute_bound(
                        cur_opt_circuit, "cx-depth", qubit_permute
                    )
                elif minimization == "bounded_cx-count_local_cx-depth":
                    bound = compute_bound(cur_opt_circuit, "cx-depth", qubit_permute)
                    # we set the local cx-count bound to the current bound i.e. cx-count:
                    options.local_cxcount_bound = compute_bound(
                        cur_opt_circuit, "cx-count", qubit_permute
                    )
                else:
                    bound = compute_bound(cur_opt_circuit, minimization, qubit_permute)
                opt_circuit = cur_opt_circuit
    else:
        # running for a specific plan length:
        assert options.search_strategy == None and options.plan_length != None
        _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
        opt_circuit = cur_opt_circuit
    total_time = clock.perf_counter() - start_time
    if options.verbose > 0:
        print(f"Time taken: {total_time}")
    # if opt circuit in not None, then we compute costs and check equivalence:
    if opt_circuit != None:
        compute_and_print_costs(
            circuit,
            opt_circuit,
            cnot_minimization=minimization,
            verbose=options.verbose,
        )
        if options.check:
            equivalence_check(circuit, opt_circuit, None, options)
    # We do not have initial permutation, So one-to-one mapping is applied:
    initial_mapping = {i: i for i in range(num_qubits)}
    if report_timeout:
        mapped_result = MappingResult(
            circuit=opt_circuit, timed_out=timed_out, initial_mapping=initial_mapping
        )
    else:
        mapped_result = MappingResult(
            circuit=opt_circuit, initial_mapping=initial_mapping
        )
    return mapped_result


# Optimize cnot circuit given a qasm file:
# Returns a more optimal circuit if found or returns the original circuit:
def cnot_optimization_from_file(
    circuit_in,
    encoding="lifted",
    solver="cd",
    preprocessor=None,
    time=1800,
    minimization="cx-count",
    verbose=0,
    coupling_graph=None,
    plan_length=None,
    search_strategy="forward",
    gate_ordering=None,
    qubit_permute=False,
    intermediate_files_path="intermediate_files",
    check=0,
):
    circuit = QuantumCircuit.from_qasm_file(circuit_in)
    if not coupling_graph_check(circuit, coupling_graph):
        print("Circuit CNOT gates don't satisfy the coupling graph restrictions")
        print("(Hint: use 'q-synth layout' first)")
        exit(-1)
    return cnot_optimization(
        circuit,
        encoding,
        solver,
        preprocessor,
        time,
        minimization,
        verbose,
        coupling_graph,
        plan_length,
        search_strategy,
        gate_ordering,
        qubit_permute,
        intermediate_files_path,
        check,
    )
