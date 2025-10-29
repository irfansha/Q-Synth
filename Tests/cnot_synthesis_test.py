# Required imports
from qsynth.peephole_synthesis import peephole_synthesis
from Tests.test_utils import (
    EXAMPLES_DIR,
    ECAI_DIR,
    generate_peephole_options,
    count_swaps_cx,
    count_depth_cx_depth,
)
from qiskit import QuantumCircuit


def test_sat_gates_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="sat",
            qubit_permute=False,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_planning_gates_fd_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="planning",
            qubit_permute=False,
            minimize="cx-count",
            solver="fd-ms",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_planning_gates_madagascar_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="planning",
            qubit_permute=False,
            minimize="cx-count",
            solver="madagascar",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_sat_depth_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="sat",
            qubit_permute=False,
            minimize="cx-depth",
            solver="pysat-cd19",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 3
    assert cx_depth == 3


def test_planning_depth_fd_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="planning",
            qubit_permute=False,
            minimize="cx-depth",
            solver="fd-ms",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 3
    assert cx_depth == 3


def test_planning_depth_madagascar_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="planning",
            qubit_permute=False,
            minimize="cx-depth",
            solver="madagascar",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 3
    assert cx_depth == 3


def test_sat_gates_qubits_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="sat",
            qubit_permute=True,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 26


def test_sat_gates_barenco_tof_3_melbourne():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform="melbourne",
            slicing="cnot",
            model="sat",
            qubit_permute=False,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=True,  # Bi-directional is important here
        )
    ).circuit

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 3
    assert cx == 30


# def test_sat_qubits_gates_ecai_24_tenerife():

#     # Compute circuit and opt_val
#     circuit = peephole_cnotsynthesis(
#         **generate_peephole_options(
#             circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
#             platform="tenerife",
#             model="sat",
#             qubit_permute=True,
#             minimize="cx-count",
#             solver="pysat-cd19",
#             bidirectional=True  # Bi-directional is important here
#         )
#     )

#     # Asserts (these are wrt. considering swaps as swaps)
#     swaps, cx = count_swaps_cx(circuit)
#     assert swaps == 0
#     assert cx == 5


# def test_sat_qubits_gates_ecai_24_tenerife():

#     # Compute circuit and opt_val
#     circuit = peephole_cnotsynthesis(
#         **generate_peephole_options(
#             circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
#             platform="tenerife",
#             model="sat",
#             qubit_permute=False,
#             minimize="cx-count",
#             solver="pysat-cd19",
#             bidirectional=True  # Bi-directional is important here
#         )
#     )

#     # Asserts (these are wrt. considering swaps as swaps)
#     swaps, cx = count_swaps_cx(circuit)
#     assert swaps == 0
#     assert cx == 6


def test_qbf_gates_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="qbf",
            qubit_permute=False,
            minimize="cx-count",
            solver="caqe",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 41


def test_qbf_depth_qft_4():
    circuit_in = QuantumCircuit.from_qasm_file(f"{ECAI_DIR}/tpar-optimized/qft_4.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="cnot",
            model="qbf",
            qubit_permute=False,
            minimize="cx-depth",
            solver="caqe",
            bidirectional=True,
        )
    ).circuit

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 172
    assert cx_depth == 77
