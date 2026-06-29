#! /usr/bin/env python3

# Irfansha Shaik, Aarhus, 19 December 2023.

# Optimize a clifford circuit by synthesis:
# - input: an input clifford circuit
# - goal: transform stabilizers and destabilizers to goal matrix by CNOT, H, S operations
# - output: minimal number of gates (other metrics are a todo)

import os
import time
import qsynth.CliffordSynthesis.clifford_synthesis_planning as cs
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford
from qsynth.CliffordSynthesis.run_planner import RunPlanner as rp
from qsynth.CliffordSynthesis.circuit_utils import (
    extract_circuit,
    compute_cnot_cost,
    compute_oneq_gate_count,
    compute_pauli_gate_count,
)
from qsynth.CliffordSynthesis.generate_pddl_specification import (
    generate_problem_specification,
)
from qsynth.CliffordSynthesis.options import Options as op
from qsynth.CliffordSynthesis.encodings.recover_phase import recover_phase
from qsynth.Utilities.result import MappingResult

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
    if options.verbose > 0:
        print(f"\nUsing {options.encoding} encoding,", end=" ")
    if options.verbose > 0:
        print(f"\nUsing Planner {options.planner}")
    if options.verbose > 0 and options.coupling_graph:
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
    if options.verbose > 0:
        print(f"\nTime taken: {total_time}")
    return plan_length, opt_circuit_with_phase, qubit_map

def compute_cnot_structure_and_dependencies(options,circuit):
    options.dependencies = dict()
    options.gate_qubit_map = dict()
    cnot_counter = 0
    for gate in circuit:
        if gate.operation.name == "cx":
            ctrl = gate.qubits[0]._index
            targ = gate.qubits[1]._index
            ctrl_1q_gate = f"c{cnot_counter}_ctrl"
            targ_1q_gate = f"c{cnot_counter}_targ"
            cnot_gate = f"c{cnot_counter}"
            if cnot_gate == "c0":
                options.dependencies[ctrl_1q_gate] = "base_gate"
            else:
                prev_cnot_gate = f"c{cnot_counter-1}"
                options.dependencies[ctrl_1q_gate] = prev_cnot_gate
            options.dependencies[targ_1q_gate] = ctrl_1q_gate
            options.dependencies[cnot_gate] = targ_1q_gate
            options.gate_qubit_map[cnot_gate] = (ctrl, targ)
            options.gate_qubit_map[ctrl_1q_gate] = (ctrl,)
            options.gate_qubit_map[targ_1q_gate] = (targ,)
            cnot_counter += 1
    for i in range(circuit.num_qubits):
        gate = f"final_1q_q{i}"
        if gate == "final_1q_q0" and cnot_counter == 0:
            options.dependencies[gate] = "base_gate"
        elif gate == "final_1q_q0":
            options.dependencies[gate] = f"c{cnot_counter-1}"
        else:
            prev_gate = f"final_1q_q{i-1}"
            options.dependencies[gate] = prev_gate
        options.gate_qubit_map[gate] = (i,)

