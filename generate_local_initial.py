# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from architecture import platform

class GenerateLocalInitial:

  # Parse and compute cnot gate list with dependencies satisfied:
  def parse_and_compute(self):

    # loading quantum circuit with qiskit:
    input_circuit = QuantumCircuit()
    try:
      self.input_circuit = input_circuit.from_qasm_file(self.args.circuit_in)
    except FileNotFoundError:
      print(f"Error: circuit_in file '{self.args.circuit_in}' not found")
      exit(-1)

    # converting to dag for extracting layers:
    self.input_dag = circuit_to_dag(self.input_circuit)

    self.num_lqubits = len(self.input_circuit.qubits)

    if (self.args.verbose > 0):
      print(self.input_circuit)

    # for each logical qubit, we define a dependency
    # we update with cnots when encountered
    current_dependency = {}

    for cur_lqubit in range(self.num_lqubits):
      current_dependency[cur_lqubit] = "l" + str(cur_lqubit)

    #print(current_dependency)
    # each gate is represented using 3 tuple, (qubit1, qubit2, layer_number)
    self.list_cx_gates = []

    # using current dependency, we create a dependency map:
    self.cnot_depends = {}

    # we remember the single gates with there instruction numbers:
    # we generate a dict with each qubit:
    self.single_qubit_timestep_map = {}

    # initializing with empty list for each qubit:
    for cur_lqubit in range(self.num_lqubits):
      self.single_qubit_timestep_map[cur_lqubit] = []

    for gate_index in range(len(self.input_circuit)):
      gate =  self.input_circuit[gate_index]
      if (self.args.verbose > 1):
        print("Printing instructions one by one:")
        print("instruction number:",gate_index)
      if (len(gate.qubits) == 2):
        #print(gate.qubits[0].index,gate.qubits[1].index, gate_index)
        # for now asserting every 2 qubit operation is "cx":
        assert(gate.operation.name == "cx")
        self.list_cx_gates.append((gate.qubits[0].index,gate.qubits[1].index, gate_index))
        # first gathering current dependency:
        self.cnot_depends[(gate.qubits[0].index,gate.qubits[1].index, gate_index)] = (current_dependency[gate.qubits[0].index],current_dependency[gate.qubits[1].index])
        if (self.args.verbose > 1):
          print(current_dependency[gate.qubits[0].index],current_dependency[gate.qubits[1].index])
        # updating current dependcy on 2 qubits:
        current_dependency[gate.qubits[0].index] = (gate.qubits[0].index,gate.qubits[1].index, gate_index)
        current_dependency[gate.qubits[1].index] = (gate.qubits[0].index,gate.qubits[1].index, gate_index)
      else:
        assert(len(gate.qubits) == 1)
        self.single_qubit_timestep_map[gate.qubits[0].index].append((gate_index,gate))


    if (self.args.verbose > 1):
      print("cnot gates: ",self.list_cx_gates)

      print("cnot_depends dict:")
      for key,value in self.cnot_depends.items():
        print(key,value)

      print("single qubit map:")
      for key, value in self.single_qubit_timestep_map.items():
        print(key,value)

  def generate_domain(self):

    f = open(self.args.pddl_domain_out,"w")
    # requirements and types:    
    f.write("(define (domain Quantum)\n(:requirements :typing)\n(:types pqubit lqubit gateid - object\n")
    # generating objects for logical qubits:
    self.lqubits = []
    for i in range(self.num_lqubits):
      self.lqubits.append("l" + str(i))
    f.write(")\n")
    # constants, this is all gateids i.e., cnots and 
    constant_string = ""
    for cnot in self.list_cx_gates:
      constant_string += "l" +str(cnot[0]) +  "_l" +str(cnot[1]) + "_i" + str(cnot[2]) + " "
    f.write("(:constants "+ constant_string + " - gateid\n")
    f.write(")")

    # predicates:
    f.write("(:predicates    (occupied_pqubit ?p - pqubit)\n\t\t(occupied_lqubit ?l - lqubit)\n\t\t(mapped ?l - lqubit ?p - pqubit)\n\t\t(connected ?p1 - pqubit ?p2 - pqubit)\n\t\t;; required cnot(control_gate,target_gate) at some depth\n\t\t(rcnot ?g - gateid)\n)\n")
    f.write("(:action map_initial\n:parameters (?l - lqubit ?p - pqubit)\n:precondition (and (not (occupied_lqubit ?l)) (not (occupied_pqubit ?p)))\n:effect\t(and (occupied_lqubit ?l) (occupied_pqubit ?p) (mapped ?l ?p))\n)\n")
    # swap action
    f.write("(:action swap\n:parameters (?l1 - lqubit ?l2 - lqubit ?p1 - pqubit ?p2 - pqubit)\n:precondition (and  (mapped ?l1 ?p1) (mapped ?l2 ?p2) (connected ?p1 ?p2))\n:effect       (and (not (mapped ?l1 ?p1)) (not (mapped ?l2 ?p2)) (mapped ?l1 ?p2) (mapped ?l2 ?p1))\n)\n")

    # for each cnot action, we generate a partially grounded local depended actions:
    for key, value in self.cnot_depends.items():
      f.write("(:action apply_cnot_" + "l" +str(key[0]) +  "_l" +str(key[1]) + "_i" + str(key[2]) + "\n:parameters (?p1 - pqubit ?p2 - pqubit)\n")

      precondition_string = ":precondition (and "
      # if string, then the conditions are satisfied by mapped conditions already:
      if (type(value[0]) != str):
        precondition_string += "(not (rcnot " + "l" +str(value[0][0]) +  "_l" +str(value[0][1]) + "_i" + str(value[0][2]) +"))"
      if (type(value[1]) != str):
        precondition_string += " (not (rcnot " + "l" +str(value[1][0]) +  "_l" +str(value[1][1]) + "_i" + str(value[1][2]) +"))"
      
      # preconditions for required cnot:
      precondition_string += " (rcnot l" +str(key[0]) +  "_l" +str(key[1]) + "_i" + str(key[2]) + ")"

      # both qubits must be mapped to the physical qubits:
      precondition_string += " (mapped l" +str(key[0]) + " ?p1)"
      precondition_string += " (mapped l" +str(key[1]) + " ?p2)"
      precondition_string += " (connected ?p1 ?p2)"

      # closing precondition brackets:
      precondition_string += ")\n"

      f.write(precondition_string)
      # effect:
      f.write(":effect (and (not (rcnot l" +str(key[0]) +  "_l" +str(key[1]) + "_i" + str(key[2]) +")))\n)\n")

    # closing the domain file:
    f.write(")\n")

  def set_architecture(self):
    (self.coupling_map, self.num_physical_qubits) \
      = platform(self.args.platform, self.args.bidirectional, self.args.verbose)

  def generate_specification(self):
    # name to be update according to the circuit input files:
    self.pddl_lines.append("(define (problem test)\n")
    # we assume our domain is fixed, Quantum:
    self.pddl_lines.append("  (:domain Quantum)\n")
    self.pddl_lines.append("  (:objects\n")
    self.pddl_lines.append("  ;; logical qubits\n")
    # generating objects for logical qubits:
    self.lqubits = []
    for i in range(self.num_lqubits):
      self.lqubits.append("l" + str(i))
    self.pddl_lines.append("  "+" ".join(self.lqubits) + " - lqubit\n")

    self.pddl_lines.append("  ;; physical qubits\n")
    # generating objects for physical qubits:
    pqubits = []
    for i in range(self.num_physical_qubits):
      pqubits.append("p" + str(i))
    self.pddl_lines.append("  "+" ".join(pqubits) + " - pqubit\n")


    self.pddl_lines.append(")\n")

  def generate_init(self):

    # we alway start we d0 as current depth:
    self.pddl_lines.append("(:init\n  ;; all physical qubits are not occupied, by default\n  ;; all logical qubits are not occupied, by default\n ;; connectivity graph\n")

    # adding coupling/connectivity graph with connected predicates:
    for edge in self.coupling_map:
      self.pddl_lines.append("  (connected " + "p" + str(edge[0]) + " p" + str(edge[1]) + ")\n")

    self.pddl_lines.append("  ;; listing required cnots\n")
    for cx_gate in self.list_cx_gates:
      self.pddl_lines.append("  (rcnot " + "l" + str(cx_gate[0]) + "_" + "l" + str(cx_gate[1]) + "_" + "i" + str(cx_gate[2]) + ")\n")


    self.pddl_lines.append(")\n")

  def generate_goal(self):
    self.pddl_lines.append("(:goal\n")
    self.pddl_lines.append("  (and\n ;; initial mapping\n")

    for lqubit in self.lqubits:
      self.num_actions += 1
      self.pddl_lines.append("  (occupied_lqubit " + str(lqubit) + ")\n")

    self.pddl_lines.append("  ;; listing negated required cnots\n")
    for cx_gate in self.list_cx_gates:
      self.num_actions += 1
      self.pddl_lines.append(" (not (rcnot " + "l" + str(cx_gate[0]) + "_" + "l" + str(cx_gate[1]) + "_" + "i" + str(cx_gate[2]) + "))\n")

    self.pddl_lines.append("  )\n)\n)")

  # Parses domain and problem file:
  def __init__(self, args):
    assert args.model == "local_initial"

    self.args = args

    self.pddl_lines = []
    self.num_actions = 0

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