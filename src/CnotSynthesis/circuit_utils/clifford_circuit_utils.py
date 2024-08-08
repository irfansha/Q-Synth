# Irfansha Shaik, Aarhus, 15 January 2024.

from qiskit import QuantumCircuit
from src.LayoutSynthesis.circuit_utils import gate_get_qubit

# Print the actions from the plan
def extract_circuit(plan, t, options, num_qubits):
    qubit_map = {}
    if ("swaps" in options.encoding):
       for i in range(num_qubits):
          qubit_map[i] = i
    opt_circuit = QuantumCircuit(num_qubits)
    for k in range(1,t+1):
        cur_action = plan[k-1]
        # handling weight cnot dummy aciton:
        if (cur_action[0] == "unblock"):
          assert(options.cnot_minimization == 'weighted')
          continue
        qubit1 = int(cur_action[1][1:])
        if (cur_action[0] == "cnot"):
          qubit2 = int(cur_action[2][1:])
          opt_circuit.cx(qubit1,qubit2)
        elif(cur_action[0] == "s-gate"):
          opt_circuit.s(qubit1)
        elif(cur_action[0] == "sdg-gate"):
          opt_circuit.sdg(qubit1)
        elif(cur_action[0] == "sx-gate"):
          opt_circuit.sx(qubit1)
        elif(cur_action[0] == "sxdg-gate"):
          opt_circuit.sxdg(qubit1)
        elif(cur_action[0] == "h-gate"):
          opt_circuit.h(qubit1)
        elif(cur_action[0] == "z-gate"):
          opt_circuit.z(qubit1)
        elif(cur_action[0] == "y-gate"):
          opt_circuit.y(qubit1)
        elif(cur_action[0] == "x-gate"):
          opt_circuit.x(qubit1)
        elif(cur_action[0] == "map-final"):
          qubit2 = int(cur_action[2][1:])
          qubit_map[qubit2] = qubit1
        elif(cur_action[0] == "swap"):
          qubit2 = int(cur_action[2][1:])
          if (options.qubit_permute):
            opt_circuit.swap(qubit1, qubit2)
          else:
            cur_logical_qubit1 = qubit_map[qubit1]
            cur_logical_qubit2 = qubit_map[qubit2]
            # swapping:
            qubit_map[qubit1] = cur_logical_qubit2
            qubit_map[qubit2] = cur_logical_qubit1
        else:
          assert(cur_action[0] == "map-initial")
          row = int(cur_action[1][1:])
          qubit1 = int(cur_action[3][1:])
          qubit_map[qubit1] = row
        

    return opt_circuit, qubit_map

# Return a copy of the mapped circuit including measurements
def get_measured_circuit(circuit, qubit_map):
    circuit_copy = circuit.copy()
    circuit_copy.measure_all()
    for i in range(len(qubit_map.items())):
      del circuit_copy.data[-1]
    #print(circuit_copy)
    for (q1, q2) in qubit_map.items():
      circuit_copy.measure([q2],[q1])
    return circuit_copy

# compute circuit cost:
def compute_cost(qc):
   num_gates = qc.size()
   num_2q_gates = 0
   num_cx_gates = 0
   cost = 0
   # counting number of cx gates:
   # for each cx gate, we give 20 cost:
   if ("cx" in qc.count_ops().keys()):
     num_2q_gates += qc.count_ops()['cx']
     num_cx_gates += qc.count_ops()['cx']
   # if a swap exists then we consider it as 3 cx:
   if ("swap" in qc.count_ops()):
     num_2q_gates += qc.count_ops()['swap']
     num_cx_gates += 3*(qc.count_ops()['swap'])
   assert("cz" not in qc.count_ops().keys())

   cost = 20*(num_cx_gates) + 2*(num_gates - num_2q_gates)
   return cost, num_cx_gates

# compute number of cnots (not swaps, only cnots):
def compute_cnot_cost(qc):
   num_cx_gates = 0
   # counting number of cx gates:
   if ("cx" in qc.count_ops().keys()):
     num_cx_gates += qc.count_ops()['cx']
   return num_cx_gates

