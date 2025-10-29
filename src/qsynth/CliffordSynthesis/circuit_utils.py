# Irfansha Shaik, Aarhus, 15 January 2024.

from qiskit import QuantumCircuit
from qsynth.LayoutSynthesis.circuit_utils import gate_get_qubit


# Print the actions from the plan
def extract_circuit(plan, t, options, num_qubits):
    qubit_map = {}
    if "swaps" in options.encoding:
        for i in range(num_qubits):
            qubit_map[i] = i
    opt_circuit = QuantumCircuit(num_qubits)
    for k in range(1, t + 1):
        cur_action = plan[k - 1]
        # handling weight cnot dummy aciton:
        if "dummy" in cur_action[0]:
            assert options.encoding == "gate_weighted"
            continue
        qubit1 = int(cur_action[1][1:])
        if cur_action[0] == "cnot":
            qubit2 = int(cur_action[2][1:])
            opt_circuit.cx(qubit1, qubit2)
        elif cur_action[0] == "s-gate" or cur_action[0] == "s-gate-last":
            opt_circuit.s(qubit1)
        elif cur_action[0] == "h-gate" or cur_action[0] == "h-gate-last":
            opt_circuit.h(qubit1)
        elif cur_action[0] == "sh-gate" or cur_action[0] == "sh-gate-last":
            opt_circuit.s(qubit1)
            opt_circuit.h(qubit1)
        elif cur_action[0] == "hs-gate" or cur_action[0] == "hs-gate-last":
            opt_circuit.h(qubit1)
            opt_circuit.s(qubit1)
        elif cur_action[0] == "hsh-gate-last":
            opt_circuit.h(qubit1)
            opt_circuit.s(qubit1)
            opt_circuit.h(qubit1)
        elif cur_action[0] == "z-gate":
            opt_circuit.z(qubit1)
        elif cur_action[0] == "y-gate":
            opt_circuit.y(qubit1)
        elif cur_action[0] == "x-gate":
            opt_circuit.x(qubit1)
        elif cur_action[0] == "map-final":
            qubit2 = int(cur_action[2][1:])
            qubit_map[qubit2] = qubit1
        elif cur_action[0] == "swap":
            qubit2 = int(cur_action[2][1:])
            if options.qubit_permute:
                opt_circuit.swap(qubit1, qubit2)
            else:
                cur_logical_qubit1 = qubit_map[qubit1]
                cur_logical_qubit2 = qubit_map[qubit2]
                # swapping:
                qubit_map[qubit1] = cur_logical_qubit2
                qubit_map[qubit2] = cur_logical_qubit1
        elif cur_action[0] == "map-initial":
            row = int(cur_action[1][1:])
            qubit1 = int(cur_action[3][1:])
            qubit_map[qubit1] = row
        else:
            assert (
                cur_action[0] == "choose"
                or cur_action[0] == "i-gate"
                or cur_action[0] == "i-gate-last"
                or cur_action[0] == "disable"
            )

    return opt_circuit, qubit_map


# Return a copy of the mapped circuit including measurements
def get_measured_circuit(circuit, qubit_map):
    circuit_copy = circuit.copy()
    circuit_copy.measure_all()
    for i in range(len(qubit_map.items())):
        del circuit_copy.data[-1]
    # print(circuit_copy)
    for q1, q2 in qubit_map.items():
        circuit_copy.measure([q2], [q1])
    return circuit_copy


# compute circuit cost:
def compute_cnot_cost(qc):
    num_2q_gates = 0
    num_cx_gates = 0
    # counting number of cx gates:
    if "cx" in qc.count_ops().keys():
        num_2q_gates += qc.count_ops()["cx"]
        num_cx_gates += qc.count_ops()["cx"]
    if "cy" in qc.count_ops().keys():
        num_2q_gates += qc.count_ops()["cy"]
        # we assume cy gate can be decomposed to cx gate with single qubit gates:
        num_cx_gates += qc.count_ops()["cy"]
    if "cz" in qc.count_ops().keys():
        num_2q_gates += qc.count_ops()["cz"]
        # we assume cz gate can be decomposed to cx gate with single qubit gates:
        num_cx_gates += qc.count_ops()["cz"]
    # if a swap exists then we consider it as 3 cx:
    if "swap" in qc.count_ops():
        num_2q_gates += qc.count_ops()["swap"]
        num_cx_gates += 3 * (qc.count_ops()["swap"])
    return num_cx_gates


# compute number of cnots (not swaps, only cnots):
def compute_cnot_without_swaps_cost(qc):
    num_cx_gates = 0
    # counting number of cx gates:
    if "cx" in qc.count_ops().keys():
        num_cx_gates += qc.count_ops()["cx"]
    if "cy" in qc.count_ops().keys():
        # we assume cy gate can be decomposed to cx gate with single qubit gates:
        num_cx_gates += qc.count_ops()["cy"]
    if "cz" in qc.count_ops().keys():
        # we assume cz gate can be decomposed to cx gate with single qubit gates:
        num_cx_gates += qc.count_ops()["cz"]
    return num_cx_gates


# we do not count swap gates depth, we ignore every other 2-qubit gate:
def compute_cnot_depth(qc):
    num_qubits = len(qc.qubits)
    cx_circuit = QuantumCircuit(num_qubits)
    for gate in qc:
        if len(gate.qubits) == 2 and (
            gate.operation.name == "cx"
            or gate.operation.name == "cy"
            or gate.operation.name == "cz"
        ):
            cx_circuit.append(gate)
    # print(cx_circuit)
    return cx_circuit.depth()


def replace_swaps_with_3cx(circuit, check=0, verbose=0):
    num_qubits = len(circuit.qubits)
    swap_free_circuit = QuantumCircuit(num_qubits, num_qubits)
    for gate in circuit:
        if gate.operation.name == "swap":
            # decomposing swap to 3 cnots:
            q1, q2 = gate_get_qubit(gate, 0), gate_get_qubit(gate, 1)
            swap_free_circuit.cx(q1, q2)
            swap_free_circuit.cx(q2, q1)
            swap_free_circuit.cx(q1, q2)
        else:
            swap_free_circuit.append(gate)
    return swap_free_circuit


# we convert swap to 3 cnots and compute the depth:
def compute_depth_swaps_as_3cx(circuit, check=0, verbose=0):
    swap_free_circuit = replace_swaps_with_3cx(circuit, check, verbose)
    return swap_free_circuit.depth()


# we convert swap to 3 cnots and compute the cnot-depth:
def compute_cnotdepth_swaps_as_3cx(circuit, check=0, verbose=0):
    swap_free_circuit = replace_swaps_with_3cx(circuit, check, verbose)
    return compute_cnot_depth(swap_free_circuit)


def compute_and_print_costs(
    org_circuit, opt_circuit, cnot_minimization=None, verbose=0
):

    initial_cx_gates = compute_cnot_cost(org_circuit)
    if verbose > 1:
        print("Original Circuit: ")
        print(org_circuit)
        print("Initial CNOT gates: ", initial_cx_gates)
        if cnot_minimization == "cx-depth":
            print("Initial depth: ", org_circuit.depth())

    final_cx_gates = compute_cnot_cost(opt_circuit)
    if verbose > 1:
        print("Optimized Circuit: ")
        print(opt_circuit)
        print("Final CNOT gates: ", final_cx_gates)
        if cnot_minimization == "cx-depth":
            print("Final depth: ", opt_circuit.depth())

    return initial_cx_gates, final_cx_gates
