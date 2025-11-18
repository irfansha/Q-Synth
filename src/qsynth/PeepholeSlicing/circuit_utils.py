# Irfansha Shaik, Aarhus, 05 January 2023.

from qiskit import QuantumCircuit
from qiskit.circuit import Gate
from qsynth.PeepholeSlicing.circuit_slice import CircuitSlice as cs
from qsynth.LayoutSynthesis.circuit_utils import (
    gate_get_qubit,
    gate_set_qubits,
    gate_set_qubit,
)
from qsynth.Utilities.slices import get_slices
import numpy


# we initialize a Quantum circuit for a given number of qubits
# we only initialize classical bits if allowed:
def initialize_circuit(num_qubits, clbits=None):
    if clbits:
        circuit = QuantumCircuit(num_qubits, num_qubits)
    else:
        circuit = QuantumCircuit(num_qubits)
    return circuit


# If measurements are present at the end, we generate measurementless circuit and circuit with only measurements:
def separate_measurements(circuit, num_qubits, clbits):
    circuit_measurements = None
    barrier_flag = False
    for gate in circuit:
        if gate.operation.name == "barrier":
            barrier_flag = True
            # Initialize empty circuit:
            circuit_measurements = initialize_circuit(num_qubits, clbits)
        if barrier_flag:
            circuit_measurements.append(gate)
    # measurementless circuit:
    circuit.remove_final_measurements()
    return circuit, circuit_measurements


def equivalence_check_with_map(org_circuit, opt_circuit, qubit_map, verbose=False):
    if verbose > 0:
        print("Currently, equivalence checking is not supported")


# given a cnot circuit with zero cost swaps, we remove the swaps
# we assume there are no measurements:
def remove_zero_cost_swaps(circuit, num_qubits):
    no_swaps_circuit = QuantumCircuit(num_qubits)
    # default initial mapping:
    mapping = {}
    for i in range(num_qubits):
        mapping[i] = i

    for gate in circuit:
        if gate.operation.name == "swap":
            q1 = gate_get_qubit(gate, 0)
            q2 = gate_get_qubit(gate, 1)

            tmp = mapping[q1]
            mapping[q1] = mapping[q2]
            mapping[q2] = tmp
        elif gate.operation.name == "cx":
            q1 = gate_get_qubit(gate, 0)
            q2 = gate_get_qubit(gate, 1)
            # we update the qubit in the gate:
            newq1 = mapping[q1]
            newq2 = mapping[q2]
            no_swaps_circuit.cx(newq1, newq2)
        elif len(gate.qubits) == 1:
            # we update the qubit in the gate:
            q = gate_get_qubit(gate, 0)
            newq = mapping[q]
            newgate = gate_set_qubit(gate, newq, num_qubits)
            no_swaps_circuit.append(newgate)
        else:
            # we update the qubit in the gate:
            assert len(gate.qubits) == 2
            q0 = gate_get_qubit(gate, 0)
            q1 = gate_get_qubit(gate, 1)
            newgate = gate_set_qubits(gate, mapping[q0], mapping[q1], num_qubits)
            no_swaps_circuit.append(newgate)

    return no_swaps_circuit, mapping


def is_multiple_of_piby2(param: float) -> bool:
    return ((param * 2) / numpy.pi).is_integer()


def is_cnot(gate: Gate) -> bool:
    return gate.operation.name in ["cx", "swap"]


def is_clifford(gate: Gate) -> bool:
    clifford_gates = [
        "x",
        "y",
        "z",
        "cx",
        "h",
        "s",
        "sdg",
        "x",
        "sx",
        "sxdg",
        "swap",
        "cz",
        "cy",
    ]
    if gate.operation.name in clifford_gates:
        return True
    elif gate.operation.name in ["u", "u1", "u2", "u3", "rx", "ry", "rz"]:
        is_clifford_gate = True
        for param in gate.params:
            # check if param is a multiple of pi/2:
            if not is_multiple_of_piby2(param=param):
                return False
        return True
    else:
        return False


def project_circuit(
    circuit: QuantumCircuit, qubit_map: dict, num_qubits: int
) -> QuantumCircuit:
    projected_circuit = QuantumCircuit(num_qubits)
    for gate in circuit:
        if len(gate.qubits) == 1:
            # we update the qubit in the gate:
            q = gate_get_qubit(gate, 0)
            newgate = gate_set_qubit(gate, qubit_map[q], num_qubits)
        else:
            # we update the qubit in the gate:
            assert len(gate.qubits) == 2
            q0 = gate_get_qubit(gate, 0)
            q1 = gate_get_qubit(gate, 1)
            newgate = gate_set_qubits(gate, qubit_map[q0], qubit_map[q1], num_qubits)
        projected_circuit.append(newgate)
    return projected_circuit


def project_coupling_graph(coupling_map: list[list], qubit_map: dict) -> list[list]:
    projected_coupling_graph = []
    for [x0, x1] in coupling_map:
        if x0 in qubit_map and x1 in qubit_map:
            projected_coupling_graph.append([qubit_map[x0], qubit_map[x1]])
    return projected_coupling_graph


class CircuitUtils:
    def gate_get_qubit(self, gate, bit_idx):
        return gate.qubits[bit_idx]._index

    def compute_unused_qubits(self):
        for slice in self.slices:
            used_qubits = set()
            for gate in slice.optimization_slice:
                # qubit1
                used_qubits.add(gate_get_qubit(gate, 0))
                if len(gate.qubits) == 2:
                    # qubit2
                    used_qubits.add(gate_get_qubit(gate, 1))
            slice.used_qubits_optimization_slice = list(used_qubits)
            # creating map for qubits for projection:
            slice.projection_map = {
                k: v for v, k in enumerate(slice.used_qubits_optimization_slice)
            }
            slice.reverse_projection_map = {
                k: v for k, v in enumerate(slice.used_qubits_optimization_slice)
            }
            for i in range(self.num_qubits):
                if i not in used_qubits:
                    slice.unused_qubits_optimization_slice.append(i)
            # print(used_qubits)

    # Parses domain and problem file:
    def __init__(self, circuit, slice_type, check, verbose=False):
        self.circuit = circuit
        # if we have classical bits in original circuit, then we use it in the optimized circuit:
        if len(self.circuit.clbits) == 0:
            self.clbits = None
        else:
            self.clbits = True
        self.num_qubits = len(self.circuit.qubits)
        self.circuit, self.circuit_measurements = separate_measurements(
            self.circuit, self.num_qubits, self.clbits
        )
        self.measurementless_circuit = self.circuit.copy()
        self.slices = []
        # adding appropriate predicate:
        if slice_type == "cnot":
            is_valid = is_cnot
        else:
            assert slice_type == "clifford"
            is_valid = is_clifford
        current_slice_index = 0
        for non_opt, opt in get_slices(self.circuit, is_valid):
            slice = cs()
            slice.non_optimization_slice = initialize_circuit(
                self.num_qubits, self.clbits
            )
            for i in non_opt:
                slice.non_optimization_slice.append(self.circuit.data[i])
            slice.optimization_slice = initialize_circuit(self.num_qubits, self.clbits)
            for i in opt:
                slice.optimization_slice.append(self.circuit.data[i])
            slice.slice_index = current_slice_index
            current_slice_index = current_slice_index + 1
            self.slices.append(slice)
        self.compute_unused_qubits()
        # checking equivalence:
        if check and verbose > 0:
            print("Currently, equivalence checking is not supported")
