# Required imports
from src.peephole_cnotsynthesis import peephole_cnotsynthesis
from Tests.test_utils import (
    EXAMPLES_DIR,
    ECAI_DIR,
    generate_peephole_options,
    count_swaps_cx,
    count_depth_cx_depth,
)


def test_sat_gates_ecai24():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
            platform=None,
            model="sat",
            qubit_permute=False,
            minimize="gates",
            solver="cd",
            bidirectional=False,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_planning_gates_fd_ecai24():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
            platform=None,
            model="planning",
            qubit_permute=False,
            minimize="gates",
            solver="fd-ms",
            bidirectional=False,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_planning_gates_madagascar_ecai24():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
            platform=None,
            model="planning",
            qubit_permute=False,
            minimize="gates",
            solver="madagascar",
            bidirectional=False,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 3


def test_sat_depth_ecai24():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
            platform=None,
            model="sat",
            qubit_permute=False,
            minimize="depth",
            solver="cd",
            bidirectional=False,
        )
    )

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 3
    assert cx_depth == 3


def test_planning_depth_fd_ecai24():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
            platform=None,
            model="planning",
            qubit_permute=False,
            minimize="depth",
            solver="fd-ms",
            bidirectional=False,
        )
    )

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 3
    assert cx_depth == 3


def test_planning_depth_madagascar_ecai24():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{EXAMPLES_DIR}/ecai24.qasm",
            platform=None,
            model="planning",
            qubit_permute=False,
            minimize="depth",
            solver="madagascar",
            bidirectional=False,
        )
    )

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 3
    assert cx_depth == 3


def test_sat_gates_qubits_barenco_tof_3():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm",
            platform=None,
            model="sat",
            qubit_permute=True,
            minimize="gates",
            solver="cd",
            bidirectional=False,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 26


def test_sat_gates_barenco_tof_3_melbourne():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{ECAI_DIR}/permuted_mapped/barenco_tof_3.qasm",
            platform="melbourne",
            model="sat",
            qubit_permute=False,
            minimize="gates",
            solver="cd",
            bidirectional=True,  # Bi-directional is important here
        )
    )

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
#             minimize="gates",
#             solver="cd",
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
#             minimize="gates",
#             solver="cd",
#             bidirectional=True  # Bi-directional is important here
#         )
#     )

#     # Asserts (these are wrt. considering swaps as swaps)
#     swaps, cx = count_swaps_cx(circuit)
#     assert swaps == 0
#     assert cx == 6


def test_qbf_gates_barenco_tof_3():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{ECAI_DIR}/tpar-optimized/barenco_tof_3.qasm",
            platform=None,
            model="qbf",
            qubit_permute=False,
            minimize="gates",
            solver="caqe",
            bidirectional=False,
        )
    )

    # Asserts
    swaps, cx = count_swaps_cx(circuit)
    assert swaps == 0
    assert cx == 41


def test_qbf_depth_qft_4():

    # Compute circuit and opt_val
    circuit = peephole_cnotsynthesis(
        **generate_peephole_options(
            circuit=f"{ECAI_DIR}/tpar-optimized/qft_4.qasm",
            platform=None,
            model="qbf",
            qubit_permute=False,
            minimize="depth",
            solver="caqe",
            bidirectional=True,
        )
    )

    # Asserts
    depth, cx_depth = count_depth_cx_depth(circuit)
    assert depth == 172
    assert cx_depth == 77
