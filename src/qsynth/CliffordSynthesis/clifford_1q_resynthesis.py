from qsynth.CliffordSynthesis.rewrite_rules import best_rewrite_rules, best_cx_to_cz_rewrite_rules, state_to_unique_sequences
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Clifford
from qsynth.CliffordSynthesis.encodings.recover_phase import recover_phase
import numpy as np

def add_gate_sequence(circuit: QuantumCircuit, gate_sequence: str, qubit: int) -> None:
    """
    Add a sequence of gates to the quantum circuit on the specified qubit.

    Args:
        circuit (QuantumCircuit): The quantum circuit to which gates will be added.
        gate_sequence (str): The sequence of gates to add (e.g., 'h', 's', 'hs', etc.).
        qubit (int): The index of the qubit to which the gates will be applied.
    """
    if gate_sequence == 'h':
        circuit.h(qubit)
    elif gate_sequence == 's':
        circuit.s(qubit)
    elif gate_sequence == 'hs':
        circuit.h(qubit)
        circuit.s(qubit)
    elif gate_sequence == 'sh':
        circuit.s(qubit)
        circuit.h(qubit)
    elif gate_sequence == 'sx':
        circuit.sx(qubit)
    elif gate_sequence == 'x':
        circuit.x(qubit)
    elif gate_sequence == 'y':
        circuit.y(qubit)
    elif gate_sequence == 'z':
        circuit.z(qubit)
    elif gate_sequence == 'i':
        pass  # Identity gate, do nothing
    else:
        raise ValueError(f"Unsupported gate '{gate_sequence}' in sequence.")

def transpile_circuit_to_hs_pauli_gateset(circuit: QuantumCircuit) -> QuantumCircuit:
    """
    Transpile a given quantum circuit to use only H, S 1q gates.
    Pauli gates are dropped by default.

    Args:
        circuit (QuantumCircuit): The input quantum circuit.
    Returns:
        QuantumCircuit: The transpiled quantum circuit using only H and S gates.
    """
    u3_circuit = transpile(circuit, basis_gates=['u3', 'cx'], optimization_level=0)
    u3_circuit_clifford = Clifford(u3_circuit)
    transpiled_circuit = QuantumCircuit(u3_circuit.num_qubits, u3_circuit.num_clbits)
    for instr, qargs, cargs in u3_circuit.data:
        if instr.name == 'u3':
            theta, phi, lam = instr.params
            temp_circuit = QuantumCircuit(1)
            temp_circuit.u(theta, phi, lam, 0)
            temp_clifford = Clifford(temp_circuit)
            flattened = tuple(temp_clifford.symplectic_matrix.flatten().tolist())
            if flattened in state_to_unique_sequences:
                gate = state_to_unique_sequences[flattened]
                q = qargs[0]._index
                add_gate_sequence(transpiled_circuit, gate, q)
            else:
                raise ValueError(f"U3 gate with parameters ({theta}, {phi}, {lam}) cannot be mapped to H and S gates.")
        else:
            assert instr.name == 'cx'
            transpiled_circuit.cx(qargs[0]._index, qargs[1]._index)
    transpiled_circuit_clifford = Clifford(transpiled_circuit)
    assert u3_circuit_clifford.destab.all() == transpiled_circuit_clifford.destab.all() and u3_circuit_clifford.stab.all() == transpiled_circuit_clifford.stab.all(), "Transpiled circuit does not match original Clifford operation."
    return transpiled_circuit


def compute_flattened_clifford(oneq_gate_sequence: str) -> tuple:
    """
    Compute the flattened Clifford representation for a given one-qubit gate sequence.

    Args:
        oneq_gate_sequence (str): The sequence of one-qubit gates.
    Returns:
        tuple: The flattened Clifford representation as a key.
    """
    qc = QuantumCircuit(1)
    for gate in oneq_gate_sequence:
        if gate == 'i':
            pass
        elif gate == 'h':
            qc.h(0)
        elif gate == 's':
            qc.s(0)
        elif gate == 'hs':
            qc.h(0)
            qc.s(0)
        elif gate == 'sh':
            qc.s(0)
            qc.h(0)
        elif gate == 'sx':
            qc.sx(0)
        else:
            raise ValueError(f"Unsupported gate '{gate}' in sequence.")
    return tuple(Clifford(qc).symplectic_matrix.flatten().tolist())

