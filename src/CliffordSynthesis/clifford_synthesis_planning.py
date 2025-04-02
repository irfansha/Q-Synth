#! /usr/bin/env python3

# Irfansha Shaik, Aarhus, 19 December 2023.

# Optimize a clifford circuit by synthesis:
# - input: an input clifford circuit
# - goal: transform stabilizers and destabilizers to goal matrix by CNOT, H, S operations
# - output: minimal number of gates (other metrics are a todo)

import os
import time
import src.CliffordSynthesis.clifford_synthesis_planning as cs
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford
from src.CliffordSynthesis.run_planner import RunPlanner as rp
from src.CliffordSynthesis.circuit_utils import (
    extract_circuit,
    compute_cnot_cost,
)
from src.CliffordSynthesis.generate_pddl_specification import (
    generate_problem_specification,
)
from src.CliffordSynthesis.options import Options as op
from src.CliffordSynthesis.encodings.recover_phase import recover_phase


# solve using a planner:
def solve_clifford(clifford_matrix, options, num_qubits):
    pddl_lines = generate_problem_specification(clifford_matrix, options, num_qubits)
    # print(pddl_lines)
    # writing pddl to file:
    f = open(options.pddl_problem_out, "w")
    for line in pddl_lines:
        f.write(line)
    f.close()
    run_instance = rp(options)
    # returning empty plan:
    return run_instance.plan


# Solve clifford problem with a planner, and print the result
def clifford_main(clifford_matrix, options, num_qubits):
    start_time = time.perf_counter()
    if options.verbose:
        print(f"\nUsing {options.encoding} encoding,", end=" ")
    if options.verbose:
        print(f"\nUsing Planner {options.planner}")
    if options.verbose and options.coupling_graph:
        print(f"Mapping to Coupling graph:\n {options.coupling_graph}\n")
    plan = solve_clifford(clifford_matrix, options, num_qubits)
    if plan == None:
        # empty:
        return None, None, None
    plan_length = len(plan)
    opt_circuit, qubit_map = extract_circuit(plan, plan_length, options, num_qubits)
    current_phase = Clifford(opt_circuit).phase
    phase_gates = recover_phase(
        optimal_phase=current_phase,
        goal_phase=clifford_matrix.phase,
        num_qubits=num_qubits,
    )
    plan = phase_gates + plan
    plan_length += len(phase_gates)
    # circuit with recovered phase:
    opt_circuit_with_phase, qubit_map = extract_circuit(
        plan, plan_length, options, num_qubits
    )
    # print(f"\nSolved in {plan_length} steps")
    total_time = time.perf_counter() - start_time
    if options.verbose:
        print(f"\nTime taken: {total_time}")
    return plan_length, opt_circuit_with_phase, qubit_map


def set_options(
    encoding, planner, time, cnot_minimization, verbose, coupling_graph, check
):
    options = op()
    options.verbose = verbose
    options.encoding = encoding
    options.planner = planner
    options.time = time
    options.coupling_graph = coupling_graph
    options.cnot_minimization = cnot_minimization
    options.check = check

    # find Benchmarks and Domains,
    source_location = os.path.dirname(cs.__file__)
    options.domains = os.path.join(source_location, "Domains")

    aux_files = "intermediate_files"

    if options.coupling_graph:
        # We only handle right now with plain gate_optimal encoding:
        # TODO: handle for rest of the encoding with permutations and swaps:
        assert options.encoding == "gate_optimal"
        map_string = "-map"
    else:
        map_string = ""

    # we use intermediate directory for intermediate files:
    os.makedirs(aux_files, exist_ok=True)
    options.pddl_domain_out = os.path.join(
        options.domains, options.encoding + map_string + ".pddl"
    )
    options.pddl_problem_out = os.path.join(aux_files, "problem.pddl")
    options.log_out = os.path.join(aux_files, "log_out")
    options.SAS_file = os.path.join(aux_files, "out.sas")
    options.plan_file = os.path.join(aux_files, "plan")
    return options


def equivalence_check(org_circuit, opt_circuit, qubit_map, options):
    if options.verbose > 0:
        print("================== Checking Equivalence ==================")
    if "permute" in options.encoding:
        print("Equivalence check not available")
    else:
        org_clifford_matrix = Clifford(org_circuit)
        opt_circuit_clifford = Clifford(opt_circuit)
        assert org_clifford_matrix == opt_circuit_clifford
        # print(opt_circuit)
        if options.verbose > 0:
            print("Optimized circuit is equivalent to the original circuit")


def compute_and_print_costs(
    org_circuit, opt_circuit, cnot_minimization=None, verbose=0
):

    initial_cx_gates = compute_cnot_cost(org_circuit)
    if verbose > 1:
        print("Original Circuit: ")
        print(org_circuit)
        print("Initial CNOT gates: ", initial_cx_gates)
        if cnot_minimization == "depth":
            print("Initial depth: ", org_circuit.depth())

    final_cx_gates = compute_cnot_cost(opt_circuit)
    if verbose > 1:
        print("Optimized Circuit: ")
        print(opt_circuit)
        print("Final CNOT gates: ", final_cx_gates)
        if cnot_minimization == "depth":
            print("Final depth: ", opt_circuit.depth())

    return initial_cx_gates, final_cx_gates


# Returns a more optimal circuit if found or returns the original circuit:
def clifford_optimization(
    circuit,
    encoding="gate_optimal",
    planner="lama",
    time=1800,
    cnot_minimization=None,
    verbose=None,
    coupling_graph=None,
    check=0,
):
    options = set_options(
        encoding, planner, time, cnot_minimization, verbose, coupling_graph, check
    )

    clifford_matrix = Clifford(circuit)
    num_qubits = len(circuit.qubits)

    _, opt_circuit, qubit_map = clifford_main(clifford_matrix, options, num_qubits)
    # if opt circuit in not None, then we compute costs and check equivalence:
    if opt_circuit != None:
        compute_and_print_costs(circuit, opt_circuit, cnot_minimization, verbose)
        if check:
            equivalence_check(circuit, opt_circuit, qubit_map, options)
    return opt_circuit


# Optimize clifford circuit given a qasm file:
# Returns a more optimal circuit if found or returns the original circuit:
def clifford_optimization_from_file(
    circuit_in,
    encoding="gate_optimal",
    planner="lama",
    time=1800,
    cnot_minimization=None,
    verbose=None,
    coupling_graph=None,
    check=0,
):
    circuit = QuantumCircuit.from_qasm_file(circuit_in)
    return clifford_optimization(
        circuit,
        encoding,
        planner,
        time,
        cnot_minimization,
        verbose,
        coupling_graph,
        check,
    )
