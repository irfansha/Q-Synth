# Irfansha Shaik, Aarhus, 05 January 2023.

from qiskit import QuantumCircuit
from src.PeepholeSlicing.circuit_slice import CircuitSlice as cs
from src.LayoutSynthesis.circuit_utils import gate_get_qubit, gate_set_qubit
from src.CnotSynthesis.circuit_utils.clifford_circuit_utils import get_measured_circuit

# we initialize a Quantum circuit for a given number of qubits
# we only initialize classical bits if allowed:
def initialize_circuit(num_qubits, clbits=None):
  if (clbits): circuit = QuantumCircuit(num_qubits,num_qubits)
  else:        circuit = QuantumCircuit(num_qubits)
  return circuit

# If measurements are present at the end, we generate measurementless circuit and circuit with only measurements:
def separate_measurements(circuit, num_qubits, clbits):
    circuit_measurements = None
    barrier_flag = False
    for gate in circuit:
      if gate.operation.name == "barrier":
        barrier_flag =  True
        # Initialize empty circuit:
        circuit_measurements = initialize_circuit(num_qubits, clbits)
      if barrier_flag: circuit_measurements.append(gate)
    # measurementless circuit:
    circuit.remove_final_measurements()
    return circuit, circuit_measurements

def equivalence_check_with_map(org_circuit, opt_circuit, qubit_map, verbose=False):
    # Measuring original circuit:
    org_circuit_copy = org_circuit.copy()
    org_circuit_copy.measure_all() 
    if (verbose > 1): print(org_circuit_copy)
    measured_circuit = get_measured_circuit(opt_circuit, qubit_map)
    if (verbose > 1): print(measured_circuit)
    # checking equivalence:
    from mqt import qcec
    result = qcec.verify(org_circuit_copy, measured_circuit)
    assert result.equivalence == qcec.pyqcec.EquivalenceCriterion.equivalent, "Error, QCEC equivalence check failed"
    if (verbose > -1): print("Optimized circuit is equivalent to the original circuit")

# given a cnot circuit with zero cost swaps, we remove the swaps
# we assume there are no measurements:
def remove_zero_cost_swaps(circuit, num_qubits):
  no_swaps_circuit = QuantumCircuit(num_qubits)
  # default initial mapping:
  mapping = {}
  for i in range(num_qubits):
    mapping[i] = i

  for gate in circuit:
    if (gate.operation.name == "swap"):
      q1 = gate_get_qubit(gate, 0)
      q2 = gate_get_qubit(gate, 1)

      tmp = mapping[q1]
      mapping[q1] = mapping[q2]
      mapping[q2] = tmp
    elif(gate.operation.name == "cx"):
      q1 = gate_get_qubit(gate, 0)
      q2 = gate_get_qubit(gate, 1)
      # we update the qubit in the gate:
      newq1 = mapping[q1]
      newq2 = mapping[q2]
      no_swaps_circuit.cx(newq1, newq2)
    else:
      # we update the qubit in the gate:
      assert len(gate.qubits) == 1
      q = gate_get_qubit(gate, 0)
      newq = mapping[q]
      newgate = gate_set_qubit(gate, newq, num_qubits)
      no_swaps_circuit.append(newgate)
  return no_swaps_circuit, mapping