def set_options(
    circuit, encoding, planner, metric, time, verbose, coupling_graph, check
):
    options = op()
    options.verbose = verbose
    options.encoding = encoding
    options.planner = planner
    options.metric = metric
    options.time = time
    options.coupling_graph = coupling_graph
    options.check = check

    # find Benchmarks and Domains,
    source_location = os.path.dirname(cs.__file__)
    options.domains = os.path.join(source_location, "Domains")

    aux_files = "intermediate_files"
    if options.metric == "cx-count" or options.metric == "cx-count_1q-count":
        # we minimize cnot count, so we given normal formal upper bound as cost:
        # We compute CNOT cost based on input circuit and normal form upper bound:
        initial_cnot_cost = compute_cnot_cost(circuit)
        # number of qubits:
        num_qubits = len(circuit.qubits)
        # updated normal form upper bound:
        options.cnot_cost = 2 * (initial_cnot_cost) + 2 * (num_qubits) + 1
    elif options.metric == "cx-count_near-optimal":
        # we minimize cnot count, so we give 10 as cost:
        options.cnot_cost = 10
    else:
        assert options.metric == "gate-count"
        # we minimize total gate count, so we give 1 as cost:
        options.cnot_cost = 1

    # set number of two qubit gates based on initial circuit:
    options.twoq_gate_count = compute_cnot_cost(circuit)
    options.oneq_gate_count = compute_oneq_gate_count(circuit) - compute_pauli_gate_count(circuit)

    # setting plan bound:
    if options.encoding == "costbased" or options.encoding == "simple":
        options.plan_bound = (options.cnot_cost*options.twoq_gate_count) + options.oneq_gate_count
        #print(options.plan_bound)
    elif options.encoding == "normalform":
        # each cnot can have at most 2 one qubit actions before + final one qubit gates
        options.plan_bound = (2 * options.twoq_gate_count) + len(circuit.qubits)
        #print(options.plan_bound)
    elif options.encoding == "rigidcnot":
        # we can only improve by removing one qubit gates:
        options.plan_bound = options.twoq_gate_count + len(circuit.qubits)

    # flip_cnot only affects the rigidcnot encoding (adds the (flip_cnot) predicate
    # in generate_pddl_specification.py); normalform/costbased ignore it.
    options.flip_cnot = False
    if options.encoding == "rigidcnot":
        # in rigid cnot encoding we need to compute cnot structure and dependencies:
        compute_cnot_structure_and_dependencies(options, circuit)

    # we use intermediate directory for intermediate files:
    os.makedirs(aux_files, exist_ok=True)
    options.pddl_domain_out = os.path.join(
            options.domains, options.encoding + ".pddl"
    )
    options.pddl_problem_out = os.path.join(aux_files, "problem.pddl")
    options.log_out = os.path.join(aux_files, "log_out")
    options.SAS_file = os.path.join(aux_files, "out.sas")
    options.plan_file = os.path.join(aux_files, "plan")
    return options


def equivalence_check(org_circuit, opt_circuit, qubit_map, options):
    if options.verbose > 1:
        print("================== Checking Equivalence ==================")
    if "permute" in options.encoding:
        print("Equivalence check not available")
    else:
        org_clifford_matrix = Clifford(org_circuit)
        opt_circuit_clifford = Clifford(opt_circuit)
        assert org_clifford_matrix == opt_circuit_clifford
        # print(opt_circuit)
        if options.verbose > 1:
            print("Optimized circuit is equivalent to the original circuit")


# Returns a more optimal circuit if found or returns the original circuit:
def clifford_optimization(
    circuit,
    encoding="simple",
    planner="fd-ms",
    metric="cx-count",
    time=1800,
    verbose=None,
    coupling_graph=None,
    check=0,
):
    # Assert encoding is either simple, costbased, normalform or bounded.
    assert encoding in ["simple", "costbased", "normalform", "rigidcnot"]
    options = set_options(
        circuit=circuit, encoding=encoding, planner=planner, metric=metric, time=time, verbose=verbose, coupling_graph=coupling_graph, check=check
    )

    clifford_matrix = Clifford(circuit)
    num_qubits = len(circuit.qubits)

    _, opt_circuit, qubit_map = clifford_main(clifford_matrix, options, num_qubits)
    if opt_circuit is None:
        # no optimization found, return original circuit
        return MappingResult(
            circuit=circuit,
            initial_mapping={i: i for i in range(num_qubits)},
            final_mapping={i: i for i in range(num_qubits)},
            no_plan_found=True,
        )
    # We do not have initial permutation, So one-to-one mapping is applied:
    initial_mapping = {i: i for i in range(num_qubits)}
    result = MappingResult(
        circuit=opt_circuit, initial_mapping=initial_mapping, final_mapping=qubit_map
    )
    return result


# Optimize clifford circuit given a qasm file:
# Returns a more optimal circuit if found or returns the original circuit:
def clifford_optimization_from_file(
    circuit_in,
    encoding="simple",
    planner="fd-ms",
    metric="cx-count",
    time=1800,
    verbose=None,
    coupling_graph=None,
    check=0,
):
    circuit = QuantumCircuit.from_qasm_file(circuit_in)
    return clifford_optimization(
        circuit=circuit,
        encoding=encoding,
        planner=planner,
        metric=metric,
        time=time,
        verbose=verbose,
        coupling_graph=coupling_graph,
        check=check,
    )
