# Irfansha Shaik, 17.09.2024, Aarhus

import dataclasses
from enum import Enum
import pprint
from qiskit import QuantumCircuit
from qiskit.quantum_info import Clifford
from qsynth.CliffordSynthesis.encodings.recover_phase import recover_phase

all_visited_states = []
state_to_sequence_dict = {}

def compose_gates(circuit, sequence, qubit):
    for gate in sequence:
        if gate == "H":
            circuit.h(qubit)
        elif gate == "P":
            circuit.s(qubit)

def apply_entangling_gate_sequences(
    qi, qj, qi_end, qj_end, flip_cnot=False, use_cz_gate=False
):
    qc = QuantumCircuit(2)
    # First on qubit i:
    compose_gates(qc, qi, 0)
    # Second on qubit j:
    compose_gates(qc, qj, 1)
    # use CNOT or CZ gate
    if use_cz_gate:
        qc.cz(0, 1)
    else:
        if flip_cnot:
            # apply cnot gate (j,i):
            qc.cx(1, 0)
        else:
            # apply cnot gate (i,j):
            qc.cx(0, 1)
    # applying post qi and qj sequences:
    compose_gates(qc, qi_end, 0)
    compose_gates(qc, qj_end, 1)
    return qc

def per_sequence_equivalence(qi_sequence, qj_sequence, flip_cnot=False, use_cz_gate=False, verbose=False):
    equivalent_sequences = []
    base_qc = apply_entangling_gate_sequences(
        qi=qi_sequence,
        qj=qj_sequence,
        qi_end="",
        qj_end="",
        flip_cnot=False, # for base case, we always do not flip
    )
    base_clifford = Clifford(base_qc).symplectic_matrix
    for qi_start_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
        for qj_start_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
            for qi_end_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
                for qj_end_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
                    rewrite_qc = apply_entangling_gate_sequences(
                        qi=qi_start_sequence,
                        qj=qj_start_sequence,
                        qi_end=qi_end_sequence,
                        qj_end=qj_end_sequence,
                        flip_cnot=flip_cnot,
                        use_cz_gate=use_cz_gate,
                    )
                    rewrite_clifford = Clifford(rewrite_qc).symplectic_matrix
                    if (rewrite_clifford == base_clifford).all():
                        equivalent_sequences.append((qi_start_sequence, qj_start_sequence, qi_end_sequence, qj_end_sequence))
                        if verbose:
                            print(f"Equivalent found for {qi_sequence, qj_sequence} with {qi_start_sequence, qj_start_sequence, qi_end_sequence, qj_end_sequence}, flip_cnot={flip_cnot}, use_cz_gate={use_cz_gate}")
    return equivalent_sequences

def find_all_equivalents(use_cz_gate=False, verbose=False):
    unique_equivalents = {}
    valid_single_qubit_sequences = ["", "HP", "PH", "H", "P", "HPH"]
    for qi_sequence in valid_single_qubit_sequences:
        for qj_sequence in valid_single_qubit_sequences:
            equivalents = per_sequence_equivalence(qi_sequence, qj_sequence, flip_cnot=False, use_cz_gate=use_cz_gate, verbose=verbose)
            unique_equivalents[(qi_sequence, qj_sequence)] = equivalents
    return unique_equivalents
def find_all_equivalents_with_reverse(use_cz_gate=False, verbose=False):
    unique_equivalents = {}
    valid_single_qubit_sequences = ["", "HP", "PH", "H", "P", "HPH"]
    for qi_sequence in valid_single_qubit_sequences:
        for qj_sequence in valid_single_qubit_sequences:
            equivalents = per_sequence_equivalence(qi_sequence, qj_sequence, flip_cnot=True, use_cz_gate=use_cz_gate, verbose=verbose)
            unique_equivalents[(qi_sequence, qj_sequence)] = equivalents
    return unique_equivalents

