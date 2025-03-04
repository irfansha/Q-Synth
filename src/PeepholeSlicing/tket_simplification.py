import argparse
from qiskit import QuantumCircuit

from pytket.passes import CliffordSimp
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit

# Main:
if __name__ == "__main__":
    text = "A test script for tket clifford simplification"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--circuit_in",
        help="input circuit file",
        default="Benchmarks/Testing/toggle.qasm",
    )

    args = parser.parse_args()

    # load your own QASM file
    circuit_file = QuantumCircuit.from_qasm_file(args.circuit_in)
    # print(circuit_file)
    # circuit_file.measure_all()
    circ = qiskit_to_tk(circuit_file)

    CliffordSimp().apply(circ)

    simp_circ = tk_to_qiskit(circ)
    print(simp_circ)

    print("Original operators:", circuit_file.count_ops())
    print("Final operators:", simp_circ.count_ops())
