# Irfansha Shaik, 17.09.2024, Aarhus

import dataclasses

all_visited_states = []
state_to_sequence_dict = {}


# we realize that any state can atmost have a XOR of 4 terms
# xi + xj + zi + zj, or any subset of this
# we will use this to keep track of the state and manipulate when XORs are applied:
@dataclasses.dataclass(unsafe_hash=True)
class xor_state:
    # by default false, we set required ones to true:
    xi: bool = False
    xj: bool = False
    zi: bool = False
    zj: bool = False

    def xor_xi(self):
        if self.xi == True:
            self.xi = False
        else:
            assert self.xi == False
            self.xi = True

    def xor_xj(self):
        if self.xj == True:
            self.xj = False
        else:
            assert self.xj == False
            self.xj = True

    def xor_zi(self):
        if self.zi == True:
            self.zi = False
        else:
            assert self.zi == False
            self.zi = True

    def xor_zj(self):
        if self.zj == True:
            self.zj = False
        else:
            assert self.zj == False
            self.zj = True

    def copy_update(self, other_xor):
        self.xi = other_xor.xi
        self.xj = other_xor.xj
        self.zi = other_xor.zi
        self.zj = other_xor.zj

    # updating current state by xoring with input control state:
    def xor_update(self, control_xor):
        if control_xor.xi:
            self.xor_xi()
        if control_xor.xj:
            self.xor_xj()
        if control_xor.zi:
            self.xor_zi()
        if control_xor.zj:
            self.xor_zj()

    def __str__(self) -> str:
        enabled_values = []
        if self.xi:
            enabled_values.append("xi")
        if self.xj:
            enabled_values.append("xj")
        if self.zi:
            enabled_values.append("zi")
        if self.zj:
            enabled_values.append("zj")
        return "+".join(enabled_values).ljust(12)


# Swaps x colum and z column:
def apply_h_gate(X, Z):
    X_copy = dataclasses.replace(X)
    X.copy_update(Z)
    Z.copy_update(X_copy)


# Column addition between x column and z column, so we do the same for the truth table:
def apply_p_gate(X, Z):
    Z.xor_update(X)


# Column additions between xi and xj columns; and zj and zi columns:
def apply_cnot_gate(Xi, Xj, Zi, Zj):
    Xj.xor_update(Xi)
    Zi.xor_update(Zj)


def generate_and_check_single_sequences():
    # We start with xi and zi
    # create sequences starting with H/P:
    interesting_gate_sequences = []
    for i in range(4):
        P_gate_sequence = ""
        H_gate_sequence = ""
        for j in range(i):
            if j % 2 == 0:
                H_gate_sequence += "H"
                P_gate_sequence += "P"
            else:
                H_gate_sequence += "P"
                P_gate_sequence += "H"
        interesting_gate_sequences.append(H_gate_sequence)
        interesting_gate_sequences.append(P_gate_sequence)

    for gate_sequence in interesting_gate_sequences:
        print(
            f"----------------------------{gate_sequence}-----------------------------"
        )
        # start from xi and zi i.e., the identity gate:
        Xi = xor_state(xi=True)
        Zi = xor_state(zi=True)
        print("Original", Xi, Zi)
        for gate in gate_sequence:
            if gate == "H":
                apply_h_gate(X=Xi, Z=Zi)
            elif gate == "P":
                apply_p_gate(X=Xi, Z=Zi)

        print("Final   ", Xi, Zi)
        if (Xi, Zi) not in all_visited_states:
            all_visited_states.append((Xi, Zi))
        else:
            print("Found")


# CNOT is applied from i to j by default for now:
def apply_entangling_gate_sequences(
    qi, qj, qi_end, qj_end, Xi, Zi, Xj, Zj, flip_cnot=False
):
    # First on qubit i:
    for gate in qi:
        if gate == "H":
            apply_h_gate(X=Xi, Z=Zi)
        elif gate == "P":
            apply_p_gate(X=Xi, Z=Zi)
    # Second on qubit j:
    for gate in qj:
        if gate == "H":
            apply_h_gate(X=Xj, Z=Zj)
        elif gate == "P":
            apply_p_gate(X=Xj, Z=Zj)

    # print("precnot ",Xi, Zi, Xj, Zj)
    if flip_cnot:
        # apply cnot gate (j,i):
        apply_cnot_gate(Xi=Xj, Zi=Zj, Xj=Xi, Zj=Zi)
    else:
        # apply cnot gate (i,j):
        apply_cnot_gate(Xi=Xi, Zi=Zi, Xj=Xj, Zj=Zj)
    # print("postcnot ",Xi, Zi, Xj, Zj)

    # applying post qi and qj sequences:
    for gate in qi_end:
        if gate == "H":
            apply_h_gate(X=Xi, Z=Zi)
        elif gate == "P":
            apply_p_gate(X=Xi, Z=Zi)
    # Second on qubit j:
    for gate in qj_end:
        if gate == "H":
            apply_h_gate(X=Xj, Z=Zj)
        elif gate == "P":
            apply_p_gate(X=Xj, Z=Zj)


