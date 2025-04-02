#! /usr/bin/env python3

# Irfansha Shaik, 31.01.2024, Aarhus

# Optimize a clifford circuit by synthesis:
# - input: an input clifford circuit
# - goal: transform stabilizer matric to goal matrix by CNOT, H, S operations
# - output: minimal number of CNOT gates (for now; later depth)

import os
import time as clock
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford
from src.CliffordSynthesis.circuit_utils import (
    extract_circuit,
    compute_cnot_cost,
    compute_cnotdepth_swaps_as_3cx,
    compute_cnot_without_swaps_cost,
    compute_cnot_depth,
)
from src.CnotSynthesis.options import Options as op
from src.CliffordSynthesis.clifford_synthesis_planning import equivalence_check
from src.CliffordSynthesis.encodings.simple_aux import SimpleAux
from src.CliffordSynthesis.encodings.solve_and_extract_plan import (
    SolveandExtractPlan,
)
from src.CliffordSynthesis.encodings.recover_phase import recover_phase
from src.CnotSynthesis.cnot_synthesis import coupling_graph_check


# solve using a sat solver:
def solve_clifford_synth(matrix, options, num_qubits):
    solver = SolveandExtractPlan(options)

    # # simple encoding with a sat solver:
    encoder = SimpleAux(matrix, options, num_qubits)
    start_run_time = clock.perf_counter()
    if options.solver == "gimsatul":
        solver.run_gimsatul()
    elif options.solver == "mallob":
        solver.run_mallob()
    else:
        # by default, we run cadical:
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
        solver.extract_simpleaux_plan(encoder)
        # finding current phase:
        opt_circuit, _ = extract_circuit(
            solver.plan, len(solver.plan), options, num_qubits
        )
        current_phase = Clifford(opt_circuit).phase
        phase_gates = recover_phase(
            optimal_phase=current_phase,
            goal_phase=encoder.matrix.phase,
            num_qubits=num_qubits,
        )
        solver.plan = phase_gates + solver.plan
        return solver.plan, False


# Solve clifford_synth problem with a sat solver, and print the result
def clifford_synth_main(matrix, options, num_qubits):
    if options.verbose > 1:
        print(f"\nUsing {options.encoding} encoding,", end=" ")
    if options.verbose > 1:
        print(f"\nUsing Solver {options.solver}")
    if options.verbose > 1:
        print(f"\nSearching for plan length {options.plan_length}")
    if options.verbose > 1 and options.coupling_graph:
        print(f"Mapping to Coupling graph:\n {options.coupling_graph}\n")
    plan, timed_out = solve_clifford_synth(matrix, options, num_qubits)
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
    nthreads,
    time,
    minimization,
    verbose,
    platform,
    coupling_graph,
    plan_length,
    optimal_search,
    qubit_permute,
    gate_ordering,
    simple_path_restrictions,
    cycle_bound,
    intermediate_files_path,
    check,
):
    options = op()
    options.verbose = verbose
    # default current model is sat:
    options.model = "sat"
    options.encoding = encoding
    options.solver = solver
    options.nthreads = nthreads
    options.time = time
    options.remaining_time = time
    options.platform = platform
    options.coupling_graph = coupling_graph
    options.minimization = minimization
    options.plan_length = plan_length
    options.optimal_search = optimal_search
    options.qubit_permute = qubit_permute
    options.gate_ordering = gate_ordering
    options.simple_path_restrictions = simple_path_restrictions
    options.cycle_bound = cycle_bound
    options.check = check

    # find Benchmarks and Domains,
    aux_files = intermediate_files_path

    # we use intermediate directory for intermediate files:
    os.makedirs(aux_files, exist_ok=True)
    options.dimacs_out = os.path.join(aux_files, "out.dimacs")
    options.solver_out = os.path.join(aux_files, "out.txt")
    return options


