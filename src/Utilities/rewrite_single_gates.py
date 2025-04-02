from qiskit import QuantumCircuit

# Cancelations

# X X
# Y Y
# Z Z
# H H

# S Sdg
# T Tdg
# Sdg S
# Tdg T

# CX CX
# CZ CZ


# Conjugations

# H Z H -> X
# H X H -> Z
# H Y H -> -Y
# S X Sdg -> Y
# S Z Sdg -> Z
# S Y Sdg -> -X

# Simplifications

# S S -> Z
# Sdg Sdg -> Z
# T T -> S
# Tdg Tdg -> Sdg
# R(t1) R(t2) -> R(t1+t2)
# SX SX -> X

# Reordering

# Z-like over control CX
# X-like over data CX

known_unary_gates = set(["x", "y", "z", "h", "s", "t", "sdg", "tdg", "sx"])
cancel_pairs = set(
    [
        ("x", "x"),
        ("y", "y"),
        ("z", "z"),
        ("h", "h"),
        ("s", "sdg"),
        ("sdg", "s"),
        ("t", "tdg"),
        ("tdg", "t"),
    ]
)
rewrite_pairs = {
    ("s", "s"): "z",
    ("sdg", "sdg"): "z",
    ("t", "t"): "s",
    ("tdg", "tdg"): "sdg",
    ("sx", "sx"): "x",
}


def add_gate(circuit, name, qubit):
    match name:
        case "x":
            circuit.x(qubit)
        case "y":
            circuit.y(qubit)
        case "z":
            circuit.z(qubit)
        case "h":
            circuit.h(qubit)
        case "s":
            circuit.s(qubit)
        case "t":
            circuit.t(qubit)
        case "sdg":
            circuit.sdg(qubit)
        case "tdg":
            circuit.tdg(qubit)
        case _:
            print(f"Not prepared to add {name} to circuit")
            exit(-1)


def add_gates(circuit, names, qubit):
    for g in names[qubit]:
        add_gate(circuit, g, qubit)
    names[qubit] = list()


def add_single(buffer, gate):
    if len(buffer) > 0 and (gate, buffer[-1]) in cancel_pairs:
        print(f"...canceling {gate}-{buffer[-1]}")
        buffer.pop()
    elif len(buffer) > 0 and (gate, buffer[-1]) in rewrite_pairs:
        new_name = rewrite_pairs[(gate, buffer[-1])]
        print(f"...rewriting {gate}-{buffer[-1]} -> {new_name}")
        buffer.pop()  # remove old gate
        add_single(buffer, new_name)  # add the new gate recursively
    else:
        buffer.append(gate)


def rewrite_singles(buffer):
    output = list()
    for g in buffer:
        add_single(output, g)
    return output


def cancel_single(circuit):
    print("Canceling")
    output = circuit.copy_empty_like()

    # buffers[i] are the 1-qubit gate-names that have not yet been applied
    buffers = list()
    for _ in range(circuit.num_qubits):
        buffers.append(list())

    # apply gates in the circuit, but delay 1-qubit gates until you encounter 2-qubit gate
    for g in circuit.data:
        if g.name in known_unary_gates:  # store in buffer
            q = g.qubits[0]._index
            add_single(buffers[q], g.name)
        else:
            for q in range(len(g.qubits)):
                qubit = g.qubits[q]._index
                add_gates(output, buffers, qubit)
            output.data.append(g)

    # append the 1-qubit gates that are still remaining at the end
    for q in range(circuit.num_qubits):
        add_gates(output, buffers, q)

    return output


if __name__ == "__main__":
    from sys import argv
    from qiskit import qasm2

    circuit = QuantumCircuit.from_qasm_file(argv[1])
    print("Input circuit:")
    print(circuit)
    circuit = cancel_single(circuit)
    print("Output circuit:")
    print(circuit)
    if len(argv) > 2:
        qasm2.dump(circuit, argv[2])
