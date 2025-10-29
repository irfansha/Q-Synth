# Required imports
from qsynth.layout_synthesis_wrapper import layout_synthesis
from Tests.test_utils import (
    CIRCUITS_DIR,
    generate_wrapper_options,
    count_swaps_cx,
    count_depth_cx_depth,
)
from qiskit import QuantumCircuit


# Repeated tests for layout synthesis only
def test_melbourne_sat_vbe_adder_3():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/vbe_adder_3.qasm"
    )
    # Compute circuit and opt_val
    result = layout_synthesis(
        **generate_wrapper_options(
            circuit=circuit_in,
            platform="melbourne",
            model="sat",
            metric="cx-count",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=False,
            bridge=False,
        )
    )

    circuit = result.circuit
    opt_val = result.swap_count
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 8
    assert cx == 50


def test_sycamore_sat_mod5mils_65():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm"
    )
    # Compute circuit and opt_val for
    result = layout_synthesis(
        **generate_wrapper_options(
            circuit=circuit_in,
            platform="sycamore",
            model="sat",
            metric="cx-count",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=False,
            bridge=True,
        )
    )

    circuit = result.circuit
    opt_val = result.swap_count
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 1
    assert cx == 25


def test_sycamore_sat_mod5mils_65_relaxed():
    circuit_in = QuantumCircuit.from_qasm_file(
        f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm"
    )
    # Compute circuit and opt_val
    result = layout_synthesis(
        **generate_wrapper_options(
            circuit=circuit_in,
            platform="sycamore",
            model="sat",
            metric="cx-count",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=True,
            bridge=False,
        )
    )

    circuit = result.circuit
    opt_val = result.swap_count
    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 4
    assert cx == 16


# Run using depth optimal synthesis
def test_tenerife_sat_adder_cadical153_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/adder.qasm")
    # Compute circuit and opt_val
    result = layout_synthesis(
        **generate_wrapper_options(
            circuit=circuit_in,
            platform="tenerife",
            model="sat",
            metric="depth",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=False,
            relaxed=False,
            bridge=False,
        )
    )

    circuit = result.circuit
    opt_val = result.opt_val
    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 15
    assert depth == 13


def test_melbourne_sat_qaoa5_depth():
    circuit_in = QuantumCircuit.from_qasm_file(f"{CIRCUITS_DIR}/Standard/qaoa5.qasm")
    # Compute circuit and opt_val
    result = layout_synthesis(
        **generate_wrapper_options(
            circuit=circuit_in,
            platform="melbourne",
            model="sat",
            metric="depth",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=False,
            bridge=False,
        )
    )

    circuit = result.circuit
    opt_val = result.opt_val
    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 14
    assert depth == 14
