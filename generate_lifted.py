# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from circuit_utils import strict_dependencies, all_cx_gates, gate_get_qubit
from architecture import platform

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
    self.logical_circuit = self.input_circuit.copy() # might be pre-optimized later
    if (self.args.verbose > 0):
      print(self.input_circuit)

    self.cnot_depends = strict_dependencies(self.logical_circuit, debug=self.args.verbose)
    
    self.list_cx_gates = all_cx_gates(self.logical_circuit)
    if (self.args.verbose > 2):
      print("cnot gates left:", self.list_cx_gates)

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
    lqubits = ""
    for i in range(self.num_lqubits):
      lqubits += f"l{i} "
    self.pddl_lines.append(f"  {lqubits} - lbit\n")

    # we need logical qubit number of initial map actions in the plan:
    self.num_actions += self.num_lqubits

    self.pddl_lines.append("  ;; physical qubits\n")
    # generating objects for physical qubits:
    pqubits = ""
    for i in range(self.num_physical_qubits):
      pqubits += f"p{i} "
    self.pddl_lines.append(f"  {pqubits} - pbit\n")

    gate_str = "  "
    for cx_gate in self.list_cx_gates:
      gate_str +=  f"g{cx_gate} "
    self.pddl_lines.append(f"{gate_str} - gate)\n")

  def generate_init(self):

    # we alway start we d0 as current depth:
    self.pddl_lines.append("(:init\n")
    self.pddl_lines.append("  ;; no physical qubits are occupied initially\n")
    self.pddl_lines.append("  ;; no logical qubits are mapped initially\n")
    self.pddl_lines.append("  ;; no CNOT gates are done initially\n")
    self.pddl_lines.append("  ;; connectivity graph\n")

    # adding coupling/connectivity graph with connected predicates:
    for edge in self.coupling_map:
      self.pddl_lines.append(f"  (neighbour p{edge[0]} p{edge[1]})\n")

    self.pddl_lines.append("  ;; listing cnots with their logical qubits (and dependencies)\n")
    for cx_gate in self.list_cx_gates:
      ctrl = gate_get_qubit(self.logical_circuit[cx_gate], 0)
      data = gate_get_qubit(self.logical_circuit[cx_gate], 1)
      cur_str = f"  (cnot l{ctrl} l{data} g{cx_gate} "

      x,y = self.cnot_depends[cx_gate]
      #print(x,y)
      if (len(x) == 0):
        cur_str += f"l{ctrl} "
      else:
        assert len(x)==1 # can only handle strict dependencies
        cur_str += f"g{x[0]} "

      if (len(y) == 0):
        cur_str += f"l{data}"
      else:
        assert len(y)==1 # can only handle strict dependencies
        cur_str += f"g{y[0]}"
    
      cur_str += ")\n"
      self.pddl_lines.append(cur_str)
      #print(self.cnot_depends[cx_gate])

    self.pddl_lines.append(")\n")

  def generate_goal(self):
    self.pddl_lines.append("(:goal\n")
    self.pddl_lines.append("  (and\n")
    for cx_gate in self.list_cx_gates:
      self.num_actions += 1
      self.pddl_lines.append(f" (done g{cx_gate})\n")

    self.pddl_lines.append("  )\n)\n)")

  # Parses domain and problem file:
  def __init__(self, args):
    self.args = args

    self.pddl_lines = []
    self.num_actions = 0

    self.parse_and_compute()

    self.set_architecture()

    self.generate_specification()

    self.generate_init()

    self.generate_goal()

    # writing pddl to file:
    f = open(args.pddl_problem_out,"w")
    for line in self.pddl_lines:
      f.write(line)
    f.close()