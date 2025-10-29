# Required imports
from qsynth.peephole_synthesis import peephole_synthesis
from Tests.test_utils import (
    EXAMPLES_DIR,
    ECAI_DIR,
    generate_peephole_options,
    count_swaps_cx,
    count_depth_cx_depth,
    get_cx_depth_swaps_as_3cx,
)
from qiskit import QuantumCircuit

# simpleaux tests:


def test_sat_gates_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
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


def test_sat_depth_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=False,
            minimize="cx-depth",
            solver="pysat-cd19",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    assert cx_depth == 3


def test_sat_gates_permute_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
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
    assert cx == 25


def test_sat_depth_permute_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=True,
            minimize="cx-depth",
            solver="pysat-cd19",
            bidirectional=False,
        )
    ).circuit

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    assert cx_depth == 21


# simple aux with gate ordering + simple paths :


def test_sat_gates_gate_ordering_simple_paths_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=False,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=False,
            gate_ordering=True,
            simple_path_restrictions=True,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_sat_depth_gate_ordering_simple_paths_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=False,
            minimize="cx-depth",
            solver="pysat-cd19",
            bidirectional=False,
            gate_ordering=True,
            simple_path_restrictions=True,
        )
    ).circuit

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    assert cx_depth == 3


def test_sat_gates_permute_gate_ordering_simple_paths_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=True,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=False,
            gate_ordering=True,
            simple_path_restrictions=True,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 25


def test_sat_depth_permute_gate_ordering_simple_paths_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=True,
            minimize="cx-depth",
            solver="pysat-cd19",
            bidirectional=False,
            gate_ordering=True,
            simple_path_restrictions=True,
        )
    ).circuit

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    assert cx_depth == 21


# simple aux with gate ordering + simple paths + disabled qubits :


def test_sat_gates_permute_gate_ordering_simple_paths_disable_unused_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=True,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=False,
            gate_ordering=True,
            simple_path_restrictions=True,
            disable_unused=True,
        )
    ).circuit

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 25


def test_sat_depth_permute_gate_ordering_simple_paths_disable_unused_barenco_tof_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            model="sat",
            qubit_permute=True,
            minimize="cx-depth",
            solver="pysat-cd19",
            bidirectional=False,
            gate_ordering=True,
            simple_path_restrictions=True,
            disable_unused=True,
        )
    ).circuit

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    assert cx_depth == 21


def test_planning_gates_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            encoding="gate_optimal",
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


def test_planning_cnot_optimal_ecai24():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform=None,
            slicing="clifford",
            encoding="cnot_optimal",
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


def test_sat_gates_disable_unused_barenco_tof_3_melbourne():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform="melbourne",
            slicing="clifford",
            model="sat",
            qubit_permute=False,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=True,  # Bi-directional is important here
            disable_unused=True,
        )
    ).circuit

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 2
    assert cx == 31


def test_sat_depth_disable_unused_barenco_tof_3_melbourne():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm"
    )
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform="melbourne",
            slicing="clifford",
            model="sat",
            qubit_permute=False,
            minimize="cx-depth",
            solver="pysat-cd19",
            bidirectional=True,  # Bi-directional is important here
            disable_unused=True,
        )
    ).circuit

    # Asserts
    cx_depth = get_cx_depth_swaps_as_3cx(circuit)
    assert cx_depth == 32


def test_sat_qubits_gates_ecai_24_SR_linear():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform="line-4",
            model="sat",
            slicing="clifford",
            qubit_permute=False,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=True,  # Bi-directional is important here
            search_strategy="unbounded-forward",
        )
    ).circuit

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 7


def test_sat_qubits_gates_backward_ecai_24_SR_linear():
    circuit_in = QuantumCircuit.from_qasm_file(f"{EXAMPLES_DIR}/ecai24_S+R.qasm")
    # Compute circuit and opt_val
    circuit = peephole_synthesis(
        **generate_peephole_options(
            circuit=circuit_in,
            platform="line-4",
            model="sat",
            slicing="clifford",
            qubit_permute=False,
            minimize="cx-count",
            solver="pysat-cd19",
            bidirectional=True,  # Bi-directional is important here
            search_strategy="backward",
        )
    ).circuit

    # Asserts (these are wrt. considering swaps as swaps)
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 7


"""
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
"""
