# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

"""
Todos:
  - specify grounded actions for avoiding unnecessary actions/propositions.
  - specify in Heirarcial planning? seems more suitable?
  - partial order planners work?
  - use forall and exists conditional statements for compact or effective domain.
  - group many cnot gates for reducing time slices? might improve performance
  - Allow unrolling with qiskit if circuit has non-standard gates (later)
"""

from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from qsynth.LayoutSynthesis.architecture import platform
from qsynth.LayoutSynthesis.circuit_utils import (
    strict_dependencies,
    relaxed_dependencies,
    cancel_cnots,
)


class GenerateGlobalPDDL:

    # Parse and compute cnot gate list with dependencies satisfied:
    def parse_and_compute(self):

        self.input_circuit = self.args.circuit_in
        self.num_lqubits = len(self.input_circuit.qubits)

        if self.args.verbose > 0:
            print(self.input_circuit)

        self.logical_circuit = self.input_circuit.copy()  # might be pre-optimized later

        # cancel CNOTS
        if self.args.cnot_cancel == 1:
            deps = relaxed_dependencies(self.logical_circuit, verbose=self.args.verbose)
            self.logical_circuit = cancel_cnots(
                self.logical_circuit, deps, verbose=self.args.verbose
            )

        assert (
            self.args.relaxed == 0
        )  # relaxed is not implemented for the global encoding
        self.cnot_depends = strict_dependencies(
            self.logical_circuit, verbose=self.args.verbose
        )

        # converting to dag for extracting layers:
        self.input_dag = circuit_to_dag(self.input_circuit)

        # print(input_dag.op_nodes())

        # each gate is represented using 3 tuple, (qubit1, qubit2, layer_number)
        self.list_cx_gates = []

        for i, layer in enumerate(self.input_dag.layers()):
            if self.args.verbose > 2:
                print("Printing operators layer by layer:")
                print("layer number:", i + 1)
            subdag = layer["graph"]
            # print(subdag)
            for node in subdag.op_nodes():
                # for now asserting every 2 qubit operation is "cx":
                if node.op.num_qubits == 2:
                    if node.name != "cx":
                        print(
                            f"Error: currently, Q-Synth assumes CNOT is the only binary operators, found '{node.name}'"
                        )
                        exit(-1)
                    self.list_cx_gates.append(
                        (node.qargs[0]._index, node.qargs[1]._index, i + 1)
                    )
                if self.args.verbose > 2:
                    print(
                        node.name,
                        node.op.num_qubits,
                        node.qargs,
                        node.cargs,
                        node.op.params,
                    )

        if self.args.verbose > 2:
            print("cnot gates: ", self.list_cx_gates)

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
        self.pddl_lines.append("(define (problem test)")
        # we assume our domain is fixed, Quantum:
        self.pddl_lines.append("  (:domain Quantum)\n")
        self.pddl_lines.append("  (:objects\n")
        self.pddl_lines.append("  ;; logical qubits\n")
        # generating objects for logical qubits:
        self.lqubits = []
        for i in range(self.num_lqubits):
            self.lqubits.append("l" + str(i))
        self.pddl_lines.append("  " + " ".join(self.lqubits) + " - lqubit\n")
        self.pddl_lines.append("  ;; physical qubits\n")
        # generating objects for physical qubits:
        pqubits = []
        for i in range(self.num_physical_qubits):
            pqubits.append("p" + str(i))
        self.pddl_lines.append("  " + " ".join(pqubits) + " - pqubit\n")
        self.pddl_lines.append("  ;; layer depth\n")
        # generating objects for cx operating layer depths:
        self.cx_layer_depths = []
        for gate in self.list_cx_gates:
            # we simply append the layer depth with d:
            if "d" + str(gate[2]) not in self.cx_layer_depths:
                self.cx_layer_depths.append("d" + str(gate[2]))
        self.pddl_lines.append(
            "  " + " ".join(self.cx_layer_depths) + " - depth\n  )\n"
        )

    def generate_init(self):

        self.pddl_lines.append(
            "(:init\n  ;; all physical qubits are not occupied, by default\n  ;; all logical qubits are not occupied, by default\n"
        )
        self.pddl_lines.append(
            f"  ;; current depth is first CX layer\n  (current_depth {str(self.cx_layer_depths[0])})\n  ;; connectivity graph\n"
        )

        # adding coupling/connectivity graph with connected predicates:
        for edge in self.bi_coupling_map:
            self.pddl_lines.append(
                "  (connected " + "p" + str(edge[0]) + " p" + str(edge[1]) + ")\n"
            )

        # we connect the depths:
        self.pddl_lines.append("  ;; depths\n")
        for i in range(len(self.cx_layer_depths) - 1):
            self.pddl_lines.append(
                "  (next_depth "
                + str(self.cx_layer_depths[i])
                + " "
                + str(self.cx_layer_depths[i + 1])
                + ")\n"
            )

        self.pddl_lines.append("  ;; listing required cnots\n")
        for cx_gate in self.list_cx_gates:
            self.pddl_lines.append(
                "  (rcnot "
                + "l"
                + str(cx_gate[0])
                + " "
                + "l"
                + str(cx_gate[1])
                + " "
                + "d"
                + str(cx_gate[2])
                + ")\n"
            )

        self.pddl_lines.append(")\n")

    def generate_goal(self):
        self.pddl_lines.append("(:goal\n")
        self.pddl_lines.append("  (and\n  ;; depth 0, initial mapping\n")

        for lqubit in self.lqubits:
            self.pddl_lines.append("  (occupied_lqubit " + str(lqubit) + ")\n")
            self.num_actions += 1

        self.pddl_lines.append("  ;; listing negated required cnots\n")
        for cx_gate in self.list_cx_gates:
            self.pddl_lines.append(
                " (not (rcnot "
                + "l"
                + str(cx_gate[0])
                + " "
                + "l"
                + str(cx_gate[1])
                + " "
                + "d"
                + str(cx_gate[2])
                + "))\n"
            )
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
        for line in self.pddl_lines:
            f.write(line)
        f.close()
