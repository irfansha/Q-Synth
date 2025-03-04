# Required imports
from src.DepthOptimal.depthoptimal import depth_optimal_mapping
from Tests.test_utils import (
    CIRCUITS_DIR,
    generate_depth_options,
    count_swaps_cx,
    count_depth_cx_depth,
)


def test_tenerife_sat_adder():

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="sat",
            solver="cd19",
            cx_optimal=False,
            swap_optimal=False,
            allow_ancillas=True,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 15
    assert depth == 13


def test_melbourne_sat_adder_mcm():

    # For some reason,
    # depth-optimal can only map adder.qasm on tenerife with cd19
    # other sat solvers work fine

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="melbourne",
            model="sat",
            solver="mcm",
            cx_optimal=False,
            swap_optimal=False,
            allow_ancillas=True,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert opt_val == 11
    assert depth == 11


def test_tokyo_sat_qaoa5():

    # For some reason,
    # depth-optimal can only map adder.qasm on tenerife with cd19
    # other sat solvers work fine

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/qaoa5.qasm",
            platform="tokyo",
            model="sat",
            solver="cd19",
            cx_optimal=False,
            swap_optimal=False,
            allow_ancillas=True,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert depth == 14
    assert opt_val == 14


def test_tenerife_sat_adder_cx_depth():

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="sat",
            solver="cd19",
            cx_optimal=True,
            swap_optimal=False,
            allow_ancillas=True,
        )
    )

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    assert opt_val == 10
    assert cx_depth == 7


def test_tenerife_sat_adder_depth_cx_count():

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="sat",
            solver="cd19",
            cx_optimal=False,
            swap_optimal=True,
            allow_ancillas=True,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    swaps, _ = count_swaps_cx(circuit)
    assert opt_val == 15
    assert depth == 13
    assert swaps == 1


def test_tenerife_sat_adder_cx_depth_cx_count():

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="sat",
            solver="cd19",
            cx_optimal=True,
            swap_optimal=True,
            allow_ancillas=True,
        )
    )

    # Asserts
    _, cx_depth = count_depth_cx_depth(circuit)
    swaps, _ = count_swaps_cx(circuit)
    assert opt_val == 10
    assert cx_depth == 7
    assert swaps == 1


def test_tenerife_plan_cost_opt_depth_adder():

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="cost_opt",
            solver="fd-bjolp",
            cx_optimal=False,
            swap_optimal=False,
            allow_ancillas=False,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert depth == 13
    assert opt_val == 15


def test_tenerife_plan_cond_cost_opt_depth_adder():

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="cond_cost_opt",
            solver="fd-ms",
            cx_optimal=False,
            swap_optimal=False,
            allow_ancillas=False,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert depth == 13
    assert opt_val == 15


def test_tenerife_plan_lc_incr_depth_or():

    # Compute circuit and opt_val
    circuit, opt_val = depth_optimal_mapping(
        **generate_depth_options(
            circuit=f"{CIRCUITS_DIR}/Standard/or.qasm",
            platform="tenerife",
            model="lc_incr",
            solver="fd-bjolp",
            cx_optimal=False,
            swap_optimal=False,
            allow_ancillas=False,
        )
    )

    # Asserts
    depth, _ = count_depth_cx_depth(circuit)
    assert depth == 8
    assert opt_val == 8