def compute_and_print_costs(org_circuit, opt_circuit, cnot_minimization=None, verbose=0):
    
    initial_cost, initial_cx_gates = compute_cost(org_circuit)
    if (not cnot_minimization): initial_cost = org_circuit.size()

    if (verbose > 1):
      print("Original Circuit: ")
      print(org_circuit)
      print("Initial CNOT gates: ", initial_cx_gates)
      if (cnot_minimization == 'depth'): print("Initial depth: ", org_circuit.depth())

    final_cost, final_cx_gates = compute_cost(opt_circuit)
    # if cost is not enabled:
    if (not cnot_minimization): final_cost = opt_circuit.size()
    if (verbose > 1):
      print("Optimized Circuit: ")
      print(opt_circuit)
      print("Final CNOT gates: ", final_cx_gates)
      if (cnot_minimization == 'depth'): print("Final depth: ", opt_circuit.depth())
    
    return initial_cost, initial_cx_gates, final_cost, final_cx_gates

def compute_cnot_depth(qc):
  num_qubits = len(qc.qubits)
  cx_circuit = QuantumCircuit(num_qubits)
  for gate in qc:
    if (len(gate.qubits) == 2):
      cx_circuit.append(gate)
  #print(cx_circuit)
  return cx_circuit.depth()

def replace_swaps_with_3cx(circuit, check_equivalence=0, verbose=0):
  num_qubits = len(circuit.qubits)
  swap_free_circuit = QuantumCircuit(num_qubits, num_qubits)
  for gate in circuit:
    if (gate.operation.name == "swap"):
      # decomposing swap to 3 cnots:
      q1, q2 = gate_get_qubit(gate, 0), gate_get_qubit(gate, 1)
      swap_free_circuit.cx(q1,q2)
      swap_free_circuit.cx(q2,q1)
      swap_free_circuit.cx(q1,q2)
    else:
      swap_free_circuit.append(gate)
  # we check if the circuits are equivalent:
  if (check_equivalence):
    from mqt import qcec
    result = qcec.verify(circuit, swap_free_circuit)
    assert result.equivalence == qcec.pyqcec.EquivalenceCriterion.equivalent, "Error, QCEC equivalence check failed"
    #print("Decomposed swap to cnots circuit is equivalent")
  return swap_free_circuit

# we convert swap to 3 cnots and compute the depth:
def compute_depth_swaps_as_3cx(circuit, check_equivalence=0, verbose=0):
  swap_free_circuit = replace_swaps_with_3cx(circuit, check_equivalence, verbose)
  return swap_free_circuit.depth()

# we convert swap to 3 cnots and compute the cnot-depth:
def compute_cnotdepth_swaps_as_3cx(circuit, check_equivalence=0, verbose=0):
  swap_free_circuit = replace_swaps_with_3cx(circuit, check_equivalence, verbose)
  return compute_cnot_depth(swap_free_circuit)

def compute_and_print_costs(org_circuit, opt_circuit, cnot_minimization=None, verbose=0):
    
    initial_cost, initial_cx_gates = compute_cost(org_circuit)
    if (not cnot_minimization): initial_cost = org_circuit.size()

    if (verbose > 1):
      print("Original Circuit: ")
      print(org_circuit)
      print("Initial cost: ", initial_cost)
      print("Initial CNOT gates: ", initial_cx_gates)
      if (cnot_minimization == 'depth'): print("Initial depth: ", org_circuit.depth())

    final_cost, final_cx_gates = compute_cost(opt_circuit)
    # if cost is not enabled:
    if (not cnot_minimization): final_cost = opt_circuit.size()
    if (verbose > 1):
      print("Optimized Circuit: ")
      print(opt_circuit)
      print("Final cost: ", final_cost)
      print("Final CNOT gates: ", final_cx_gates)
      if (cnot_minimization == 'depth'): print("Final depth: ", opt_circuit.depth())
    
    return initial_cost, initial_cx_gates, final_cost, final_cx_gates

# add measurements for both circuits and check equivalence:
def equivalence_check_measureall(circuit, opt_circuit, verbose=0):
    # equivalence check with the original circuit:
    if verbose > 1: print("================== Checking Equivalence ==================")
    # Measuring original circuit:
    org_circuit_copy = circuit.copy()
    org_circuit_copy.measure_all()
    measured_opt_circuit = opt_circuit.copy()
    measured_opt_circuit.measure_all()
    # checking equivalence:
    from mqt import qcec
    result = qcec.verify(org_circuit_copy, measured_opt_circuit)
    assert result.equivalence == qcec.pyqcec.EquivalenceCriterion.equivalent, "Error, QCEC equivalence check failed"
    if verbose > 0: print("Optimized circuit is equivalent to the original circuit")