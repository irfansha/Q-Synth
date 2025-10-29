# Irfansha Shaik, 21.11.2024, Aarhus
from qiskit.quantum_info import Clifford
from qiskit import QuantumCircuit
from operator import xor


def recover_phase(
    optimal_phase: Clifford.phase, goal_phase: Clifford.phase, num_qubits: int
) -> list((str, str)):

    phase_gates = []
    for i in range(2 * num_qubits):

        if xor(optimal_phase[i], goal_phase[i]):
            # we first add z gates, on destabilizers:
            if i < num_qubits:
                phase_gates.append(("z-gate", "q" + str(i)))
            # we add x gates on stabilizers:
            else:
                phase_gates.append(("x-gate", "q" + str(i - num_qubits)))
    return phase_gates
