from qiskit import QuantumCircuit, QuantumRegister
from typing import Optional

from qsynth.layout_synthesis_wrapper import layout_synthesis as ls_wrapper

from qsynth.CliffordSynthesis.circuit_utils import (
    compute_cnotdepth_swaps_as_3cx,
)

CIRCUITS_DIR = "Benchmarks/SAT-24"
EXAMPLES_DIR = "Benchmarks/Examples"
ECAI_DIR = "Benchmarks/ECAI-24"


def get_cx_depth_swaps_as_3cx(circuit: QuantumCircuit) -> int:
    return compute_cnotdepth_swaps_as_3cx(circuit)


def get_cx_depth(circuit: QuantumCircuit) -> int:

    num_qubits = circuit.num_qubits
    qubit_name = circuit.qregs[0].name
    new_circuit = QuantumCircuit(QuantumRegister(num_qubits, qubit_name))
    for instr in circuit.data:

        if instr.name == "cx":
            new_circuit.append(instr.operation, qargs=instr.qubits)

    return new_circuit.depth()


def count_depth_cx_depth(circuit: QuantumCircuit) -> tuple[int, int]:
    depth = circuit.remove_final_measurements(inplace=False).depth()
    cx_depth = get_cx_depth(circuit)
    return depth, cx_depth


def count_swaps(circuit: QuantumCircuit) -> int:
    ops = circuit.count_ops()
    if "swap" in ops.keys():
        return ops["swap"]
    else:
        return 0


def count_cx(circuit: QuantumCircuit) -> int:
    ops = circuit.count_ops()
    if "cx" in ops.keys():
        return ops["cx"]
    else:
        return 0


def count_swaps_cx(circuit: QuantumCircuit) -> tuple[int, int]:
    return count_swaps(circuit), count_cx(circuit)


def generate_wrapper_options(
    circuit: str,
    platform: str,
    model: str,
    metric: str,
    solver: str,
    allow_ancillas: bool,
    bidirectional: bool,
    relaxed: bool,
    bridge: bool,
) -> dict[str, any]:

    # Set required options
    options = {
        "circuit_in": circuit,
        "circuit_out": None,
        "platform": platform,
        "model": model,
        "solver": solver,
        "solver_time": 1800,
        "allow_ancillas": allow_ancillas,
        "relaxed": 1 if relaxed else 0,
        "bidirectional": 1 if bidirectional else 0,
        "bridge": 1 if bridge else 0,
        "start": 0,
        "step": 1,
        "end": None,
        "check": 1,
        "verbose": -1,
        "cnot_cancel": 0,
        "cardinality": 1,
        "parallel_swaps": 0,
        "aux_files": "./intermediate_files",
        "metric": metric,
        "coupling_graph": None,
    }

    # Return options
    return options


def generate_layout_options(
    circuit: str,
    platform: str,
    model: str,
    solver: Optional[str],
    allow_ancillas: bool,
    bidirectional: bool,
    relaxed: bool,
    bridges: bool,
) -> dict[str, any]:

    # Set required options
    options = {
        "circuit_in": circuit,
        "circuit_out": None,
        "platform": platform,
        "model": model,
        "solver": solver,
        "solver_time": 1800,
        "allow_ancillas": allow_ancillas,
        "relaxed": 1 if relaxed else 0,
        "bidirectional": 1 if bidirectional else 0,
        "bridge": 1 if bridges else 0,
        "start": 0,
        "step": 1,
        "end": None,
        "check": 1,
        "verbose": -1,
        "cnot_cancel": 0,
        "cardinality": 1,
        "parallel_swaps": 0,
        "aux_files": "./intermediate_files",
        "coupling_graph": None,
    }

    # Return built options
    return options


def generate_subarchitecture_options(
    circuit: str,
    platform: str,
    model: str,
    metric: str,
    solver: Optional[str],
    num_ancillary_qubits: int,
) -> dict[str, any]:

    # Set required options
    options = {
        "circuit_in": circuit,
        "circuit_out": None,
        "platform": platform,
        "model": model,
        "metric": metric,
        "solver": solver,
        "solver_time": 1800,
        "num_ancillary_qubits": num_ancillary_qubits,
        "relaxed": 0,
        "bidirectional": 1,
        "bridge": 0,
        "start": 0,
        "step": 1,
        "end": None,
        "check": 1,
        "verbose": -1,
        "cnot_cancel": 0,
        "cardinality": 1,
        "parallel_swaps": 0,
        "aux_files": "./intermediate_files",
        "layout_synthesis_method": ls_wrapper,
    }

    # Return built options
    return options


def generate_peephole_options(
    circuit: str,
    platform: str,
    slicing: str,
    model: str,
    qubit_permute: Optional[bool],
    minimize: str,
    solver: Optional[str],
    bidirectional: bool,
    encoding: str = None,
    gate_ordering: bool = False,
    simple_path_restrictions: bool = False,
    disable_unused: bool = False,
    time: int = 600,
    search_strategy: str = "forward",
) -> dict[str, any]:

    # Set required options
    options = {
        "circuit_in": circuit,
        "circuit_out": None,
        "slicing": slicing,
        "minimize": minimize,
        "model": model,
        "qubit_permute": qubit_permute,
        "search_strategy": search_strategy,
        "solver": solver,
        "time": time,
        "platform": platform,
        "bidirectional": 1 if bidirectional else 0,
        "encoding": encoding,
        "intermediate_files_path": "./intermediate_files",
        "verbose": -1,
        "check": True,
        "gate_ordering": gate_ordering,
        "simple_path_restrictions": simple_path_restrictions,
        "disable_unused": disable_unused,
    }

    # Return built options
    return options


def generate_depth_options(
    circuit: str,
    platform: str,
    model: str,
    solver: str,
    cx_optimal: bool,
    swap_optimal: bool,
    allow_ancillas: bool,
) -> dict[str, any]:

    options = {
        "circuit_in": circuit,
        "circuit_out": None,
        "platform_name": platform,
        "coupling_graph": None,
        "model": model,
        "solver_name": solver,
        "solver_time": 600,
        "output_initial": None,
        "cx_optimal": cx_optimal,
        "swap_optimal": swap_optimal,
        "allow_ancillas": allow_ancillas,
        "verbose": -1,
        "swap_bound": None,
        "depth_bound": None,
        "check": True,
    }

    return options
