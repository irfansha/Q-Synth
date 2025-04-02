# Irfansha Shaik, 01-11-2024, Aarhus.

# We generate random clifford circuits with qiksit

import argparse
import os
from qiskit import quantum_info, qasm2
from qiskit.quantum_info import Clifford
from pathlib import Path
from pytket.passes import CliffordSimp
from pytket.qasm import circuit_from_qasm, circuit_to_qasm
from pytket.extensions.qiskit import tk_to_qiskit
from pytket.circuit import OpType


def count_gates(circuit):
    return circuit.n_1qb_gates(), circuit.n_gates_of_type(OpType.CX) + (
        3 * circuit.n_gates_of_type(OpType.SWAP)
    )


def optimize_with_tket_qiskit(original_clifford, circuit_file, allow_swaps):
    tket_circuit = circuit_from_qasm(circuit_file)
    oneq_gates, cx_gates = count_gates(tket_circuit)
    # we repeat the optimization until there is no difference in cnot count:
    while True:
        if allow_swaps:
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
    qiskit_translated_circuit = tk_to_qiskit(tket_circuit)
    # print(qiskit_translated_circuit)
    assert Clifford(qiskit_translated_circuit) == original_clifford
    circuit_to_qasm(tket_circuit, circuit_file)


def generate_clifford_and_dump(
    nqubits, seed, output_dir, synthesize_optimize, allow_swaps
):
    clifford = quantum_info.random_clifford(num_qubits=nqubits, seed=seed)
    print(clifford)
    if synthesize_optimize:
        # if enabled, then we generate a qasm file:
        output_file_path = os.path.join(output_dir, f"{nqubits:02}q_{seed:05}.qasm")
        qiskit_circuit = clifford.to_circuit()
        qasm2.dump(qiskit_circuit, output_file_path)
        optimize_with_tket_qiskit(clifford, output_file_path, allow_swaps)
    else:
        # if not enabled, we only write the stabilizer to a file:
        output_file_path = os.path.join(output_dir, f"{nqubits:02}q_{seed:05}.txt")
        with open(output_file_path, "w") as f:
            f.write(" ".join(clifford.to_labels()))


# Main:
if __name__ == "__main__":
    text = "A script for generating random clifford circuits using Aaronson's synthesis in qiskit"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-n", "--nqubits", type=int, help="number of qubits, default = 5", default=5
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        help="seed for random generation, default 0",
        default=0,
    )
    parser.add_argument(
        "--num_iterations",
        type=int,
        help="number of iterations, numbered with the random seed used (between 0 and 10^6)",
        default=None,
    )
    parser.add_argument(
        "--out_folder",
        help="path to output circuit file, default=benchmarks",
        default="benchmarks",
    )
    parser.add_argument(
        "--synthesize_optimize",
        help="synthesize with qiskit, optimize with -O3 and optimize tket (CliffordSimp) (default disabled)",
        action="store_true",
    )
    parser.add_argument(
        "--allow_swaps",
        help="allow swaps in tket optimization, default disabled",
        action="store_true",
    )

    args = parser.parse_args()

    current_file_path = os.path.abspath(__file__)
    current_folder_path = Path(current_file_path).parent
    output_dir = os.path.join(current_folder_path, args.out_folder)
    # Checking if out directory exits:
    if not Path(output_dir).is_dir():
        print("Invalid directory path: " + output_dir)
        print("Creating new directory with same path.")
        os.mkdir(output_dir)

    if args.num_iterations == None:
        generate_clifford_and_dump(
            args.nqubits,
            args.seed,
            output_dir,
            args.synthesize_optimize,
            args.allow_swaps,
        )
    else:
        import random

        # fixing generator seed for reproducablity:
        random.seed(0)
        for iter in range(args.num_iterations):
            seed = random.randint(0, 99999)
            generate_clifford_and_dump(
                args.nqubits,
                seed,
                output_dir,
                args.synthesize_optimize,
                args.allow_swaps,
            )
