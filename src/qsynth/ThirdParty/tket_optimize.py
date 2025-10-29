from pytket.qasm import circuit_from_qasm, circuit_to_qasm
import argparse
from pytket.circuit import OpType
from pytket.passes import CliffordSimp, AutoRebase
from qiskit import qasm2, QuantumCircuit
from pytket.extensions.qiskit import tk_to_qiskit


def gate_get_qubit(gate, bit_idx):
    return gate.qubits[bit_idx]._index


def replace_swaps_with_3cx(qc):
    num_qubits = len(qc.qubits)
    swap_free_circuit = QuantumCircuit(num_qubits)
    for gate in qc:
        if gate.operation.name == "swap":
            # decomposing swap to 3 cnots:
            q1, q2 = gate_get_qubit(gate, 0), gate_get_qubit(gate, 1)
            swap_free_circuit.cx(q1, q2)
            swap_free_circuit.cx(q2, q1)
            swap_free_circuit.cx(q1, q2)
        else:
            swap_free_circuit.append(gate)
    return swap_free_circuit


# compute number of cnots (not swaps, only cnots):
def cxcount(qc):
    return qc.count_ops()["cx"]


# compute circuit cost:
def cxcount_swaps_as_3cx(qc):
    if "swap" in qc.count_ops():
        return qc.count_ops()["cx"] + 3 * (qc.count_ops()["swap"])
    else:
        return qc.count_ops()["cx"]


# we do not count swap gates depth, we ignore every other 2-qubit gate:
def cxdepth(qc):
    num_qubits = len(qc.qubits)
    cx_circuit = QuantumCircuit(num_qubits)
    for gate in qc:
        if len(gate.qubits) == 2 and (gate.operation.name == "cx"):
            cx_circuit.append(gate)
    # print(cx_circuit)
    return cx_circuit.depth()


# we convert swap to 3 cnots and compute the cnot-depth:
def cxdepth_swaps_as_3cx(qc):
    swap_free_circuit = replace_swaps_with_3cx(qc)
    return cxdepth(swap_free_circuit)


def count_gates(circuit):
    return circuit.n_1qb_gates(), circuit.n_gates_of_type(OpType.CX) + (
        3 * circuit.n_gates_of_type(OpType.SWAP)
    )


if __name__ == "__main__":
    text = "A script for tket optimization"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--circuit_in", help="input circuit path")
    parser.add_argument("--circuit_out", help="output circuit path")
    parser.add_argument(
        "--allow_swaps",
        help="allow swaps in tket optimization, default disabled",
        action="store_true",
    )
    args = parser.parse_args()

    tket_circuit = circuit_from_qasm(args.circuit_in)
    oneq_gates, cx_gates = count_gates(tket_circuit)
    # we repeat the optimization until there is no difference in cnot count:
    while True:
        if args.allow_swaps:
            CliffordSimp(allow_swaps=True).apply(tket_circuit)
        else:
            CliffordSimp(allow_swaps=False).apply(tket_circuit)
        cur_1q_gates, cur_cx_gates = count_gates(tket_circuit)
        if oneq_gates == cur_1q_gates and cx_gates == cur_cx_gates:
            print("equal")
            break
        else:
            print(
                f"improved {oneq_gates}, {cx_gates} -> {cur_1q_gates}, {cur_cx_gates}"
            )
            oneq_gates = cur_1q_gates
            cx_gates = cur_cx_gates

    tket_circuit.replace_implicit_wire_swaps()
    AutoRebase(
        gateset={
            OpType.X,
            OpType.Y,
            OpType.Z,
            OpType.SX,
            OpType.S,
            OpType.Sdg,
            OpType.SXdg,
            OpType.H,
            OpType.CX,
            OpType.Rx,
            OpType.Ry,
            OpType.Rz,
            OpType.SWAP,
        }
    ).apply(tket_circuit)
    # circuit_to_qasm(tket_circuit, args.circuit_out)
    qc = tk_to_qiskit(tket_circuit)
    # print(qc)
    qasm2.dump(qc, args.circuit_out)
    print("cx count without swaps", cxcount(qc))
    print("cx count with swaps as 3cx", cxcount_swaps_as_3cx(qc))
    print("cx depth without swaps", cxdepth(qc))
    print("cx depth with swaps as 3cx", cxdepth_swaps_as_3cx(qc))
