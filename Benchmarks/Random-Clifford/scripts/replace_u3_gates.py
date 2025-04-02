from qiskit import quantum_info, qasm2, QuantumCircuit, transpile
from qiskit.quantum_info import Clifford
import argparse
import os
from pathlib import Path

if __name__ == "__main__":
    text = "A script for replacing u3 gates to clifford gates by aaronson synthesis"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--circuit_in", help="circuit in file path")
    parser.add_argument(
        "--output_folder",
        help="output folder to write the circuit with the same name as input file",
    )

    args = parser.parse_args()

    current_file_path = os.path.abspath(__file__)
    input_file_name = os.path.basename(args.circuit_in)
    current_folder_path = Path(current_file_path).parent
    output_dir = os.path.join(current_folder_path, args.output_folder)

    # Checking if out directory exits:
    if not Path(output_dir).is_dir():
        print("Invalid directory path: " + output_dir)
        print("Creating new directory with same path.")
        os.mkdir(output_dir)

    output_file = os.path.join(current_folder_path, args.output_folder, input_file_name)

    circuit = qasm2.load(args.circuit_in)
    print(circuit)
    in_clifford = Clifford(circuit)

    out_circuit = QuantumCircuit(circuit.num_qubits)

    for gate in circuit:
        # create a dummy circuit
        temp_circuit = QuantumCircuit(circuit.num_qubits)
        temp_circuit.append(gate)
        # synthesis the right single qubit gates:
        if gate.operation.name != "cx" and gate.operation.name != "swap":
            temp_clifford = Clifford(temp_circuit)
            temp_circuit = temp_clifford.to_circuit()
        # concatenate to output circuit:
        out_circuit = out_circuit.compose(temp_circuit)

    print(out_circuit)
    out_clifford = Clifford(out_circuit)
    assert in_clifford == out_clifford
    assert circuit.count_ops()["cx"] == out_circuit.count_ops()["cx"]

    qasm2.dump(out_circuit, output_file)