# Returns a more optimal circuit if found or returns the original circuit:
def clifford_optimization(
    circuit,
    encoding="simpleaux",
    solver="cadical",
    nthreads=1,
    time=1800,
    minimization="gates",
    verbose=0,
    platform=None,
    coupling_graph=None,
    plan_length=None,
    gate_ordering=None,
    simple_path_restrictions=None,
    cycle_bound=3,
    optimal_search="f",
    qubit_permute=False,
    intermediate_files_path="intermediate_files",
    check=0,
    report_timeout=False,
):
    options = set_options(
        encoding,
        solver,
        nthreads,
        time,
        minimization,
        verbose,
        platform,
        coupling_graph,
        plan_length,
        optimal_search,
        qubit_permute,
        gate_ordering,
        simple_path_restrictions,
        cycle_bound,
        intermediate_files_path,
        check,
    )
    # we give the complete clifford matrix, we only next destabilizer X matrix for cnot synthesis:
    matrix = Clifford(circuit)
    num_qubits = len(circuit.qubits)

    if minimization == "gates":
        # if qubit permute allows, we ignore swaps:
        if options.qubit_permute:
            bound = compute_cnot_without_swaps_cost(circuit)
        else:
            bound = compute_cnot_cost(circuit)
        if verbose > 1:
            print("Original number of CNOTs : ", bound)
    else:
        if options.qubit_permute:
            bound = compute_cnot_depth(circuit)
        else:
            bound = compute_cnotdepth_swaps_as_3cx(circuit)
        if verbose > 1:
            print("Original circuit CNOT depth : ", bound)
    # initializing optimal circuit with original circuit:
    opt_circuit = circuit
    if verbose > 1:
        print("Original Circuit:")
        print(circuit)
    start_time = clock.perf_counter()
    # forward search:
    if options.optimal_search == "f":
        for cur_plan_length in range(bound):
            # update plan length:
            options.plan_length = cur_plan_length
            _, cur_opt_circuit, timed_out = clifford_synth_main(
                matrix, options, num_qubits
            )
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
            _, cur_opt_circuit, timed_out = clifford_synth_main(
                matrix, options, num_qubits
            )
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
        while bound > 0:
            # update plan length:
            options.plan_length = bound - 1
            _, cur_opt_circuit, timed_out = clifford_synth_main(
                matrix, options, num_qubits
            )
            # we stop if no solution is found:
            if timed_out:
                if verbose > 1:
                    print("Timed out, search stopped")
                break
            elif not cur_opt_circuit:
                if verbose > 1:
                    print("Optimal solution found")
                break
            else:
                if options.qubit_permute:
                    # we do not count SWAP gates:
                    if minimization == "gates":
                        bound = compute_cnot_without_swaps_cost(cur_opt_circuit)
                    else:
                        bound = compute_cnot_depth(cur_opt_circuit)
                else:
                    if minimization == "gates":
                        bound = compute_cnot_cost(cur_opt_circuit)
                    else:
                        bound = compute_cnotdepth_swaps_as_3cx(cur_opt_circuit)
                opt_circuit = cur_opt_circuit
    else:
        # running for a specific plan length:
        assert options.optimal_search == None and options.plan_length != None
        _, cur_opt_circuit, timed_out = clifford_synth_main(matrix, options, num_qubits)
        opt_circuit = cur_opt_circuit
    total_time = clock.perf_counter() - start_time
    if options.verbose > 1:
        print(f"\nTime taken: {total_time}")
    # if opt circuit in not None, then we compute costs and check equivalence:
    if opt_circuit != None:
        if options.verbose > 1:
            print(opt_circuit)
        if options.check:
            equivalence_check(circuit, opt_circuit, None, options)
    if report_timeout:
        return opt_circuit, timed_out
    else:
        return opt_circuit


# Optimize clifford circuit given a qasm file:
# Returns a more optimal circuit if found or returns the original circuit:
def clifford_optimization_from_file(
    circuit_in,
    encoding="simpleaux",
    solver="cadical",
    nthreads=1,
    time=1800,
    minimization="gates",
    verbose=0,
    platform=None,
    coupling_graph=None,
    plan_length=None,
    gate_ordering=None,
    simple_path_restrictions=None,
    cycle_bound=3,
    optimal_search="f",
    qubit_permute=False,
    intermediate_files_path="intermediate_files",
    check=0,
):
    circuit = QuantumCircuit.from_qasm_file(circuit_in)
    if not coupling_graph_check(circuit, coupling_graph):
        print("Circuit CNOT gates don't satisfy the coupling graph restrictions")
        print("(Hint: use 'q-synth layout' first)")
        exit(-1)
    return clifford_optimization(
        circuit=circuit,
        encoding=encoding,
        solver=solver,
        nthreads=nthreads,
        time=time,
        minimization=minimization,
        verbose=verbose,
        coupling_graph=coupling_graph,
        plan_length=plan_length,
        optimal_search=optimal_search,
        qubit_permute=qubit_permute,
        gate_ordering=gate_ordering,
        simple_path_restrictions=simple_path_restrictions,
        cycle_bound=cycle_bound,
        intermediate_files_path=intermediate_files_path,
        check=check,
    )
