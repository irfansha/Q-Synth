# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit_aer import AerSimulator
from mqt import qcec
import qiskit
import argparse
from qiskit import QuantumCircuit

# Main:
if __name__ == "__main__":
    text = "A test scripts for equivalence using qiskit, assumming measuremets are already there"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--circuit1", help="input circuit file 1")
    parser.add_argument("--circuit2", help="input circuit file 2")
    args = parser.parse_args()

    # reading first circuit:
    circuit_file1 = QuantumCircuit.from_qasm_file(args.circuit1)
    print(circuit_file1)
    # reading second circuit:
    circuit_file2 = QuantumCircuit.from_qasm_file(args.circuit2)
    print(circuit_file2)

    # Construct an ideal simulator
    aersim = AerSimulator()

    # Perform an ideal simulation
    result_ideal = qiskit.execute(
        [circuit_file1, circuit_file2], aersim, shots=1000000
    ).result()
    counts1 = result_ideal.get_counts(circuit_file1)
    counts2 = result_ideal.get_counts(circuit_file2)
    print(counts1, counts2)

    # verify the equivalence of two circuits provided as qasm files
    result = qcec.verify(args.circuit1, args.circuit2)

    # print the result
    print(result.equivalence)