class CircuitUtils:

  def gate_get_qubit(self, gate, bit_idx):
    return gate.qubits[bit_idx].index

  def extract_top_slice(self, allowed_gates):
    #print("Top slice extraction")

    top_slice = initialize_circuit(self.num_qubits, self.clbits)
    buffer_circuit = initialize_circuit(self.num_qubits, self.clbits)

    # in the starting all the qubits are free (not blocked):
    blocked = []

    while(True):
      # TODO: check the edge case when the circuit is at the end:
      if (len(self.circuit) == 0 or len(blocked) == self.num_qubits):
        # all the qubits are blocked:
        # we stop and copy rest of the gates to remaining_circuit:
        remaining_circuit = buffer_circuit.compose(self.circuit)
        break
      top_gate = self.circuit.data[0]
      del self.circuit.data[0]
      # if single qubit:
      if (len(top_gate.qubits) == 1):
        qubit = self.gate_get_qubit(top_gate,0)
        # only if the qubit is not blocked then 
        if (qubit not in blocked):
          if (top_gate.operation.name in allowed_gates):
            top_slice.append(top_gate)
          else:
            blocked.append(qubit)
            buffer_circuit.append(top_gate)
        else:
          buffer_circuit.append(top_gate)
      elif (len(top_gate.qubits) == 2):
        # we assume that only clifford 2 qubit gates are present in the input circuit:
        assert(top_gate.operation.name in self.clifford_gates)
        qubit1 = self.gate_get_qubit(top_gate,0)
        qubit2 = self.gate_get_qubit(top_gate,1)

        #print(qubit1, qubit2, blocked)

        if ((qubit1 in blocked or qubit2 in blocked) or top_gate.operation.name not in allowed_gates):
          # 2-qubit gate does not belong to the same block:
          # we block both the qubits:
          if (qubit1 not in blocked):
            blocked.append(qubit1)
          if (qubit2 not in blocked):
            blocked.append(qubit2)
          
          buffer_circuit.append(top_gate)
        else:
          # only when both qubits are not blocked and the operation is allowed i.e., in clifford slice, we add to top slice:
          top_slice.append(top_gate)
    #print(top_slice)
    #print(remaining_circuit)
    return top_slice, remaining_circuit

  def extract_all_gates(self):
    self.all_gates_list = []
    self.non_optimization_slice_gates = []
    for gate in self.circuit:
      if (gate.operation.name not in self.all_gates_list):
        self.all_gates_list.append(gate.operation.name)
      if (gate.operation.name not in self.non_optimization_slice_gates and gate.operation.name not in self.optimization_slice_gates):
        self.non_optimization_slice_gates.append(gate.operation.name)
    

  # Parses domain and problem file:
  def __init__(self, circuit, slice_type, check_equivalence):
    self.circuit = circuit
    # if we have classical bits in original circuit, then we use it in the optimized circuit:
    if (len(self.circuit.clbits) == 0): self.clbits = None
    else:                               self.clbits = True
    org_circuit_copy = circuit.copy()
    self.num_qubits = len(self.circuit.qubits)
    self.circuit, self.circuit_measurements = separate_measurements(self.circuit, self.num_qubits, self.clbits)
    self.measurementless_circuit = self.circuit.copy()
    # NOTE: we assume that if a clifford gate is added it is one of the following gate:
    self.clifford_gates = ['x', 'y', 'z', 'cx','h', 's', 'sdg','x', 'sx', 'sxdg', 'swap', 'cz']
    # for now, we only look at cnot and swap gates:
    self.cnot_gates = ['cx','swap']

    # we chose slice gates based on the slice type:
    if (slice_type == 'cnot'):
      self.optimization_slice_gates = list(self.cnot_gates)
    else:
      assert(slice_type == 'clifford')
      self.optimization_slice_gates = list(self.clifford_gates)

    # We extract non-clifford gates in the current circuit:
    self.extract_all_gates()

    #print(self.all_gates_list)
    #print(self.non_optimization_slice_gates)

    self.slices = []

    while(len(self.circuit) != 0):
      slice = cs()

      # we extract clifford part first:
      slice.optimization_slice, self.circuit = self.extract_top_slice(self.optimization_slice_gates)
      slice.non_optimization_slice, self.circuit = self.extract_top_slice(self.non_optimization_slice_gates)

      #print(slice.optimization_slice)
      #print(slice.non_optimization_slice)

      self.slices.append(slice)

    # Test if the slices are same as the original circuit:
    sliced_circuit = initialize_circuit(self.num_qubits, self.clbits)

    for slice in self.slices:
      sliced_circuit = sliced_circuit.compose(slice.optimization_slice)
      sliced_circuit = sliced_circuit.compose(slice.non_optimization_slice)
    
    measured_sliced_circuit = sliced_circuit.copy()
    # if measurements are not present, we measure all:
    if (self.circuit_measurements == None):
      measured_sliced_circuit.measure_all()
      org_circuit_copy.measure_all()
    else:
      measured_sliced_circuit = measured_sliced_circuit.compose(self.circuit_measurements)

    # checking equivalence:
    if check_equivalence:
      from mqt import qcec
      result = qcec.verify(org_circuit_copy, measured_sliced_circuit)
      print(result.equivalence)
      assert result.equivalence == qcec.pyqcec.EquivalenceCriterion.equivalent, "Error, QCEC equivalence check failed"