def clifford_1q_optimization_greedy(circuit: QuantumCircuit, use_cz_gate: bool = False) -> QuantumCircuit:
    """
    Transform a quantum circuit by applying the best rewrite rules greedily.

    Args:
        circuit (QuantumCircuit): The input quantum circuit.

    Returns:
        QuantumCircuit: The transformed quantum circuit.
    """
    # dropping pauli gates first:
    hs_gate_circuit = transpile_circuit_to_hs_pauli_gateset(circuit)
    transformed_circuit = QuantumCircuit(hs_gate_circuit.num_qubits, hs_gate_circuit.num_clbits)
    gate_sequence_per_qubit = dict()
    for qubit in range(hs_gate_circuit.num_qubits):
        gate_sequence_per_qubit[qubit] = []
    for instr, qargs, cargs in hs_gate_circuit.data:
        if instr.name in ['h', 's', 'sx']:
            q = qargs[0]._index
            gate_sequence_per_qubit[q].append(instr.name)
        else:
            assert instr.name == 'cx'
            ctrl = qargs[0]._index
            targ = qargs[1]._index
            # first applying accumulated single qubit gates on control and target qubits
            ctrl_gate_sequence = gate_sequence_per_qubit[ctrl]
            targ_gate_sequence = gate_sequence_per_qubit[targ]
            # build circuit and compute flatten clifford:
            ctrl_qc = compute_flattened_clifford(ctrl_gate_sequence)
            targ_qc = compute_flattened_clifford(targ_gate_sequence)
            oneq_ctrl_gate = state_to_unique_sequences[ctrl_qc]
            oneq_targ_gate = state_to_unique_sequences[targ_qc]
            # applying the best rewrite rule for the cx gate with the given one qubit gates
            if use_cz_gate:
                (rewrite_rule, flip_cnot) = best_cx_to_cz_rewrite_rules[(oneq_ctrl_gate, oneq_targ_gate)]
                assert flip_cnot == 'd', "CZ-based rewrite rules should not flip CNOT direction."
            else:
                (rewrite_rule, flip_cnot) = best_rewrite_rules[(oneq_ctrl_gate, oneq_targ_gate)]
            add_gate_sequence(transformed_circuit, rewrite_rule[0], ctrl)
            add_gate_sequence(transformed_circuit, rewrite_rule[1], targ)
            # adding the cz/cx gate
            if use_cz_gate:
                transformed_circuit.cz(ctrl, targ)
            else:
                if flip_cnot == 'f':
                    transformed_circuit.cx(targ, ctrl)
                else:
                    # dont flip the cnot
                    assert flip_cnot == 'd'
                    transformed_circuit.cx(ctrl, targ)
            # resetting rewrite sequences 1q gates:
            gate_sequence_per_qubit[ctrl] = [rewrite_rule[2]]
            gate_sequence_per_qubit[targ] = [rewrite_rule[3]]
    # finally applying the accumulated single qubit gates on each qubit
    for qubit in range(hs_gate_circuit.num_qubits):
        final_gate_sequence = gate_sequence_per_qubit[qubit]
        final_key = compute_flattened_clifford(final_gate_sequence)
        final_oneq_gate = state_to_unique_sequences[final_key]
        add_gate_sequence(transformed_circuit, final_oneq_gate, qubit)
    pauli_gates = recover_phase(
        optimal_phase=Clifford(transformed_circuit).phase,
        goal_phase=Clifford(circuit).phase,
        num_qubits=circuit.num_qubits,
    )
    phase_recovered_circuit = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)
    for gate, id in pauli_gates:
        q = int(id[1:])  # Extract qubit index from id string like 'q0', 'q1', etc.
        if gate == 'x-gate':
            phase_recovered_circuit.x(q)
        elif gate == 'y-gate':
            phase_recovered_circuit.y(q)
        elif gate == 'z-gate':
            phase_recovered_circuit.z(q)
    transformed_circuit = phase_recovered_circuit.compose(transformed_circuit)
    assert Clifford(transformed_circuit) == Clifford(circuit), "Final transformed circuit does not match original Clifford operation."
    return transformed_circuit
