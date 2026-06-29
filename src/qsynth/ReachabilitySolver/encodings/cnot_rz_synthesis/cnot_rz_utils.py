import numpy as np
from qiskit import QuantumCircuit

from qsynth.ReachabilitySolver.framework.variable import Variable


def remove_gates_by_name(circuit, gate_name):
    """
    Returns a copy of the input circuit but with all 'gate_name' gates removed.
    """
    new_circ = QuantumCircuit(*circuit.qregs, *circuit.cregs)

    for instr, qargs, cargs in circuit.data:
        if instr.name != gate_name:
            new_circ.append(instr, qargs, cargs)

    return new_circ


def get_circuit_converted_to_cnot_rz(circuit):
    """
    Takes a circuit with all gates in { CNOT, Rz, SWAP, Z, T, S, Tdg, Sdg } and returns an equivalent CNOT+Rz circuit.
    """
    new_qc = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)

    for instr, qargs, cargs in circuit.data:
        name = instr.name
        qubits = [circuit.find_bit(q).index for q in qargs]

        if name == "cx":
            new_qc.cx(*qubits)
        elif name == "swap":
            new_qc.swap(*qubits)
        elif name == "rz":
            theta = instr.params[0]
            new_qc.rz(theta, qubits[0])
        elif name == "z":
            new_qc.rz(np.pi, qubits[0])
        elif name == "s":
            new_qc.rz(np.pi / 2, qubits[0])
        elif name == "sdg":
            new_qc.rz(-np.pi / 2, qubits[0])
        elif name == "t":
            new_qc.rz(np.pi / 4, qubits[0])
        elif name == "tdg":
            new_qc.rz(-np.pi / 4, qubits[0])
        else:
            raise ValueError(f"Unsupported gate: {name}")
    return new_qc


def get_cnot_rz_circuit_converted_to_z_t_tdg_s_sdg(circuit):
    new_qc = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)

    for instr, qargs, cargs in circuit.data:
        name = instr.name
        qubits = [circuit.find_bit(q).index for q in qargs]

        if name == "cx":
            new_qc.cx(*qubits)
        elif name == "swap":
            new_qc.swap(*qubits)
        elif name == "rz":
            theta = instr.params[0] % (2 * np.pi)
            if np.isclose(theta, np.pi):
                new_qc.z(*qubits)
            elif np.isclose(theta, np.pi / 2):
                new_qc.s(*qubits)
            elif np.isclose(theta, 3 * np.pi / 2):
                new_qc.sdg(*qubits)
            elif np.isclose(theta, np.pi / 4):
                new_qc.t(*qubits)
            elif np.isclose(theta, 7 * np.pi / 4):
                new_qc.tdg(*qubits)
            else:
                new_qc.rz(theta, qubits[0])
        else:
            raise ValueError(f"Unsupported gate: {name}")
    return new_qc



def get_goal_matrix_and_phase_polynomial_from_cnot_rz_circuit(circuit):
    """
    Returns:
        goal_matrix as a numpy array
        phase_polynomial as a dictionary from state vectors (tuples of ints) to phases (modulo 2π)
    """
    circuit = get_circuit_converted_to_cnot_rz(circuit)
    goal_matrix = np.eye(circuit.num_qubits, dtype=int)
    phase_polynomial = {}

    for instr in circuit.data:
        if instr.name == "cx":
            ctrl, trg = [circuit.find_bit(q).index for q in instr.qubits]
            goal_matrix[:, trg] = (goal_matrix[:, trg] + goal_matrix[:, ctrl]) % 2
        elif instr.name == "swap":
            i, j = [circuit.find_bit(q).index for q in instr.qubits]
            goal_matrix[:, [i, j]] = goal_matrix[:, [j, i]]
        elif instr.name == "rz":
            theta = instr.params[0]
            q = circuit.find_bit(instr.qubits[0]).index
            state_vector = tuple(goal_matrix[:, q])
            old_coeff = phase_polynomial.get(state_vector, 0)
            phase_polynomial[state_vector] = old_coeff + theta
        else:
            raise ValueError(f"Unsupported gate: {instr.name}")

        # Simplify phase polynomial by taking coefficients modulo 2π and leaving out coefficients of 0
        phase_polynomial = {
            k: (v % (2 * np.pi))
            for k, v in phase_polynomial.items()
            if not np.isclose(v % (2 * np.pi), 0)
        }
    return goal_matrix, phase_polynomial


def check_equivalence_of_cnot_rz_circuits(circuit1, circuit2):
    """
    Checks equivalence of the parity matrix and phase polynomial of the two circuits.
    """
    def dicts_close(d1, d2):
        if d1.keys() != d2.keys():
            return False
        return all(np.isclose(d1[k], d2[k]) for k in d1)

    goal_matrix1, phase_polynomial1 = get_goal_matrix_and_phase_polynomial_from_cnot_rz_circuit(circuit1)
    goal_matrix2, phase_polynomial2 = get_goal_matrix_and_phase_polynomial_from_cnot_rz_circuit(circuit2)
    assert np.all(goal_matrix1 == goal_matrix2), f"Goal matrix\n{goal_matrix1}\nis different from goal matrix\n{goal_matrix2}"
    assert dicts_close(phase_polynomial1, phase_polynomial2), f"Phase polynomial\n{phase_polynomial1}\nis different from phase polynomial\n{phase_polynomial2}"


def get_rz_sequence_from_action_sequence(action_sequence):
    """
    Given an action sequence, compute a list of lists of Rz gates as (rz_index, qubit) tuples for each time step.
    The action_sequence should be a list of the true action variables at each time step.
    """
    rz_sequence = []
    applied_rotations = set()
    for action_vars in action_sequence:
        rz_gates = []
        for var in action_vars:
            if var.name != "ar":
                continue
            rotation_index, qubit = var.params
            if rotation_index in applied_rotations:
                continue
            rz_gates.append((rotation_index, qubit))
            applied_rotations.add(rotation_index)
        rz_sequence.append(rz_gates)
    return rz_sequence



def ar(r, q, t):
    return Variable(name="ar", params=[r, q], time_step=t)

def e(r, t):
    return Variable(name="e", params=[r], time_step=t)