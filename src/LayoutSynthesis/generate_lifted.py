# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from src.LayoutSynthesis.circuit_utils import (
    strict_dependencies,
    relaxed_dependencies,
    all_cx_gates,
    cancel_cnots,
    gate_get_qubit,
)
from src.LayoutSynthesis.architecture import platform


class GenerateLifted:

    # Parse and compute cnot gate list with dependencies satisfied:
    def parse_and_compute(self):

        # loading quantum circuit with qiskit:
        try:
            self.input_circuit = QuantumCircuit.from_qasm_file(self.args.circuit_in)
        except FileNotFoundError:
            print(f"Error: circuit_in file '{self.args.circuit_in}' not found")
            exit(-1)

        self.num_lqubits = len(self.input_circuit.qubits)
        self.logical_circuit = self.input_circuit.copy()  # might be pre-optimized later
        if self.args.verbose > 0:
            print(self.input_circuit)

        # cancel CNOTS
        if self.args.cnot_cancel == 1:
            deps = relaxed_dependencies(self.logical_circuit, verbose=self.args.verbose)
            self.logical_circuit = cancel_cnots(
                self.logical_circuit, deps, verbose=self.args.verbose
            )

        # compute dependencies
        if self.args.relaxed == 1:
            self.cnot_depends = relaxed_dependencies(
                self.logical_circuit, verbose=self.args.verbose
            )
        else:
            self.cnot_depends = strict_dependencies(
                self.logical_circuit, verbose=self.args.verbose
            )

        self.list_cx_gates = all_cx_gates(self.logical_circuit)
        if self.args.verbose > 2:
            print("cnot gates left:", self.list_cx_gates)

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

    def generate_encoding_line(self, f):
        relaxed = "relaxed" if self.args.relaxed == 1 else "strict"
        withanc = "with" if self.args.allow_ancillas else "without"
        f.write(
            f"; Lifted {relaxed} encoding ({withanc} ancillaries) for {self.args.circuit_in}\n"
        )

    # compute the logical qubits that are used in a CNOT gate
    def used_in_cnot(self):
        cnot_lqubits = set()
        for cnot in self.list_cx_gates:
            ctrl = gate_get_qubit(self.logical_circuit[cnot], 0)
            data = gate_get_qubit(self.logical_circuit[cnot], 1)
            cnot_lqubits.add(ctrl)
            cnot_lqubits.add(data)
        return sorted(cnot_lqubits)

    def generate_specification(self):
        # name to be update according to the circuit input files:
        self.pddl_lines.append("(define (problem circuit)\n")
        # we assume our domain is fixed, Quantum:
        self.pddl_lines.append("  (:domain Quantum)\n")
        self.pddl_lines.append("  (:objects\n")
        self.pddl_lines.append("  ;; logical qubits\n")
        # generating objects for logical qubits:
        lqubits = ""
        for i in self.used_in_cnot():
            lqubits += f"l{i} "
        self.pddl_lines.append(f"  {lqubits} - lbit\n")

        self.pddl_lines.append("  ;; physical qubits\n")
        # generating objects for physical qubits:
        pqubits = ""
        for i in range(self.num_physical_qubits):
            pqubits += f"p{i} "
        self.pddl_lines.append(f"  {pqubits} - pbit\n")

        gate_str = "  "
        for cx_gate in self.list_cx_gates:
            gate_str += f"g{cx_gate} "
        self.pddl_lines.append(f"{gate_str} - gate)\n")

    def generate_init(self):

        # we alway start we d0 as current depth:
        self.pddl_lines.append("(:init\n")
        self.pddl_lines.append("  ;; no physical qubits are occupied initially\n")
        self.pddl_lines.append("  ;; no logical qubits are mapped initially\n")
        self.pddl_lines.append("  ;; no CNOT gates are done initially\n")
        self.pddl_lines.append("  ;; connectivity graph\n")

        # adding coupling/connectivity graph with connected predicates:
        for edge in self.bi_coupling_map:
            self.pddl_lines.append(f"  (connected p{edge[0]} p{edge[1]})\n")

        self.pddl_lines.append(
            "  ;; listing cnots with their logical qubits (and dependencies)\n"
        )
        for cx_gate in self.list_cx_gates:
            ctrl = gate_get_qubit(self.logical_circuit[cx_gate], 0)
            data = gate_get_qubit(self.logical_circuit[cx_gate], 1)
            cur_str = f"  (cnot l{ctrl} l{data} g{cx_gate} "

            if self.args.relaxed == 0:
                x, y = self.cnot_depends[cx_gate]
                # print(x,y)
                if len(x) == 0:
                    cur_str += f"l{ctrl} "
                else:
                    assert len(x) == 1  # can only handle strict dependencies
                    cur_str += f"g{x[0]} "

                if len(y) == 0:
                    cur_str += f"l{data}"
                else:
                    assert len(y) == 1  # can only handle strict dependencies
                    cur_str += f"g{y[0]}"

            cur_str += ")\n"
            self.pddl_lines.append(cur_str)
            # print(self.cnot_depends[cx_gate])

        if self.args.relaxed == 1:
            self.pddl_lines.append("   ;; list cnots with dependencies (for relaxed)\n")
            for cx_gate in self.list_cx_gates:
                x, y = self.cnot_depends[cx_gate]
                for g in x:
                    self.pddl_lines.append(f"  (ctrl_depends g{cx_gate} g{g})\n")
                for g in y:
                    self.pddl_lines.append(f"  (data_depends g{cx_gate} g{g})\n")

        self.pddl_lines.append(")\n")

    def generate_goal(self):
        self.pddl_lines.append("(:goal\n")
        self.pddl_lines.append("  (and\n")
        for cx_gate in self.list_cx_gates:
            self.pddl_lines.append(f" (done g{cx_gate})\n")
            self.num_actions += 1
        self.pddl_lines.append("  )\n)\n)")

    # Parses domain and problem file:
    def __init__(self, args):
        self.args = args
        self.num_actions = 0
        self.pddl_lines = []

        self.parse_and_compute()

        self.set_architecture()

        if self.num_lqubits > self.num_physical_qubits:
            print(
                f"No solution, since there are more logical than physical qubits ({self.num_lqubits} > {self.num_physical_qubits})"
            )
            exit(-1)

        self.generate_specification()

        self.generate_init()

        self.generate_goal()

        # writing pddl to file:
        f = open(args.pddl_problem_out, "w")
        self.generate_encoding_line(f)
        for line in self.pddl_lines:
            f.write(line)
        f.close()
