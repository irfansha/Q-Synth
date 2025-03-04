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
from src.CnotSynthesis.circuit_utils.clifford_circuit_utils import (
    extract_circuit,
    compute_and_print_costs,
    compute_cnotdepth_swaps_as_3cx,
    compute_cost,
)
from src.CnotSynthesis.options import Options as op
import src.CnotSynthesis.cnot_synthesis_sat_qbf as cs
from src.CnotSynthesis.cnot_synthesis import equivalence_check
from src.CnotSynthesis.encodings.lifted_qbf import LiftedQbf
from src.CnotSynthesis.encodings.grounded_sat import GroundedSat
from src.CnotSynthesis.encodings.solve_and_extract_plan import SolveandExtractPlan
from src.CnotSynthesis.cnot_synthesis import coupling_graph_check


# solve using a planner:
def solve_cnot_synth(matrix, options, num_qubits):
    solver = SolveandExtractPlan(options)

    # If a QBF solver is called then lifted encoding is used:
    if options.solver == "caqe":
        encoder = LiftedQbf(matrix, options, num_qubits)
        start_run_time = clock.perf_counter()
        solver.run_caqe()
    else:
        # if a sat solver is called then we use the grounded encoding:
        assert options.solver == "cadical"
        encoder = GroundedSat(matrix, options, num_qubits)
        start_run_time = clock.perf_counter()
        solver.run_cadical()
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
        # Extract the plan:
        if options.minimization == "depth":
            solver.extract_depth_optimal_plan(encoder)
        else:
            assert options.minimization == "gates"
            solver.extract_cnot_optimal_plan(encoder)
        return solver.plan, False


# Solve cnot_synth problem with a planner, and print the result
def cnot_synth_main(matrix, options, num_qubits):
    if options.verbose > 1:
        print(f"\nUsing {options.encoding} encoding,", end=" ")
    if options.verbose > 1:
        print(f"\nUsing Solver {options.solver}")
    if options.verbose > 1:
        print(f"\nSearching for plan length {options.plan_length}")
    if options.verbose > 1 and options.coupling_graph:
        print(f"Mapping to Coupling graph:\n {options.coupling_graph}\n")
    plan, timed_out = solve_cnot_synth(matrix, options, num_qubits)
    if plan == None:
        # empty:
        return None, None, timed_out
    plan_length = len(plan)
    opt_circuit, _ = extract_circuit(plan, plan_length, options, num_qubits)
    # print(f"\nSolved in {plan_length} steps")
    return plan_length, opt_circuit, timed_out


def set_options(
    encoding,
    solver,
    preprocessor,
    time,
    minimization,
    verbose,
    coupling_graph,
    plan_length,
    optimal_search,
    qubit_permute,
    intermediate_files_path,
    check,
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
    options.optimal_search = optimal_search
    options.qubit_permute = qubit_permute
    options.check = check

    # find Benchmarks and Domains,
    source_location = os.path.dirname(cs.__file__)
    aux_files = os.path.join(source_location, intermediate_files_path)

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
    solver="qubi",
    preprocessor="bloqqer",
    time=1800,
    minimization="gates",
    verbose=0,
    coupling_graph=None,
    plan_length=None,
    optimal_search=None,
    qubit_permute=False,
    intermediate_files_path="intermediate_files",
    check=0,
):
    options = set_options(
        encoding,
        solver,
        preprocessor,
        time,
        minimization,
        verbose,
        coupling_graph,
        plan_length,
        optimal_search,
        qubit_permute,
        intermediate_files_path,
        check,
    )
    # we give the complete clifford matrix, we only next destabilizer X matrix for cnot synthesis:
    matrix = Clifford(circuit)
    num_qubits = len(circuit.qubits)

    if minimization == "gates":
        _, bound = compute_cost(circuit)
        if verbose > 1:
            print("Original number of CNOTs : ", bound)
    else:
        bound = compute_cnotdepth_swaps_as_3cx(circuit)
        if verbose > 1:
            print("Original circuit depth : ", bound)
    # initializing optimal circuit with original circuit:
    opt_circuit = circuit
    start_time = clock.perf_counter()
    # forward search:
    if options.optimal_search == "f":
        for cur_plan_length in range(bound):
            # update plan length:
            options.plan_length = cur_plan_length
            _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
            # we stop if solution is found:
            if cur_opt_circuit != None:
                if verbose > 1:
                    print("Optimal solution found")
                opt_circuit = cur_opt_circuit
                break
            elif timed_out:
                if verbose > 1:
                    print("Timed out, search stopped")
                break
    elif options.optimal_search == "uf":
        cur_plan_length = 0
        while 1:
            # update plan length:
            options.plan_length = cur_plan_length
            _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
            # we stop if solution is found:
            if cur_opt_circuit != None:
                if verbose > 1:
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
    elif options.optimal_search == "b":
        for cur_plan_length in range(bound - 1, 0, -1):
            # update plan length:
            options.plan_length = cur_plan_length
            _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
            # we stop if no solution is found:
            if not cur_opt_circuit:
                if verbose > 1:
                    print("Optimal solution found")
                break
            elif timed_out:
                if verbose > 1:
                    print("Timed out, search stopped")
                break
            else:
                opt_circuit = cur_opt_circuit
    else:
        assert options.optimal_search == None and options.plan_length != None
        _, cur_opt_circuit, timed_out = cnot_synth_main(matrix, options, num_qubits)
        opt_circuit = cur_opt_circuit
    total_time = clock.perf_counter() - start_time
    if options.verbose > 1:
        print(f"\nTime taken: {total_time}")
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
    return opt_circuit


# Optimize cnot circuit given a qasm file:
# Returns a more optimal circuit if found or returns the original circuit:
def cnot_optimization_from_file(
    circuit_in,
    encoding="lifted",
    solver="caqe",
    preprocessor="bloqqer",
    time=1800,
    minimization="gates",
    verbose=0,
    coupling_graph=None,
    plan_length=None,
    optimal_search=None,
    qubit_permute=False,
    intermediate_files_path="intermediate_files",
    check=0,
):
    circuit = QuantumCircuit.from_qasm_file(circuit_in)
    if not coupling_graph_check(circuit, coupling_graph):
        print("Circuit CNOT gates don't satisfy the coupling graph restrictions")
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
        optimal_search,
        qubit_permute,
        intermediate_files_path,
        check,
    )
