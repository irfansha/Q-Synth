# Required imports
from src.Subarchitectures.subarchitectures import subarchitecture_mapping
from Tests.test_utils import (
    CIRCUITS_DIR,
    generate_subarchitecture_options,
    count_swaps_cx,
    count_depth_cx_depth,
)


def test_sycamore_sat_4gt13_92():

    # Compute circuit and opt_val
    circuit, opt_val = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=f"{CIRCUITS_DIR}/Standard/4gt13_92.qasm",
            platform="sycamore",
            model="sat",
            metric="cx-count",
            solver="cd19",
            num_ancillary_qubits=2,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 10
    assert cx == 30


def test_tokyo_sat_mod5mils_65():

    # Compute circuit and opt_val
    circuit, opt_val = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm",
            platform="tokyo",
            model="sat",
            metric="cx-count",
            solver="cd19",
            num_ancillary_qubits=2,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 16


def test_eagle_sat_vqe_8_4_5_100():

    # Compute circuit and opt_val
    circuit, opt_val = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=f"{CIRCUITS_DIR}/VQE/vqe_8_1_5_100.qasm",
            platform="eagle",
            model="sat",
            metric="cx-count",
            solver="cd19",
            num_ancillary_qubits=0,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 3
    assert cx == 18


# Perform some tests with depth as well
def test_tokyo_sat_qaoa5_depth():
    # Compute circuit and opt_val
    circuit, opt_val = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=f"{CIRCUITS_DIR}/Standard/qaoa5.qasm",
            platform="tokyo",
            model="sat",
            metric="depth",
            solver="cd19",
            num_ancillary_qubits=2,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 14
    assert depth == 14


def test_tokyo_sat_qaoa5_cx_depth_cx_count():
    # Compute circuit and opt_val
    circuit, opt_val = subarchitecture_mapping(
        **generate_subarchitecture_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="sat",
            metric="cx-depth-cx-count",
            solver="cd19",
            num_ancillary_qubits=-1,
        )
    )

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    swaps, cx_count = count_swaps_cx(circuit)
    assert opt_val == 10
    assert cx_depth == 7
    assert swaps == 1
