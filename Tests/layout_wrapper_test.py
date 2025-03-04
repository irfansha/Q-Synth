# Required imports
from src.layout_synthesis_wrapper import layout_synthesis
from Tests.test_utils import (
    CIRCUITS_DIR,
    generate_wrapper_options,
    count_swaps_cx,
    count_depth_cx_depth,
)


# Repeated tests for layout synthesis only
def test_melbourne_sat_vbe_adder_3():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_wrapper_options(
            circuit=f"{CIRCUITS_DIR}/Standard/vbe_adder_3.qasm",
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

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 8
    assert cx == 50


def test_sycamore_sat_mod5mils_65():

    # Compute circuit and opt_val for
    circuit, opt_val = layout_synthesis(
        **generate_wrapper_options(
            circuit=f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm",
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

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 1
    assert cx == 25


def test_sycamore_sat_mod5mils_65_relaxed():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_wrapper_options(
            circuit=f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm",
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

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 4
    assert cx == 16


# Run using depth optimal synthesis
def test_tenerife_sat_adder_cadical153_depth():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_wrapper_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
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

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 15
    assert depth == 13


def test_melbourne_sat_qaoa5_depth():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_wrapper_options(
            circuit=f"{CIRCUITS_DIR}/Standard/qaoa5.qasm",
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

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 14
    assert depth == 14
