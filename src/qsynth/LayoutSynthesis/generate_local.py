# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from qsynth.LayoutSynthesis.circuit_utils import (
    strict_dependencies,
    relaxed_dependencies,
    cancel_cnots,
    all_cx_gates,
    gate_get_qubit,
)
from qsynth.LayoutSynthesis.architecture import platform


class GenerateLocal:

    # Parse and compute cnot gate list with dependencies satisfied:
    def parse_and_compute(self):

        self.input_circuit = self.args.circuit_in
        self.logical_circuit = self.input_circuit.copy()
        self.num_lqubits = len(self.input_circuit.qubits)
        if self.args.verbose > 0:
            print(self.input_circuit)

        # cancel CNOTS
        if self.args.cnot_cancel == 1:
            deps = relaxed_dependencies(self.logical_circuit, verbose=self.args.verbose)
            self.logical_circuit = cancel_cnots(
                self.logical_circuit, deps, verbose=self.args.verbose
            )

        # computing dependencies
        if self.args.relaxed == 0:
            self.cnot_depends = strict_dependencies(
                self.logical_circuit, verbose=self.args.verbose
            )
        else:
            self.cnot_depends = relaxed_dependencies(
                self.logical_circuit, verbose=self.args.verbose
            )

        self.list_cx_gates = all_cx_gates(self.logical_circuit)
        if self.args.verbose > 2:
            print("cnot gates: ", self.list_cx_gates)

    def generate_encoding_line(self, f):
        relaxed = "relaxed" if self.args.relaxed == 1 else "strict"
        withanc = "with" if self.args.allow_ancillas else "without"
        f.write(f"; Local {relaxed} encoding ({withanc} ancillaries)\n")

    def generate_domain(self):
        f = open(self.args.pddl_domain_out, "w")
        self.generate_encoding_line(f)
        # requirements and types:
        f.write("(define (domain Quantum)\n")
        f.write("(:requirements :strips :typing :negative-preconditions)\n")
        if self.args.relaxed == 0:
            f.write("(:types gate lqubit pqubit - object)\n")
        else:
            f.write("(:types gate pqubit - object\n")
            f.write("             lqubit - gate)\n")

        # generating constants for logical qubits:
        lqubits = ""
        for i in self.used_in_cnot():
            lqubits += f"l{i} "
        # generating constants for CNOT gates:
        gates = ""
        for cnot in self.list_cx_gates:
            gates += f"g{cnot} "

        f.write(f"(:constants\n")
        f.write(f"\t{gates} - gate ; all CNOT gates \n")
        f.write(f"\t{lqubits}- lqubit ; all logical qubits\n")
        f.write(")\n")

        # predicates:
        f.write("(:predicates\n")
        f.write("\t(occupied ?p - pqubit)\n")
        f.write("\t(mapped ?l - lqubit ?p - pqubit)\n")
        f.write("\t(connected ?p1 - pqubit ?p2 - pqubit)\n")
        f.write("\t(done ?g - gate)\n)\n")

        # swap action
        f.write("(:action swap\n")
        f.write(" :parameters (?l1 ?l2 - lqubit ?p1 ?p2 - pqubit)\n")
        f.write(
            " :precondition (and (mapped ?l1 ?p1) (mapped ?l2 ?p2) (connected ?p1 ?p2))\n"
        )
        f.write(
            " :effect (and (not (mapped ?l1 ?p1)) (not (mapped ?l2 ?p2)) (mapped ?l1 ?p2) (mapped ?l2 ?p1))\n)\n"
        )
        if self.args.allow_ancillas:
            f.write("(:action swap-ancillary1\n")
            f.write(" :parameters (?l1 - lqubit ?p1 ?p2 - pqubit)\n")
            f.write(
                " :precondition (and (mapped ?l1 ?p1) (not (occupied ?p2)) (connected ?p1 ?p2))\n"
            )
            f.write(
                " :effect (and (not (mapped ?l1 ?p1)) (not (occupied ?p1)) (mapped ?l1 ?p2) (occupied ?p2))\n)\n"
            )

            f.write("(:action swap-ancillary2\n")
            f.write(" :parameters (?l2 - lqubit ?p1 ?p2 - pqubit)\n")
            f.write(
                " :precondition (and (mapped ?l2 ?p2) (not (occupied ?p1)) (connected ?p1 ?p2))\n"
            )
            f.write(
                " :effect (and (not (mapped ?l2 ?p2)) (not (occupied ?p2)) (mapped ?l2 ?p1) (occupied ?p1))\n)\n"
            )

        def gen_strict_cnot_action(ctrl, data, gate_idx, deps):
            ctrl_data = (ctrl, data)
            f.write(f"(:action apply_cnot_g{gate_idx}\n")
            f.write(" :parameters (?p1 ?p2 - pqubit)\n")

            precondition_string = " :precondition (and"
            # fixed preconditions for required cnot:
            precondition_string += f" (not (done g{gate_idx})) (connected ?p1 ?p2)"
            for arg in (0, 1):  # two arguments of this CX key
                if len(deps[arg]) == 1:
                    # take care of the dependency
                    precondition_string += f" (done g{deps[arg][0]})"
                if len(deps[arg]) == 1:
                    # make sure the logical qubit is mapped to the physical qubit
                    precondition_string += f" (mapped l{ctrl_data[arg]} ?p{arg+1})"
                if len(deps[arg]) == 0:
                    # integrated initial mapping, check ?p is free
                    precondition_string += f" (not (occupied ?p{arg+1}))"
            precondition_string += ")\n"
            f.write(precondition_string)

            effect_string = f" :effect (and (done g{gate_idx})"
            for arg in (0, 1):
                if len(deps[arg]) == 0:
                    # effect if there are no dependencies: map initial bits
                    effect_string += (
                        f" (mapped l{ctrl_data[arg]} ?p{arg+1}) (occupied ?p{arg+1})"
                    )
            effect_string += f")\n)\n"
            f.write(effect_string)

        def gen_relaxed_cnot_action(ctrl, data, gate_idx, deps, mapctrl, mapdata):
            f.write(f"(:action apply_cnot_g{gate_idx}\n")
            f.write(" :parameters (?p1 ?p2 - pqubit)\n")
            precondition_string = " :precondition (and"
            precondition_string += f" (not (done g{gate_idx})) (connected ?p1 ?p2)"

            # take care of all dependencies:
            for arg in (0, 1):  # two arguments of this CX gate
                logical = f"l{(ctrl, data)[arg]}"
                physical = f"?p{arg+1}"
                initial = (mapctrl, mapdata)[arg]  # arg must be mapped initially

                # All dependencies should be done:
                if len(deps[arg]) > 0:
                    for val in deps[arg]:
                        precondition_string += f" (done g{val})"
                elif not initial:
                    precondition_string += f" (done {logical})"

                # If initial map, qubits should not be done/occupied
                # Otherwise: qubits should be mapped already
                if initial:
                    precondition_string += (
                        f" (not (done {logical})) (not (occupied {physical}))"
                    )
                else:
                    precondition_string += f" (mapped {logical} {physical})"

            precondition_string += ")\n"
            f.write(precondition_string)

            effect_string = ""
            # effect: this gate is not required anymore
            effect_string += f" :effect (and (done g{gate_idx})"
            for arg in (0, 1):
                logical = f"l{(ctrl, data)[arg]}"
                physical = f"?p{arg+1}"
                initial = (mapctrl, mapdata)[arg]  # arg must be mapped initially
                if initial:
                    effect_string += f" (done {logical}) (mapped {logical} {physical}) (occupied {physical})"
            effect_string += ")\n)\n"
            f.write(effect_string)

        # for each cnot action, we generate a partially grounded locally dependent action:
        for gate_idx, deps in self.cnot_depends.items():
            ctrl = gate_get_qubit(self.logical_circuit[gate_idx], 0)
            data = gate_get_qubit(self.logical_circuit[gate_idx], 1)

            if self.args.relaxed == 0:
                gen_strict_cnot_action(ctrl, data, gate_idx, deps)
            else:
                gen_relaxed_cnot_action(ctrl, data, gate_idx, deps, False, False)
                if deps[0] == []:
                    gen_relaxed_cnot_action(ctrl, data, gate_idx, deps, True, False)
                if deps[1] == []:
                    gen_relaxed_cnot_action(ctrl, data, gate_idx, deps, False, True)
                if deps[0] == [] and deps[1] == []:
                    gen_relaxed_cnot_action(ctrl, data, gate_idx, deps, True, True)

        # closing the domain file:
        f.write(")\n")

    def set_architecture(self):
        # edge list is injected from args
        (
            self.coupling_map,
            self.bi_coupling_map,
            self.bridge_bicoupling_map,
            self.bridge_middle_pqubit_dict,
            self.reverse_swap_distance_dict,
            self.num_physical_qubits,
        ) = platform(
            self.args.platform,
            self.args.bidirectional,
            self.args.coupling_graph,
            self.args.verbose,
        )

    def generate_specification(self):
        # name to be update according to the circuit input files:
        self.pddl_lines.append("(define (problem circuit)\n")
        # we assume our domain is fixed, Quantum:
        self.pddl_lines.append("  (:domain Quantum)\n")
        self.pddl_lines.append("  (:objects\n")
        self.pddl_lines.append("  ;; physical qubits\n")
        # generating objects for physical qubits:
        pqubits = ""
        for i in range(self.num_physical_qubits):
            pqubits += f"p{i} "
        self.pddl_lines.append(f"  {pqubits}- pqubit\n")
        self.pddl_lines.append(")\n")

    def generate_init(self):
        self.pddl_lines.append("(:init\n")
        self.pddl_lines.append(";; no gates are done initially\n")
        self.pddl_lines.append(";; no physical qubits are occupied initially\n")
        self.pddl_lines.append(";; no logical qubits are mapped initially\n")
        self.pddl_lines.append(";; connectivity graph:\n")

        # adding coupling/connectivity graph with connected predicates:
        for edge in self.bi_coupling_map:
            self.pddl_lines.append(f"  (connected p{edge[0]} p{edge[1]})\n")

        self.pddl_lines.append(")\n")

    # compute the logical qubits that are used in a CNOT gate
    def used_in_cnot(self):
        cnot_lqubits = set()
        for cnot in self.list_cx_gates:
            ctrl = gate_get_qubit(self.logical_circuit[cnot], 0)
            data = gate_get_qubit(self.logical_circuit[cnot], 1)
            cnot_lqubits.add(ctrl)
            cnot_lqubits.add(data)
        return sorted(cnot_lqubits)

    def generate_goal(self):
        self.pddl_lines.append("(:goal\n")

        if self.args.relaxed == 1:
            self.pddl_lines.append(
                "  (and ;; listing logical qubits and all gates to be done\n"
            )
            for i in self.used_in_cnot():
                self.pddl_lines.append(f"    (done l{i})\n")
        else:
            self.pddl_lines.append("  (and ;; listing all gates to be done\n")
        for cx_gate in self.list_cx_gates:
            self.pddl_lines.append(f"    (done g{cx_gate})\n")
            self.num_actions += 1
        self.pddl_lines.append("  )\n)\n)")

    # Parses domain and problem file:
    def __init__(self, args):
        self.args = args
        self.num_actions = 0
        self.pddl_lines = []
        self.initial_map_action_list = {}

        self.parse_and_compute()

        self.set_architecture()

        if self.num_lqubits > self.num_physical_qubits:
            print(
                f"No solution, since there are more logical than physical qubits ({self.num_lqubits} > {self.num_physical_qubits})"
            )
            exit(-1)

        self.generate_domain()

        self.generate_specification()

        self.generate_init()

        self.generate_goal()

        # writing pddl to file:
        f = open(args.pddl_problem_out, "w")
        self.generate_encoding_line(f)
        for line in self.pddl_lines:
            f.write(line)
        f.close()