# After some experimentation with generate_and_check_single_sequences,
# we found the following sequences unique when ignoring phase column:
# [I, H, P, HP, PH, HPH] (both HPH and PHP are equivalent, we choose HPH arbitrarly)

# Now we need to check the combinations with CNOT gate
# Since we have 6 options for single gate sequence,
# we can place those sequences either before CNOT qubits (control and target) or after the gate.
# So we have 6*6*6*6 combinations in total
# my hope is that many of the formulas coincide:


def generate_and_check_entangling_sequences():
    # valid_single_qubit_sequences = ["", "H", "P", "HP", "PH", "HPH"]
    valid_single_qubit_sequences = ["", "HP", "PH", "H", "P", "HPH"]

    count = 0
    unique = 0
    exact_found = 0

    states = []
    reversed_states = []  # CNOT flipped j,i from i,j states
    sequences = []

    for qi_sequence in valid_single_qubit_sequences:
        for qj_sequence in valid_single_qubit_sequences:
            for qi_end_sequence in valid_single_qubit_sequences:
                for qj_end_sequence in valid_single_qubit_sequences:
                    print(count)
                    count = count + 1
                    print(
                        f"----------------------------{qi_sequence,qj_sequence}-------{qi_end_sequence,qj_end_sequence}--------------------------"
                    )
                    # starting with xi, xj, zi, zj:
                    Xi = xor_state(xi=True)
                    Zi = xor_state(zi=True)
                    Xj = xor_state(xj=True)
                    Zj = xor_state(zj=True)
                    # print("Original",Xi, Zi, Xj, Zj)
                    apply_entangling_gate_sequences(
                        qi=qi_sequence,
                        qj=qj_sequence,
                        qi_end=qi_end_sequence,
                        qj_end=qj_end_sequence,
                        Xi=Xi,
                        Zi=Zi,
                        Xj=Xj,
                        Zj=Zj,
                        flip_cnot=False,
                    )
                    print("Final : ", Xi, Zi, Xj, Zj)

                    # Checking reverse CNOT with j, i instead of with i,j
                    r_Xi = xor_state(xi=True)
                    r_Zi = xor_state(zi=True)
                    r_Xj = xor_state(xj=True)
                    r_Zj = xor_state(zj=True)
                    # print("Original",r_Xi, r_Zi, r_Xj, r_Zj)
                    apply_entangling_gate_sequences(
                        qi=qi_sequence,
                        qj=qj_sequence,
                        qi_end=qi_end_sequence,
                        qj_end=qj_end_sequence,
                        Xi=r_Xi,
                        Zi=r_Zi,
                        Xj=r_Xj,
                        Zj=r_Zj,
                        flip_cnot=True,
                    )
                    print("Final : ", r_Xi, r_Zi, r_Xj, r_Zj)

                    states.append((Xi, Zi, Xj, Zj))
                    reversed_states.append((r_Xi, r_Zi, r_Xj, r_Zj))
                    sequences.append(
                        [qi_sequence, qj_sequence, qi_end_sequence, qj_end_sequence]
                    )

    all_unique_states = []
    for index in range(len(states)):
        (Xi, Zi, Xj, Zj) = states[index]
        if (Xi, Zi, Xj, Zj) in all_unique_states:
            # print("Exact Found")
            exact_found += 1
        else:
            all_unique_states.append((Xi, Zi, Xj, Zj))
            state_to_sequence_dict[(Xi, Zi, Xj, Zj)] = sequences[index]
            if sequences[index] == ["", "", "", ""]:
                print((Xi, Zi, Xj, Zj))
            unique += 1
            print(f"unique {unique}: {sequences[index]}")
    # Looping through flipped CNOT states:
    for index in range(len(states)):
        (r_Xi, r_Zi, r_Xj, r_Zj) = reversed_states[index]
        if (r_Xi, r_Zi, r_Xj, r_Zj) in all_unique_states:
            exact_found += 1
        else:
            all_unique_states.append((r_Xi, r_Zi, r_Xj, r_Zj))
            state_to_sequence_dict[(r_Xi, r_Zi, r_Xj, r_Zj)] = sequences[index]
            unique += 1
            print(f"unique {unique}: {sequences[index]}")

    print("exact found:", exact_found)
    print("Unique:", unique)
    print("Total: ", unique + exact_found)


# generate_and_check_single_sequences()
generate_and_check_entangling_sequences()

"""
print("Xi Zi Xj Zj")
for state, sequence in state_to_sequence_dict.items():
    print(state[0], state[1], state[2], state[3], sequence)
"""
