#! /usr/bin/env python3

# Irfansha Shaik, Aarhus, 26 December 2023.

# Optimize a cnot circuit by synthesis:
# - input: an input cnot circuit
# - goal: transform stabilizer X matric to goal matrix by CNOT operations
# - output: minimal number of gates (other metrics are a todo)

import os
import time
import src.CnotSynthesis.cnot_synthesis as cs
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford
from src.CnotSynthesis.run_planner import RunPlanner as rp
from src.LayoutSynthesis.circuit_utils import gate_get_qubit
from src.CnotSynthesis.circuit_utils.clifford_circuit_utils import (
    extract_circuit,
    get_measured_circuit,
    compute_and_print_costs,
)
from src.CnotSynthesis.generate_pddl_specification import generate_problem_specification
from src.CnotSynthesis.options import Options as op


# solve using a planner:
def solve_cnot_synth(matrix, options, num_qubits):
    pddl_lines = generate_problem_specification(matrix, options, num_qubits)
    # print(pddl_lines)
    # writing pddl to file:
    f = open(options.pddl_problem_out, "w")
    for line in pddl_lines:
        f.write(line)
    f.close()
    run_instance = rp(options)
    # returning empty plan:
    return run_instance.plan


# Solve cnot_synth problem with a planner, and print the result
def cnot_synth_main(matrix, options, num_qubits):
    start_time = time.perf_counter()
    if options.verbose > 1:
        print(f"\nUsing {options.encoding} encoding,", end=" ")
    if options.verbose > 1:
        print(f"\nUsing Planner {options.planner}")
    if options.verbose > 1 and options.coupling_graph:
        print(f"Mapping to Coupling graph:\n {options.coupling_graph}\n")
    plan = solve_cnot_synth(matrix, options, num_qubits)
    if plan == None:
        # empty:
        return None, None, None
    plan_length = len(plan)
    opt_circuit, qubit_map = extract_circuit(plan, plan_length, options, num_qubits)
    # print(f"\nSolved in {plan_length} steps")
    total_time = time.perf_counter() - start_time
    if options.verbose > 1:
        print(f"\nTime taken: {total_time}")
    return plan_length, opt_circuit, qubit_map


def set_options(encoding, planner, time, minimization, verbose, coupling_graph):
    options = op()
    options.verbose = verbose
    options.encoding = encoding
    options.planner = planner
    options.time = time
    options.coupling_graph = coupling_graph
    options.minimization = minimization
    options.qubit_permute = False

    # find Benchmarks and Domains,
    source_location = os.path.dirname(cs.__file__)
    options.domains = os.path.join(source_location, "Domains")

    aux_files = os.path.join(source_location, "intermediate_files")

    if options.coupling_graph:
        # We only handle right now with plain lifted encoding:
        # TODO: handle for rest of the encoding with permutations and swaps:
        assert options.encoding == "lifted" or options.encoding == "lifted-swaps"
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
    if options.verbose > 1:
        print("================== Checking Equivalence ==================")
    if (
        "permute" in options.encoding
        or "swaps" in options.encoding
        or (options.qubit_permute and qubit_map != None)
    ):
        # Measuring original circuit:
        org_circuit_copy = org_circuit.copy()
        org_circuit_copy.measure_all()
        if options.verbose > 1:
            print(org_circuit_copy)
        measured_circuit = get_measured_circuit(opt_circuit, qubit_map)
        if options.verbose > 1:
            print(measured_circuit)
        # checking equivalence:
        if options.verbose > 0:
            print(
                "Currently, equivalence checking with permutations/swaps is not supported"
            )
    else:
        org_clifford_matrix = Clifford(org_circuit)
        opt_circuit_clifford = Clifford(opt_circuit)
        assert org_clifford_matrix == opt_circuit_clifford
        # print(opt_circuit)
        if options.verbose > 1:
            print("Optimized circuit is equivalent to the original circuit")


# given a circuit and a coupling map we check if cnot gates satisfy
# the coupling connections:
def coupling_graph_check(circuit, coupling_map):
    if coupling_map:
        for gate in circuit:
            if len(gate.qubits) == 2:
                q1 = gate_get_qubit(gate, 0)
                q2 = gate_get_qubit(gate, 1)
                if [q1, q2] not in coupling_map:
                    return False
    return True


# Returns a more optimal circuit if found or returns the original circuit:
def cnot_optimization(
    circuit,
    encoding="lifted",
    planner="lama",
    time=1800,
    minimization="cnot",
    verbose=None,
    coupling_graph=None,
):
    options = set_options(
        encoding, planner, time, minimization, verbose, coupling_graph
    )
    # we give the complete clifford matrix, we only next destabilizer X matrix for cnot synthesis:
    matrix = Clifford(circuit)
    num_qubits = len(circuit.qubits)

    _, opt_circuit, qubit_map = cnot_synth_main(matrix, options, num_qubits)
    # if opt circuit in not None, then we compute costs and check equivalence:
    if opt_circuit != None:
        compute_and_print_costs(circuit, opt_circuit, verbose=verbose)
        # equivalence_check(circuit, opt_circuit, qubit_map, options)
    return opt_circuit


# Optimize cnot circuit given a qasm file:
# Returns a more optimal circuit if found or returns the original circuit:
def cnot_optimization_from_file(
    circuit_in,
    encoding="lifted",
    planner="lama",
    time=1800,
    minimization="cnot",
    verbose=None,
    coupling_graph=None,
):
    circuit = QuantumCircuit.from_qasm_file(circuit_in)
    if not coupling_graph_check(circuit, coupling_graph):
        print("Circuit CNOT gates don't satisfy the coupling graph restrictions")
        exit(-1)
    return cnot_optimization(
        circuit, encoding, planner, time, minimization, verbose, coupling_graph
    )
