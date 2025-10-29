# Irfansha Shaik, 31.01.2024, Aarhus


# takes qubit mapping and returns a sequence of swaps to rearrange a permutation:
def extract_swaps_for_initial_mapping(qubit_map, plan, num_qubits):
    qubit_sequence = []
    for i in range(num_qubits):
        qubit_sequence.append(qubit_map[i])

    swaps = []
    # every ith iteration brings the ith index in the right position:
    for i in range(num_qubits):
        index = qubit_sequence.index(i)
        if i == index:
            continue
        else:
            swaps.append(("swap", f"q{i}", f"q{index}"))
            # swapping:
            qubit1 = int(qubit_sequence[i])
            qubit2 = int(qubit_sequence[index])

            qubit_sequence[index] = qubit1
            qubit_sequence[i] = qubit2

    # reverse plan to enable the right positions of qubits:
    swaps = swaps[::-1]
    plan.extend(swaps)

    return plan
