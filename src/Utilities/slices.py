from qiskit import QuantumCircuit

clifford_gates = set(["id", "x", "y", "z", "h", "s", "sdg", "cx", "cz", "cy", "swap"])


# The dag is a dictionary with entries gate_idx -> [gate_idx, ...]
# The initial entry (root of dag) is -1
def compute_dag(circuit):
    # initialize dag
    G = len(circuit.data)  # number of gates
    dag = dict()
    dag[-1] = []
    for q in range(G):
        dag[q] = []

    # initialize last gate per qubit
    N = circuit.num_qubits  # number of qbits
    last_gate = [-1] * N

    # add all gates to dag, with dependency on last gate per qubit-
    for gate in range(G):
        for qubit in circuit.data[gate].qubits:
            q = qubit._index
            dag[last_gate[q]].append(gate)
            last_gate[q] = gate
    return dag


# Compute a maximal slice from the dag starting from front,
# A slice consists of gate indices satisfying "predicate"
# This also updates front and fanin for the next round
def slice(dag, fanin, front, predicate):
    next_front = []
    current = []

    while len(front) > 0:
        n = front.pop()
        if predicate(n):
            current.append(n)  # add n to current slice
            for s in dag[n]:
                fanin[s] -= 1
                if fanin[s] == 0:  # all predecessors are handled
                    front.append(s)
        else:
            next_front.append(n)
    front.extend(next_front)
    return current


# Yield all pairs of (non-predicate, predicate) slices:
# predicate is supposed to be applied to gates
def get_slices(circuit, predicate):
    dag = compute_dag(circuit)

    # Compute fanin for each node
    fanin = [0] * len(circuit.data)
    for n in dag:
        for s in dag[n]:
            fanin[s] += 1

    # chop off artificial root slice (updates fanin and front)
    front = [-1]
    slice(dag, fanin, front, lambda g: g == -1)

    # keep reporting pairs of bad and good slices
    while True:
        bad_gates = slice(dag, fanin, front, lambda g: not predicate(circuit.data[g]))
        good_gates = slice(dag, fanin, front, lambda g: predicate(circuit.data[g]))
        if len(bad_gates) + len(good_gates) > 0:
            yield (bad_gates, good_gates)
        if len(good_gates) == 0:
            break


if __name__ == "__main__":
    from sys import argv
    from qiskit import qasm2

    circuit = QuantumCircuit.from_qasm_file(argv[1])
    # print("Input circuit:")
    # print(circuit)
    print("Slices:")

    def is_clifford(g):
        return g.name in clifford_gates

    for n, c in get_slices(circuit, is_clifford):
        print("non-clif:", n)
        for g in n:
            print("\t", circuit.data[g].name)
        print("clifford:", c)
        for g in c:
            print("\t", circuit.data[g].name)
