import random

from qiskit import QuantumCircuit

from qsynth.ReachabilitySolver.encodings.layout_synthesis.layout_reachability_synthesis import \
    get_coupling_graph_from_platform

from qsynth.CliffordSynthesis.circuit_utils import (
    compute_cnotdepth_swaps_as_3cx, compute_cnot_depth, compute_depth_swaps_as_3cx,
)

CIRCUITS_DIR = "Benchmarks/SAT-24"
EXAMPLES_DIR = "Benchmarks/Examples"
ECAI_DIR = "Benchmarks/ECAI-24"


def get_cx_depth_swaps_as_3cx(circuit: QuantumCircuit) -> int:
    return compute_cnotdepth_swaps_as_3cx(circuit)

def get_depth_swaps_as_3cx(circuit: QuantumCircuit) -> int:
    return compute_depth_swaps_as_3cx(circuit)

def get_cx_depth(circuit: QuantumCircuit) -> int:
    return compute_cnot_depth(circuit)

def get_depth(circuit: QuantumCircuit) -> int:
    return circuit.remove_final_measurements(inplace=False).depth()

def count_depth_cx_depth(circuit: QuantumCircuit) -> tuple[int, int]:
    depth = get_depth(circuit)
    cx_depth = get_cx_depth(circuit)
    return depth, cx_depth


def get_swap_count(circuit: QuantumCircuit) -> int:
    return circuit.count_ops().get("swap", 0)


def get_cx_count(circuit: QuantumCircuit) -> int:
    return circuit.count_ops().get("cx", 0)


def get_cx_count_swaps_as_3_cx(circuit: QuantumCircuit) -> int:
    return circuit.count_ops().get("cx", 0) + 3 * circuit.count_ops().get("swap", 0)


def count_swaps_cx(circuit: QuantumCircuit) -> tuple[int, int]:
    return get_swap_count(circuit), get_cx_count(circuit)


def get_rz_count(circuit: QuantumCircuit) -> int:
    counts = circuit.count_ops()
    total_count = 0
    total_count += counts.get("rz", 0)
    total_count += counts.get("z", 0)
    total_count += counts.get("t", 0)
    total_count += counts.get("tdg", 0)
    total_count += counts.get("s", 0)
    total_count += counts.get("sdg", 0)

    return total_count


def get_1_qubit_gate_count(circuit: QuantumCircuit) -> int:
    return sum(1 for instr in circuit.data if len(instr.qubits) == 1)


def get_h_s_sx_count(circuit: QuantumCircuit) -> int:
    counts = circuit.count_ops()
    total = 0
    total += counts.get("h", 0)
    total += counts.get("s", 0)
    total += counts.get("sx", 0)
    return total


def generate_random_cnot_circuit(number_of_qubits, platform=None, number_of_gates=None):
    """
    Generates a random CNOT circuit with the specified number of qubits.
    If not specified, the number of CNOT gates is 10 times the number of qubits.
    """
    circuit = QuantumCircuit(number_of_qubits)
    if platform is None:
        # Let coupling graph include all qubit pairs
        coupling_graph = [[qi, qj] for qi in range(circuit.num_qubits)
                               for qj in range(circuit.num_qubits) if qi != qj]
    else:
        coupling_graph, _ = get_coupling_graph_from_platform(platform)

    for _ in range(10 * number_of_qubits):
        # Choose distinct ctrl and trg qubits
        ctrl = random.randint(0, number_of_qubits - 1)
        trg = ctrl
        while [ctrl, trg] not in coupling_graph:
            trg = random.randint(0, number_of_qubits - 1)
        # Apply gate
        circuit.cx(ctrl, trg)

    return circuit
