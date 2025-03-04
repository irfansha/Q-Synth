# Required imports
from src.LayoutSynthesis.layout_synthesis import layout_synthesis
from Tests.test_utils import CIRCUITS_DIR, generate_layout_options, count_swaps_cx


def test_melbourne_sat_vbe_adder_3():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/vbe_adder_3.qasm",
            platform="melbourne",
            model="sat",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=False,
            bridges=False,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 8
    assert cx == 50


def test_sycamore_sat_mod5mils_65():

    # Compute circuit and opt_val for
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm",
            platform="sycamore",
            model="sat",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=False,
            bridges=True,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 1
    assert cx == 25


def test_sycamore_sat_mod5mils_65_relaxed():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/mod5mils_65.qasm",
            platform="sycamore",
            model="sat",
            solver="cd19",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=True,
            bridges=False,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 4
    assert cx == 16


# Perform some planning tests
def test_melbourne_global_adder():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="melbourne",
            model="global",
            solver="fd-bjolp",
            allow_ancillas=False,
            bidirectional=True,
            relaxed=False,
            bridges=False,
        )
    )

    # Asserts
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 0
    assert opt_val == 0


def test_tenerife_global_adder():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/adder.qasm",
            platform="tenerife",
            model="global",
            solver="fd-ms",
            allow_ancillas=False,
            bidirectional=True,
            relaxed=False,
            bridges=False,
        )
    )

    # Asserts
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 1
    assert opt_val == 1


def test_melbourne_local_qaoa5():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/qaoa5.qasm",
            platform="melbourne",
            model="local",
            solver="fd-bjolp",
            allow_ancillas=False,
            bidirectional=True,
            relaxed=False,
            bridges=False,
        )
    )

    # Asserts
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 0
    assert opt_val == 0


def test_tenerife_lifted_4gt13_92():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/4gt13_92.qasm",
            platform="tenerife",
            model="lifted",
            solver="fd-bjolp",
            allow_ancillas=False,
            bidirectional=True,
            relaxed=False,
            bridges=False,
        )
    )

    # Asserts
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 0
    assert opt_val == 0


def test_star_lifted_madagascar_or():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/or.qasm",
            platform="star-4",
            model="lifted",
            solver="madagascar",
            allow_ancillas=False,
            bidirectional=True,
            relaxed=False,
            bridges=False,
        )
    )

    # Asserts
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 2
    assert opt_val == 2


def test_cycle_local_relaxed_madagascar_or():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/or.qasm",
            platform="cycle-4",
            model="local",
            solver="madagascar",
            allow_ancillas=True,
            bidirectional=True,
            relaxed=True,
            bridges=False,
        )
    )

    # Asserts
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 1
    assert opt_val == 1


def test_OCQ_unidirectional_or():

    # Compute circuit and opt_val
    circuit, opt_val = layout_synthesis(
        **generate_layout_options(
            circuit=f"{CIRCUITS_DIR}/Standard/or.qasm",
            platform="OCQ-tokyo",
            model="local",
            solver="madagascar",
            allow_ancillas=False,
            bidirectional=False,
            relaxed=False,
            bridges=False,
        )
    )

    # Asserts
    swaps, _ = count_swaps_cx(circuit)
    assert swaps == 4
    assert opt_val == 4
