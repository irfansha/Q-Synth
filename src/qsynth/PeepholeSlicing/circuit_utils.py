# Irfansha Shaik, Aarhus, 05 January 2023.
from mqt import qcec
from qiskit import QuantumCircuit, ClassicalRegister, qasm2, QuantumRegister
from qiskit.circuit import Gate
from qiskit.quantum_info import Clifford, Operator

from qsynth.PeepholeSlicing.circuit_slice import CircuitSlice as cs
from qsynth.LayoutSynthesis.circuit_utils import (
    gate_get_qubit,
    gate_set_qubits,
    gate_set_qubit,
)
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_utils import add_trailing_swaps, \
    get_used_qubits
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


def check_equivalence_of_clifford_circuits(org_circuit: QuantumCircuit,
                                           opt_circuit: QuantumCircuit,
                                           qubit_mapping: dict[int, int],
                                           verbose: int = 0):
    """
    Assumes both input circuits are Clifford circuits. Checks equivalence of Clifford matrices while considering the
    given qubit map from qubits in org_circuit to qubits in opt_circuit.
    Raises:
        AssertionError: if org_circuit is not equal to opt_circuit
    """
    opt_circuit_copy = opt_circuit.copy()
    add_trailing_swaps(opt_circuit_copy, qubit_mapping)
    org_clifford_matrix = Clifford(org_circuit)
    opt_clifford_matrix = Clifford(opt_circuit_copy)
    assert org_clifford_matrix == opt_clifford_matrix, "Optimized circuit is not equivalent to original circuit"
    if verbose > 0:
        print("Optimized circuit is equivalent to the original circuit")


def check_equivalence_of_arbitrary_circuits(org_circuit: QuantumCircuit,
                                           opt_circuit: QuantumCircuit,
                                           final_mapping: dict[int, int],
                                           initial_mapping: dict[int, int] = None,
                                           verbose: int = 0):
    """
    Checks equivalence of org_circuit and opt_circuit with QCEC while considering the given initial and final mappings.
    Raises:
        AssertionError: if org_circuit is not equal to opt_circuit.
    """
    # Strip all classical registers instead of just removing final measurements.
    # remove_final_measurements() leaves orphaned empty registers behind, which
    # causes QCEC to crash when we later add our own measurement register.
    org_circuit = _strip_classical_registers(org_circuit)
    opt_circuit = _strip_classical_registers(opt_circuit)
    org_circuit.measure_all()
    # Measure only qubits mapping to logical qubits
    opt_circuit.add_register(ClassicalRegister(len(final_mapping), name="meas"))
    opt_circuit.barrier(opt_circuit.qubits)
    for logical_qubit, physical_qubit in final_mapping.items():
        opt_circuit.measure(physical_qubit, logical_qubit)

    # If an initial mapping is given, we relabel all qubit inputs according to the mapping
    if initial_mapping is not None:
        # Make initial mapping complete for all used qubits by mapping unmapped qubits to ancilla positions
        initial_mapping_physical_to_logical = { v: k for k, v in initial_mapping.items() }
        used_qubits = get_used_qubits(opt_circuit)
        free_ancilla_index = org_circuit.num_qubits
        for qubit in range(opt_circuit.num_qubits):
            if qubit not in initial_mapping_physical_to_logical and qubit in used_qubits:
                initial_mapping_physical_to_logical[qubit] = free_ancilla_index
                free_ancilla_index += 1
        # Get circuit relabeled according to mapping and with unused qubits removed
        opt_circuit = get_relabeled_quantum_circuit(
            opt_circuit,
            initial_mapping_physical_to_logical
        )

    equivalence_result = qcec.verify(org_circuit, opt_circuit, check_partial_equivalence=True)
    equivalent = equivalence_result.considered_equivalent()
    if not equivalent:
        raise AssertionError("Optimized circuit is not equivalent to original circuit")
    if verbose > 0:
        print("Optimized circuit is equivalent to the original circuit")


def get_relabeled_quantum_circuit(circuit, initial_mapping):
    """
    Relabels all gates according to the initial mapping dictionary. Assumes the initial mapping contains a mapping for
    every used qubit in the circuit. The relabeled circuit will only include the qubits present in the initial_mapping.
    """
    number_of_used_qubits = len(initial_mapping)
    relabeled_circuit = QuantumCircuit(QuantumRegister(number_of_used_qubits), *circuit.cregs)
    for operation, qargs, cargs in circuit.data:
        if operation.name == "barrier":
            relabeled_circuit.barrier()
            continue
        qubits = [circuit.find_bit(q).index for q in qargs]
        classical_bits = [circuit.find_bit(c).index for c in cargs]
        relabeled_qubits = [initial_mapping[q] for q in qubits]
        relabeled_circuit.append(operation, relabeled_qubits, classical_bits)
    return relabeled_circuit


def _strip_classical_registers(circuit: QuantumCircuit) -> QuantumCircuit:
    """
    Returns a new circuit with all classical registers and bits removed,
    keeping only the quantum registers and gates intact.
    """
    # Build a new circuit with only the quantum registers
    new_circuit = QuantumCircuit(*circuit.qregs)
    for instruction in circuit.data:
        # Skip any instruction that references classical bits (e.g. measure, if_else)
        if instruction.clbits:
            continue
        new_circuit.append(instruction)
    return new_circuit


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


def is_cnot_gate(gate: Gate) -> bool:
    return gate.name in ["cx", "swap"]


def is_clifford_gate(gate) -> bool:
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
    if gate.name in clifford_gates:
        return True
    elif gate.name in ["u", "u1", "u2", "u3", "rx", "ry", "rz"]:
        for param in gate.params:
            # check if param is a multiple of pi/2:
            if not is_multiple_of_piby2(param=param):
                return False
        return True
    else:
        return False


def is_cnot_rz_gate(gate) -> bool:
    return gate.name in ["cx", "swap", "rz", "z", "s", "sdg", "t", "tdg"]


def is_clifford_circuit(circuit: QuantumCircuit) -> bool:
    for gate in circuit:
        if not is_clifford_gate(gate):
            return False
    return True


def is_cnot_circuit(circuit: QuantumCircuit) -> bool:
    return all(is_cnot_gate(gate) for gate in circuit)


def is_cnot_rz_circuit(circuit: QuantumCircuit) -> bool:
    return all(is_cnot_rz_gate(gate) for gate in circuit)


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
    def __init__(self, circuit, slice_type):
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
            is_valid = is_cnot_gate
        elif slice_type == "cnot_rz":
            is_valid = is_cnot_rz_gate
        else:
            assert slice_type == "clifford"
            is_valid = is_clifford_gate
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
