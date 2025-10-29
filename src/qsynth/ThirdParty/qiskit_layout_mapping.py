import argparse, textwrap
from qiskit import transpile
from qiskit import QuantumCircuit, qasm2
import sys

# append the path of the src directory
sys.path.append("../..")

from qsynth.LayoutSynthesis.architecture import platform as pt

if __name__ == "__main__":
    text = "A script for tket optimization"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--circuit_in", help="input circuit path")
    parser.add_argument("--circuit_out", help="output circuit path")
    parser.add_argument(
        "-p",
        "--platform",
        help=textwrap.dedent(
            """\
                               Either provider name:
                                 tenerife  = FakeTenerife/IBM QX2, 5 qubit
                                 melbourne = FakeMelbourne, 14 qubit
                                 tokyo     = FakeTokyo, 20 qubit
                               Or generated platforms:
                                 rigetti-{8,12,14,16} = various subgraphs of the rigetti platform
                                 sycamore   = google sycamore platform with grid like topology - 54 qubits
                                 star-{3,7} = test with 3/7-legged star topology (need swaps before first cnot)
                                 cycle-5    = cycle of 5 qubits (good for testing use of ancilla qubits)
                                 grid-{4,5,6,7,8}  = nxn grid (standard platforms for experiments)
                                 test       = test platform (can be anything for experimentation)
                               If none provided, we do not map (default = None)
                               """
        ),
        default=None,
    )
    args = parser.parse_args()
    circuit = QuantumCircuit.from_qasm_file(args.circuit_in)
    # if platform is chosen then coupling graph is extracted:
    if args.platform:
        coupling_graph = pt(
            platform=args.platform,
            bidirectional=1,
            coupling_graph=None,
        )[1]
    else:
        coupling_graph = None
    transpiled_circuit = transpile(
        circuit,
        coupling_map=coupling_graph,
        basis_gates=[
            "rx",
            "ry",
            "rz",
            "swap",
            "cx",
            "h",
            "s",
            "sx",
            "sdg",
            "sxdg",
            "x",
            "y",
            "z",
        ],
        optimization_level=3,
    )

    qasm2.dump(transpiled_circuit, args.circuit_out)
    # print(coupling_graph)
