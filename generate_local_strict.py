# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from circuit_utils import strict_dependencies, all_cx_gates, gate_get_qubit
from architecture import platform

class GenerateLocalStrict:

  # Parse and compute cnot gate list with dependencies satisfied:
  def parse_and_compute(self):

    # loading quantum circuit with qiskit:
    try:
      self.input_circuit = QuantumCircuit.from_qasm_file(self.args.circuit_in)
    except FileNotFoundError:
      print(f"Error: circuit_in file '{self.args.circuit_in}' not found")
      exit(-1)
    self.logical_circuit = self.input_circuit.copy()
    self.num_lqubits = len(self.input_circuit.qubits)
    if (self.args.verbose > 0):
      print(self.input_circuit)

    # computing dependencies
    self.cnot_depends = strict_dependencies(self.logical_circuit, debug=self.args.verbose)

    self.list_cx_gates = all_cx_gates(self.logical_circuit)
    if (self.args.verbose > 2):
      print("cnot gates: ",self.list_cx_gates)

  def generate_domain(self):

    f = open(self.args.pddl_domain_out,"w")
    # requirements and types:    
    f.write("(define (domain Quantum)\n")
    f.write("(:requirements :strips :typing :negative-preconditions)\n")
    f.write("(:types gateid lqubit pqubit - object)\n")
    #f.write(")\n")

    # generating objects for logical qubits:
    lqubits = ""
    for i in range(self.num_lqubits):
      lqubits += f"l{i} "

    # constants, this is all gateids i.e., cnots and logical qubits
    gates = ""
    for cnot in self.list_cx_gates:
      gates += f"g{cnot} "
    f.write(f"(:constants\n")
    f.write(f"\t{gates} - gateid\n")
    f.write("\t;; logical qubits\n")
    f.write(f"\t{lqubits}- lqubit\n")
    f.write(")\n")

    # predicates:
    f.write("(:predicates\n")
    f.write("\t(occupied ?p - pqubit)\n")
    f.write("\t(mapped ?l - lqubit ?p - pqubit)\n")
    f.write("\t(connected ?p1 - pqubit ?p2 - pqubit)\n")
    f.write("\t(done ?g - gateid)\n)\n")

    # swap action
    f.write("(:action swap\n")
    f.write(" :parameters (?l1 ?l2 - lqubit ?p1 ?p2 - pqubit)\n")
    f.write(" :precondition (and (mapped ?l1 ?p1) (mapped ?l2 ?p2) (connected ?p1 ?p2))\n")
    f.write(" :effect (and (not (mapped ?l1 ?p1)) (not (mapped ?l2 ?p2)) (mapped ?l1 ?p2) (mapped ?l2 ?p1))\n)\n")
    if (self.args.ancillary == 1):
      f.write("(:action swap-ancillary1\n")
      f.write(" :parameters (?l1 - lqubit ?p1 ?p2 - pqubit)\n")
      f.write(" :precondition (and (mapped ?l1 ?p1) (not (occupied ?p2)) (connected ?p1 ?p2))\n")
      f.write(" :effect (and (not (mapped ?l1 ?p1)) (not (occupied ?p1)) (mapped ?l1 ?p2) (occupied ?p2))\n)\n")

      f.write("(:action swap-ancillary2\n")
      f.write(" :parameters (?l2 - lqubit ?p1 ?p2 - pqubit)\n")
      f.write(" :precondition (and (mapped ?l2 ?p2) (not (occupied ?p1)) (connected ?p1 ?p2))\n")
      f.write(" :effect (and (not (mapped ?l2 ?p2)) (not (occupied ?p2)) (mapped ?l2 ?p1) (occupied ?p1))\n)\n")

    # for each cnot action, we generate a partially grounded locally dependent action:
    for gate_idx, deps in self.cnot_depends.items():
      ctrl = gate_get_qubit(self.logical_circuit[gate_idx],0)
      data = gate_get_qubit(self.logical_circuit[gate_idx],1)
      ctrl_data = (ctrl, data)

# apply_cnot_gate_gate
      if len(deps[0]) > 0 and len(deps[1]) > 0: # gate_gate
        applycnot = f"apply_cnot_g{gate_idx}"
        f.write(f"(:action {applycnot}\n")
        f.write(":parameters (?p1 ?p2 - pqubit)\n")
        precondition_string = ":precondition (and"
        # if string, then the conditions are satisfied by mapped conditions already:
        for arg in (0,1): # two arguments of this CX key
          assert len(deps[arg]) == 1
          # take care of the dependency
          precondition_string += f" (done g{deps[arg][0]})"
          precondition_string += f" (mapped l{ctrl_data[arg]} ?p{arg+1})"
        
        # fixed preconditions for required cnot:
        precondition_string += f" (not (done g{gate_idx}))"
        precondition_string += " (connected ?p1 ?p2)"
        precondition_string += ")\n"

        f.write(precondition_string)
        effect_string = ""
        # effect: this gate is not required anymore
        effect_string += f":effect (and (done g{gate_idx})"
        effect_string += ")\n)\n"
        f.write(effect_string)

