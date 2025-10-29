# Required imports
from qsynth.Subarchitectures.subarchitectures import subarchitecture_mapping
from Tests.test_utils import (
    CIRCUITS_DIR,
    generate_subarchitecture_options,
    count_swaps_cx,
    count_depth_cx_depth,
)
from qiskit import QuantumCircuit


def test_sycamore_sat_4gt13_92():
    # Initialize circuit_in
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/4gt13_92.qasm")

    # Compute circuit and opt_val
    result = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=circuit_in,
            platform="sycamore",
            model="sat",
            metric="cx-count",
            solver="cd19",
            num_ancillary_qubits=2,
        )
    )

    circuit = result.circuit
    opt_val = result.opt_val
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 10
    assert cx == 30


def test_tokyo_sat_mod5mils_65():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm"
    )
    # Compute circuit and opt_val
    result = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=circuit_in,
            platform="tokyo",
            model="sat",
            metric="cx-count",
            solver="cd19",
            num_ancillary_qubits=2,
        )
    )

    circuit = result.circuit
    opt_val = result.opt_val
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 16


def test_eagle_sat_vqe_8_4_5_100():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/VQE/vqe_8_1_5_100.qasm")
    # Compute circuit and opt_val
    result = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=circuit_in,
            platform="eagle",
            model="sat",
            metric="cx-count",
            solver="cd19",
            num_ancillary_qubits=0,
        )
    )

    circuit = result.circuit
    opt_val = result.opt_val
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 3
    assert cx == 18


# Perform some tests with depth as well
def test_tokyo_sat_qaoa5_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    # Compute circuit and opt_val
    result = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=circuit_in,
            platform="tokyo",
            model="sat",
            metric="depth",
            solver="cd19",
            num_ancillary_qubits=2,
        )
    )

    circuit = result.circuit
    opt_val = result.opt_val
    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 14
    assert depth == 14


def test_tokyo_sat_qaoa5_cx_depth_cx_count():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    # Compute circuit and opt_val
    result = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=circuit_in,
            platform="tenerife",
            model="sat",
            metric="cx-depth_cx-count",
            solver="cd19",
            num_ancillary_qubits=-1,
        )
    )

    circuit = result.circuit
    opt_val = result.opt_val
    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    swaps, cx_count = count_swaps_cx(circuit)
    assert opt_val == 10
    assert cx_depth == 7
    assert swaps == 1
