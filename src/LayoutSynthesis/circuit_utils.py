# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumRegister
from qiskit.circuit import Qubit


# Return logical qubit bit_idx of gate gate_idx
# TODO: find the proper way to do this using find_bit
def gate_get_qubit(gate, bit_idx):
    return gate.qubits[bit_idx]._index


# Return a new gate with a modified qubit
# TODO: find the proper way to do this
def gate_set_qubit(gate, bit_idx, num_qubits):

    # Using .replace instead of settings qubits directly
    return gate.replace(qubits=(Qubit(QuantumRegister(num_qubits, "q"), bit_idx),))


# Return a new gate with a modified qubit
# TODO: find the proper way to do this
def gate_set_qubits(gate, bit_idx0, bit_idx1, num_qubits):

    # Using .replace instead of settings qubits directly
    return gate.replace(
        qubits=(
            Qubit(QuantumRegister(num_qubits, "q"), bit_idx0),
            Qubit(QuantumRegister(num_qubits, "q"), bit_idx1),
        )
    )


# return a list of all CNOT gates
def all_cx_gates(circuit):
    list_cx_gates = []
    for gate_idx in range(len(circuit)):
        if circuit[gate_idx].operation.name == "cx":
            list_cx_gates.append(gate_idx)
    return list_cx_gates


# compute and return strict dependencies between CNOT gates (according to standard DAG)
def strict_dependencies(circuit, verbose=0):
    # for each logical qubit, we maintain the current dependency
    current_dependency = {}
    for cur_lqubit in range(len(circuit.qubits)):
        current_dependency[cur_lqubit] = []

    if verbose > 2:
        print("Analyzing strict dependencies one by one:")
        print("==============================================")

    # using the current dependencies, we create a dependency map:
    cnot_depends = {}
    for gate_idx in range(len(circuit)):
        gate = circuit[gate_idx]
        if len(gate.qubits) == 2:
            # for now asserting every 2 qubit operation is "cx":
            if gate.operation.name != "cx":
                print(
                    f"Error: currently, Q-Synth assumes CNOT is the only binary operators, found '{gate.operation.name}'"
                )
                exit(-1)
            ctrl = gate_get_qubit(gate, 0)
            data = gate_get_qubit(gate, 1)
            # first gathering current dependency:
            cnot_depends[gate_idx] = (
                current_dependency[ctrl],
                current_dependency[data],
            )
            # updating current dependency on both input qubits:
            current_dependency[ctrl] = [gate_idx]
            current_dependency[data] = [gate_idx]
            if verbose > 2:
                print(
                    f"CX gate {gate_idx} depends on:",
                    current_dependency[ctrl],
                    current_dependency[data],
                )
        else:
            if len(gate.qubits) != 1:
                print(
                    f"Error: can only handle unary gates and CX gates. Found {gate.operation.name} on {len(gate.qubits)} qubits"
                )
                exit(-1)
    if verbose > 2:
        print("=========================================")
    return cnot_depends


# z_phase gates commute over the control bit of CNOTS
def z_phase(gate):
    return gate.operation.name in ["p", "z", "rz", "s", "sdg", "t", "tdg", "i"]


# x_phase gates commute over the data bit of CNOTS
def x_phase(gate):
    return gate.operation.name in ["x", "rx", "sx", "sxdg", "i"]


# compute relaxed dependencies between CNOT gates (according to permutation rules)
def relaxed_dependencies(circuit, verbose=0):

    prev_block = dict()  # CNOT gates in previous block per qubit
    this_block = dict()  # CNOT gates in current block per qubit
    status = dict()  # status of current block per qubit (None, 'Ctrl' or 'Data')
    cnot_depends = dict()  # all (relaxed) dependencies

    # We initialize all blocks empty and status None
    for qubit in range(len(circuit.qubits)):
        prev_block[qubit] = []
        this_block[qubit] = []
        status[qubit] = None

    if verbose > 2:
        print("Analyzing relaxed dependencies one by one:")
        print("==============================================")

    for gate_idx in range(len(circuit)):
        gate = circuit[gate_idx]

        # take care of unary gates
        if len(gate.qubits) == 1:
            qubit = gate_get_qubit(gate, 0)
            if status[qubit] == "Ctrl" and not z_phase(gate):
                status[qubit] = None
            if status[qubit] == "Data" and not x_phase(gate):
                status[qubit] = None
            # check if we should start a new block
            if status[qubit] == None and len(this_block[qubit]) > 0:
                prev_block[qubit] = this_block[qubit]
                this_block[qubit] = []
            if verbose > 2:
                print(f"unary gate {gate_idx} ({gate.operation.name}) on qubit {qubit}")
                print(f"  status {qubit}: {status[qubit]}.")
        else:
            # for now we only handle binary CX gates
            assert gate.operation.name == "cx" and len(gate.qubits) == 2
            ctrl = gate_get_qubit(gate, 0)
            data = gate_get_qubit(gate, 1)
            if status[ctrl] in ("Ctrl", None):
                this_block[ctrl].append(gate_idx)
            else:
                prev_block[ctrl] = this_block[ctrl]
                this_block[ctrl] = [gate_idx]
            if status[data] in ("Data", None):
                this_block[data].append(gate_idx)
            else:
                prev_block[data] = this_block[data]
                this_block[data] = [gate_idx]
            status[ctrl] = "Ctrl"
            status[data] = "Data"
            cnot_depends[gate_idx] = (prev_block[ctrl], prev_block[data])
            if verbose > 2:
                print(
                    f"CX gate {gate_idx} depends on ctrl {ctrl}: {prev_block[ctrl]}, data {data}: {prev_block[data]}"
                )
                print(
                    f"  status {ctrl}: {status[ctrl]}. status {data}: {status[data]}. "
                )
    if verbose > 2:
        print("==============================================")
    return cnot_depends


# Compute and return a circuit, canceling CNOTS with the same dependencies
def cancel_cnots(circuit, cnot_depends, verbose=0):
    circuit = circuit.copy()  # return a modified copy of the circuit
    cancel = dict()
    canceled = []
    for k, v in cnot_depends.items():
        ctrl = gate_get_qubit(circuit[k], 0)
        data = gate_get_qubit(circuit[k], 1)
        cnotid = (ctrl, data, (tuple(v[0]), tuple(v[1])))
        if cnotid in cancel:
            if verbose > 1:
                (ctrl, data, gate) = cancel[cnotid]
                print(f"CANCEL cnot-gates: {k} and {gate} on qubits ({ctrl},{data})")
            canceled.append(k)
            canceled.append(cancel[cnotid][2])
            del cancel[cnotid]
        else:
            cancel[cnotid] = (ctrl, data, k)
    canceled.sort(reverse=True)  # should delete gates from HIGH to LOW index
    if verbose > 0 and len(canceled) > 0:
        print(f"Canceled {len(canceled)} CNOT gates")
    for x in canceled:
        circuit.data.pop(x)
    return circuit
