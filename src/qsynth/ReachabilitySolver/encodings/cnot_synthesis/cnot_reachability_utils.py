import numpy as np
from qiskit import QuantumCircuit

from qsynth.CliffordSynthesis.circuit_utils import compute_cnotdepth_swaps_as_3cx
from qsynth.ReachabilitySolver.framework.reachability_encoding import Variable


def get_used_qubits(circuit: QuantumCircuit) -> set[int]:
    """
    Returns a set of all qubits used as input to a gate in the given circuit.
    """
    used_qubits = set()
    for gate in circuit.data:
        if gate.name == "barrier":
            continue
        indices = [ circuit.find_bit(q).index for q in gate.qubits ]
        for index in indices:
            used_qubits.add(index)
    return used_qubits


def get_goal_matrix_from_cnot_circuit(circuit):
    """
    Computes the goal matrix from the given CNOT circuit by applying each CNOT gate and SWAP gate as column
    additions and column swaps of the parity matrix, beginning with the identity matrix.
    """
    number_of_qubits = circuit.num_qubits
    goal_matrix = np.eye(number_of_qubits, dtype=int)

    for circuit_instruction in circuit.data:
        if circuit_instruction.name == "cx":
            ctrl, trg = [circuit.find_bit(q).index for q in circuit_instruction.qubits]
            goal_matrix[:, trg] = (goal_matrix[:, trg] + goal_matrix[:, ctrl]) % 2
        elif circuit_instruction.name == "swap":
            i, j = [circuit.find_bit(q).index for q in circuit_instruction.qubits]
            goal_matrix[:, [i, j]] = goal_matrix[:, [j, i]]
        else:
            raise ValueError(f"Unsupported gate: {circuit_instruction.name}")

    return goal_matrix


def get_cx_sequence_from_action_sequence(action_sequence, metric) -> list[list[tuple[int, int]]]:
    """
    Given an action sequence, compute a list of lists of CNOT gates as (ctrl, trg) pairs for each time step.
    The action_sequence should be a list of the true action variables at each time step. If the metrix is cx-count,
    the action sequence is assumed to contain one ctrl and one trg variable at each time step. If the metric is
    cx-depth, the action sequence is assumed to contain only cnot variables (at least one for each time step).
    """
    cx_sequence = []
    for action_vars in action_sequence:
        if metric == "cx-count":
            ctrl_qubit, trg_qubit = None, None
            for var in action_vars:
                if var.name == "ctrl":
                    ctrl_qubit = var.params[0]
                elif var.name == "trg":
                    trg_qubit = var.params[0]
            if ctrl_qubit is not None and trg_qubit is not None:
                cx_sequence.append([(ctrl_qubit, trg_qubit)])
        else:
            # Metric is cx-depth
            cnots = []
            for var in action_vars:
                if var.name != "cnot": continue
                ctrl_qubit, trg_qubit = var.params
                cnots.append((ctrl_qubit, trg_qubit))
            cx_sequence.append(cnots)

    return cx_sequence


def get_initial_state_matrix_from_variables(num_qubits, reachability_solution):
    """
    Computes the initial state matrix from the given ReachabilitySolution by reading the state variables at time 0.
    """
    initial_state_matrix = np.zeros((num_qubits, num_qubits))
    for var in reachability_solution.initial_state:
        if var.name == "m":
            i, j = var.params
            assert var.time_step == 0, f"Initial state has variable with t={var.time_step}"
            initial_state_matrix[i, j] = 1

    assert_one_per_row_and_col(initial_state_matrix)
    return initial_state_matrix


def add_trailing_swaps(circuit: QuantumCircuit, final_mapping: dict[int, int]):
    """
    Append the minimal number of SWAP gates to the input circuit changing the final mapping of qubit indices to
    a 1:1 mapping.
    """
    swaps = []
    mapping = final_mapping.copy()
    for i in range(circuit.num_qubits):
        while mapping[i] != i:
            j = mapping[i]
            mapping[i] = mapping[j]
            mapping[j] = j
            swaps.append((i, j))
    for i, j in reversed(swaps):
        circuit.swap(i, j)


def compute_upper_bound(circuit: QuantumCircuit, metric: str, has_coupling_graph: bool = False) -> int:
    """
    Computes the upper bound on the number of time steps for the CnotReachabilityEncoding of the given circuit.
    """
    if metric == "cx-count":
        # Upper bound is no. of CNOTs in original circuit
        upper_bound = sum([1 if gate.name == "cx" else 3 for gate in circuit.data])
        # Or n(n-1) if it is smaller, and we are running without layout restrictions
        if not has_coupling_graph:
            upper_bound = min(upper_bound, circuit.num_qubits * (circuit.num_qubits - 1))
    else:
        upper_bound = compute_cnotdepth_swaps_as_3cx(circuit, verbose=-1)
    return upper_bound


def check_circuit_equivalence_of_cnot_circuits(original_circuit, optimized_circuit):
    goal_matrix1 = get_goal_matrix_from_cnot_circuit(original_circuit)
    goal_matrix2 = get_goal_matrix_from_cnot_circuit(optimized_circuit)
    assert np.all(goal_matrix1 == goal_matrix2), \
        (f"Goal matrix\n"
         f"{goal_matrix1}\n"
         f"is different from goal matrix\n"
         f"{goal_matrix2}\n\n"
         f"The corresponding circuits are:"
         f"{original_circuit}\n"
         f"and\n"
         f"{optimized_circuit}")


def count_cx_swaps_as_3_cx(circuit: QuantumCircuit):
    return circuit.count_ops().get("cx", 0) + 3 * circuit.count_ops().get("swap", 0)


def assert_one_per_row_and_col(matrix):
    assert np.all(np.sum(matrix, axis=0) == 1), "Not exactly one '1' in every column"
    assert np.all(np.sum(matrix, axis=1) == 1), "Not exactly one '1' in every row"


def m(r, c, t):
    return Variable(name="m", params=[r, c], time_step=t)


def p(j, k, t):
    return Variable(name="p", params=[j, k], time_step=t)


def ctrl(i, t):
    return Variable(name="ctrl", params=[i], time_step=t)


def trg(i, t):
    return Variable(name="trg", params=[i], time_step=t)


def cnot(i, j, t):
    return Variable(name="cnot", params=[i, j], time_step=t)