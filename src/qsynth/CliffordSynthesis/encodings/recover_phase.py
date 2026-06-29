# Irfansha Shaik, 21.11.2024, Aarhus
from qiskit.quantum_info import Clifford
from operator import xor


def recover_phase(
    optimal_phase: Clifford.phase, goal_phase: Clifford.phase, num_qubits: int
) -> list[tuple[str, str]]:
    phase_gates = []
    for i in range(num_qubits):
        apply_x, apply_z = False, False
        if xor(optimal_phase[i], goal_phase[i]):
            apply_z = True # z gate from destabilizer
        if xor(optimal_phase[i + num_qubits], goal_phase[i + num_qubits]):
            apply_x = True # x gate from stabilizer
        if apply_x and apply_z:
            phase_gates.append(("y-gate", "q" + str(i)))
        elif apply_x:
            phase_gates.append(("x-gate", "q" + str(i)))
        elif apply_z:
            phase_gates.append(("z-gate", "q" + str(i)))
    return phase_gates