# apply_cnot_input_gate
      if deps[0] == [] and len(deps[1]) == 1:
        applycnot = f"apply_cnot_g{gate_idx}"
        f.write(f"(:action {applycnot}\n")
        f.write(":parameters (?p1 ?p2 - pqubit)\n")
        precondition_string = ":precondition (and"
        # initial mapping, both l and ?p1 are free
        precondition_string += f" (not (occupied ?p1))"
        precondition_string += f" (done g{deps[1][0]})"
        precondition_string += f" (mapped l{data} ?p2)"

        # fixed preconditions for required cnot:
        precondition_string += f" (not (done g{gate_idx}))"
        precondition_string += " (connected ?p1 ?p2)"
        precondition_string += ")\n"

        f.write(precondition_string)
        effect_string = ""
        # effect: this gate is not required anymore
        effect_string += f":effect (and (done g{gate_idx})"
        # effect if there are no dependencies: map initial bits (TODO: only the first of a block!!)
        effect_string += f" (mapped l{ctrl} ?p1) (occupied ?p1)"
        effect_string += ")\n)\n"
        f.write(effect_string)

# apply_cnot_gate_input
      if len(deps[0]) == 1 and deps[1] == []:
        applycnot = f"apply_cnot_g{gate_idx}"
        f.write(f"(:action {applycnot}\n")
        f.write(":parameters (?p1 ?p2 - pqubit)\n")

        # fixed preconditions for required cnot:
        precondition_string = ":precondition (and"
        precondition_string += f" (done g{deps[0][0]})"
        precondition_string += f" (mapped l{ctrl} ?p1)"

        # initial mapping, both l and ?p2 are free
        precondition_string += f" (not (occupied ?p2))"

        # fixed preconditions for required cnot:
        precondition_string += f" (not (done g{gate_idx}))"
        precondition_string += " (connected ?p1 ?p2)"
        precondition_string += ")\n"

        f.write(precondition_string)
        effect_string = ""
        # effect: this gate is not required anymore
        effect_string += f":effect (and (done g{gate_idx})"
        # effect if there are no dependencies: map initial bits (TODO: only the first of a block!!)
        effect_string += f" (mapped l{data} ?p2) (occupied ?p2)"
        effect_string += ")\n)\n"
        f.write(effect_string)

# apply_cnot_input_input
      if deps[0] == [] and deps[1] == []:
        applycnot = f"apply_cnot_g{gate_idx}"
        f.write(f"(:action {applycnot}\n")
        f.write(":parameters (?p1 ?p2 - pqubit)\n")
        precondition_string = ":precondition (and"

        # initial mapping, both l1, l2 and ?p1, ?p2 are free
        precondition_string += f" (not (occupied ?p1))  (not (occupied ?p2))"

        # fixed preconditions for required cnot:
        precondition_string += f" (not (done g{gate_idx}))"
        precondition_string += " (connected ?p1 ?p2)"
        precondition_string += ")\n"

        f.write(precondition_string)
        effect_string = ""
        # effect: this gate is not required anymore
        effect_string += f":effect (and (done g{gate_idx})"
        # effect if there are no dependencies: map initial bits (TODO: only the first of a block!!)
        effect_string += f" (mapped l{ctrl} ?p1) (occupied ?p1) (mapped l{data} ?p2) (occupied ?p2)"
        effect_string += ")\n)\n"
        f.write(effect_string)

    # closing the domain file:
    f.write(")\n")

  def set_architecture(self):

    (self.coupling_map, self.num_physical_qubits) \
      = platform(self.args.platform, self.args.bidirectional, self.args.verbose)

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
    for edge in self.coupling_map:
      self.pddl_lines.append("  (connected " + "p" + str(edge[0]) + " p" + str(edge[1]) + ")\n")

    self.pddl_lines.append(")\n")

  def generate_goal(self):
    self.pddl_lines.append("(:goal\n")
    self.pddl_lines.append("  (and ;; listing all gates to be done\n")
    for cx_gate in self.list_cx_gates:
      self.num_actions += 1
      self.pddl_lines.append(f" (done g{cx_gate})\n")
    self.pddl_lines.append("  )\n)\n)")

  # Parses domain and problem file:
  def __init__(self, args):
    self.args = args

    self.pddl_lines = []
    self.num_actions = 0
    self.initial_map_action_list = {}

    self.parse_and_compute()

    self.generate_domain()

    self.set_architecture()

    self.generate_specification()

    self.generate_init()

    self.generate_goal()

    # writing pddl to file:
    f = open(args.pddl_problem_out,"w")
    for line in self.pddl_lines:
      f.write(line)
    f.close()