def add_pauli_gates(base_circuit, circuit):
    pauli_gates = recover_phase(
        optimal_phase=Clifford(circuit).phase,
        goal_phase=Clifford(base_circuit).phase,
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
    transformed_circuit = phase_recovered_circuit.compose(circuit)
    return transformed_circuit


def print_all_equivalents(use_cz_gate=False):
    unique_equivalents = find_all_equivalents(use_cz_gate=use_cz_gate)
    unique_equivalents_with_reverse = find_all_equivalents_with_reverse(use_cz_gate=use_cz_gate)
    for key, value in unique_equivalents.items():
        print(f"Sequence {key}:")
        for equivalent in value:
            print(f"  (d):                       {equivalent}")
        for equivalent in unique_equivalents_with_reverse[key]:
            print(f"  (f):                       {equivalent}")
        # check equivalence:
        base_qc = apply_entangling_gate_sequences(
            qi=key[0],
            qj=key[1],
            qi_end="",
            qj_end="",
            flip_cnot=False,
        )
        base_clifford = Clifford(base_qc)
        for equivalent in value:
            rewrite_qc = apply_entangling_gate_sequences(
                qi=equivalent[0],
                qj=equivalent[1],
                qi_end=equivalent[2],
                qj_end=equivalent[3],
                flip_cnot=False,
                use_cz_gate=use_cz_gate,
            )
            rewrite_qc = add_pauli_gates(base_qc, rewrite_qc)
            rewrite_clifford = Clifford(rewrite_qc)
            assert rewrite_clifford == base_clifford, "Equivalence check failed!"
        for equivalent in unique_equivalents_with_reverse[key]:
            rewrite_qc = apply_entangling_gate_sequences(
                qi=equivalent[0],
                qj=equivalent[1],
                qi_end=equivalent[2],
                qj_end=equivalent[3],
                flip_cnot=True,
                use_cz_gate=use_cz_gate,
            )
            rewrite_qc = add_pauli_gates(base_qc, rewrite_qc)
            rewrite_clifford = Clifford(rewrite_qc)
            assert rewrite_clifford == base_clifford, "Equivalence check failed!"


#print_all_equivalents(use_cz_gate=True)

# Gate cost dictionary: {sequence: (rx_cost, rz_cost, 1q_cost)}
gate_costs = {
    "":    (0, 0, 0),
    "P":   (0, 1, 1),
    "H":   (1, 2, 1),
    "HP":  (1, 1, 2),
    "PH":  (1, 1, 2),
    "HPH": (1, 0, 1),
}

def transform_sequences(sequence_tuple):
    transformed = []
    for seq in sequence_tuple:
        if seq == "":
            transformed.append("i")
        elif seq == "H":
            transformed.append("h")
        elif seq == "P":
            transformed.append("s")
        elif seq == "HP":
            transformed.append("hs")
        elif seq == "PH":
            transformed.append("sh")
        elif seq == "HPH":
            transformed.append("sx")
    return tuple(transformed)

cost = Enum('cost', ['rx_cost', 'rz_cost', 'one_q_cost'])

def compute_rx_cost(use_cz_gate=False):
    unique_equivalents = find_all_equivalents(use_cz_gate=use_cz_gate)
    # checking strict equivalence:
    for key, value in unique_equivalents.items():
        base_qc = apply_entangling_gate_sequences(
            qi=key[0],
            qj=key[1],
            qi_end="",
            qj_end="",
            flip_cnot=False,
        )
        base_clifford = Clifford(base_qc)
        for equivalent in value:
            rewrite_qc = apply_entangling_gate_sequences(
                qi=equivalent[0],
                qj=equivalent[1],
                qi_end=equivalent[2],
                qj_end=equivalent[3],
                flip_cnot=False,
                use_cz_gate=use_cz_gate,
            )
            rewrite_qc = add_pauli_gates(base_qc, rewrite_qc)
            rewrite_clifford = Clifford(rewrite_qc)
            assert rewrite_clifford == base_clifford, "Equivalence check failed!"
    unique_equivalents_with_reverse = find_all_equivalents_with_reverse(use_cz_gate=use_cz_gate)
    # checking equivalence with reverse:
    for key, value in unique_equivalents_with_reverse.items():
        base_qc = apply_entangling_gate_sequences(
            qi=key[0],
            qj=key[1],
            qi_end="",
            qj_end="",
            flip_cnot=False,
        )
        base_clifford = Clifford(base_qc)
        for equivalent in value:
            rewrite_qc = apply_entangling_gate_sequences(
                qi=equivalent[0],
                qj=equivalent[1],
                qi_end=equivalent[2],
                qj_end=equivalent[3],
                flip_cnot=True,
                use_cz_gate=use_cz_gate,
            )
            rewrite_qc = add_pauli_gates(base_qc, rewrite_qc)
            rewrite_clifford = Clifford(rewrite_qc)
            assert rewrite_clifford == base_clifford, "Equivalence check failed!"
    oneq_sequence_cost_dict = {}
    all_rewrite_rules = {}
    best_rewrite_rules = {}
    for key, value in unique_equivalents.items():
        rx_cost = sum(gate_costs[seq][0] for seq in key)
        rz_cost = sum(gate_costs[seq][1] for seq in key)
        one_q_cost = sum(gate_costs[seq][2] for seq in key)
        oneq_sequence_cost_dict[transform_sequences(key)] = {
            cost.rx_cost: rx_cost,
            cost.rz_cost: rz_cost,
            cost.one_q_cost: one_q_cost
        }
        #print()
        #print(f"Base sequence: {key} with costs: rx_cost={rx_cost}, rz_cost={rz_cost}, one_q_cost={one_q_cost}")
        equivalents_with_costs = []
        for equivalent in value:
            rx_cost = sum(gate_costs[seq][0] for seq in equivalent[:2])
            rz_cost = sum(gate_costs[seq][1] for seq in equivalent[:2])
            one_q_cost = sum(gate_costs[seq][2] for seq in equivalent[:2])
            equivalents_with_costs.append(("d", equivalent, rx_cost, rz_cost, one_q_cost))
            if transform_sequences(key) not in all_rewrite_rules:
                all_rewrite_rules[transform_sequences(key)] = [(transform_sequences(equivalent),"d")]
            elif transform_sequences(equivalent) not in all_rewrite_rules[transform_sequences(key)]:
                all_rewrite_rules[transform_sequences(key)].append((transform_sequences(equivalent),"d"))
        if use_cz_gate == False:
            for equivalent in unique_equivalents_with_reverse[key]:
                rx_cost = sum(gate_costs[seq][0] for seq in equivalent[:2])
                rz_cost = sum(gate_costs[seq][1] for seq in equivalent[:2])
                one_q_cost = sum(gate_costs[seq][2] for seq in equivalent[:2])
                equivalents_with_costs.append(("f", equivalent, rx_cost, rz_cost, one_q_cost))
                if transform_sequences(equivalent) not in all_rewrite_rules[transform_sequences(key)]:
                    all_rewrite_rules[transform_sequences(key)].append((transform_sequences(equivalent),"f"))
        # Sort by rx_cost, 1q_cost then rz_cost
        rx_priority_equivalents = sorted(equivalents_with_costs, key=lambda x: (x[2], x[4], x[3]))
        oneq_priority_equivalents = sorted(equivalents_with_costs, key=lambda x: (x[4], x[2], x[3]))
        #print(f"Rx priority equivalent: {rx_priority_equivalents[0]}")
        #print(f"1Q priority equivalent: {oneq_priority_equivalents[0]}")
        assert rx_priority_equivalents[0][1] == oneq_priority_equivalents[0][1]
        # Only store if the cost of rewrite rule of Rx cost and 1Q cost is less than base cost (priority rx cost).
        if use_cz_gate or \
           (rx_priority_equivalents[0][2] < oneq_sequence_cost_dict[transform_sequences(key)][cost.rx_cost] or \
           rx_priority_equivalents[0][4] < oneq_sequence_cost_dict[transform_sequences(key)][cost.one_q_cost]):
            best_rewrite_rules[transform_sequences(key)] = (transform_sequences(rx_priority_equivalents[0][1]), rx_priority_equivalents[0][0])
        else:
            best_rewrite_rules[transform_sequences(key)] = (transform_sequences((key[0],key[1],'','')), 'd')
    """
    for key, value in all_rewrite_rules.items():
        print(f"Sequence {key}:")
        for equivalent in value:
            print(f"   can be rewritten as {equivalent}")
    """
    print("all_rewrite_rules = ", end="")
    pprint.pprint(all_rewrite_rules)
    print("best_rewrite_rules_dict = ", end="")
    pprint.pprint(best_rewrite_rules)

compute_rx_cost(use_cz_gate=True)

def compute_1q_states():
    for gate in ["", "H", "P", "HP", "PH", "HPH"]:
        qc = QuantumCircuit(1)
        if gate == "":
            pass
        elif gate == "H":
            qc.h(0)
        elif gate == "P":
            qc.s(0)
        elif gate == "HP":
            qc.h(0)
            qc.s(0)
        elif gate == "PH":
            qc.s(0)
            qc.h(0)
        elif gate == "HPH":
            qc.sx(0)
        clifford = tuple(Clifford(qc).symplectic_matrix.flatten().tolist())
        state_to_sequence_dict[clifford] = gate
    print("1Q states to sequences mapping:")
    pprint.pprint(state_to_sequence_dict)

#compute_1q_states()