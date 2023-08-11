# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumRegister
from qiskit.circuit import Qubit

# Return logical qubit bit_idx of gate gate_idx
# TODO: find the proper way to do this using find_bit
def gate_get_qubit(gate,bit_idx):
    return gate.qubits[bit_idx].index

# Return a new gate with a modified qubit
# TODO: find the proper way to do this
def gate_set_qubit(gate, bit_idx, num_qubits):
  newgate = gate.copy()
  newgate.qubits = (Qubit(QuantumRegister(num_qubits, 'q'), bit_idx),)
  return newgate

# return a list of all CNOT gates
def all_cx_gates(circuit):
  list_cx_gates = []
  for gate_idx in range(len(circuit)):
    if (circuit[gate_idx].operation.name == "cx"):
      list_cx_gates.append(gate_idx)
  return list_cx_gates

# compute and return strict dependencies between CNOT gates (according to standard DAG)
def strict_dependencies(circuit, debug=0):
  # for each logical qubit, we maintain the current dependency
  current_dependency = {}
  for cur_lqubit in range(len(circuit.qubits)):
    current_dependency[cur_lqubit] = []

  if (debug > 2):
    print("Analyzing strict dependencies one by one:")
    print("==============================================")

  # using the current dependencies, we create a dependency map:
  cnot_depends = {}
  for gate_idx in range(len(circuit)):
    gate = circuit[gate_idx]
    if (len(gate.qubits) == 2):
      # for now asserting every 2 qubit operation is "cx":
      if gate.operation.name != "cx":
        print(f"Error: currently, Q-Synth assumes CNOT is the only binary operators, found '{gate.operation.name}'")
        exit(-1)
      ctrl = gate_get_qubit(gate,0)
      data = gate_get_qubit(gate,1)
      # first gathering current dependency:
      cnot_depends[gate_idx] = (current_dependency[ctrl], current_dependency[data])
      # updating current dependency on both input qubits:
      current_dependency[ctrl] = [gate_idx]
      current_dependency[data] = [gate_idx]
      if (debug > 2):
        print(f"CX gate {gate_idx} depends on:", current_dependency[ctrl], current_dependency[data])
    else:
      if len(gate.qubits) != 1:
        print(f"Error: can only handle unary gates and CX gates. Found {gate.operation.name} on {len(gate.qubits)} qubits")
        exit(-1)
  if (debug > 2):
    print("=========================================")
  return cnot_depends
