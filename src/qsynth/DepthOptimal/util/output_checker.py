from qsynth.DepthOptimal.util.circuits import (
    PhysicalQubit,
    LogicalQubit,
    gate_line_dependency_mapping,
    line_gate_mapping,
    remove_all_non_cx_gates,
    remove_all_non_swap_gates,
)
from qsynth.DepthOptimal.platform import Platform
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Qubit

# TODO: Fix mqt.qcec dependency issues
# from mqt.qcec import verify, EquivalenceCriterion


def connectivity_check(
    output_circuit: QuantumCircuit,
    platform: Platform,
) -> bool:
    cx_only_circuit = remove_all_non_cx_gates(output_circuit)
    cx_gate_line = gate_line_dependency_mapping(cx_only_circuit)
    swap_only_circuit = remove_all_non_swap_gates(output_circuit)
    swap_gate_line = gate_line_dependency_mapping(swap_only_circuit)

    for _, (_, qubits) in cx_gate_line.items():
        q1 = qubits[0]
        q2 = qubits[1]
        if (q1, q2) not in platform.connectivity_graph:
            print(f"Connectivity check failed (CX): ({q1}, {q2}) not in platform.")
            return False
    for _, (_, qubits) in swap_gate_line.items():
        q1 = qubits[0]
        q2 = qubits[1]
        if (q1, q2) not in platform.connectivity_graph:
            print(f"Connectivity check failed (SWAP): ({q1}, {q2}) not in platform.")
            return False

    return True


def equality_check(
    input_circuit: QuantumCircuit,
    output_circuit: QuantumCircuit,
    initial_mapping: dict[LogicalQubit, PhysicalQubit],
    ancillaries: bool,
) -> bool:
    output_mapping = line_gate_mapping(output_circuit)
    topo_sort_gates: list[tuple[str, list[int]]] = []
    while not all(len(output_mapping[line]) == 0 for line in output_mapping.keys()):
        for line in output_mapping.keys():
            gates = output_mapping[line]
            for _, gate_name in gates:
                if gate_name.startswith("swap") or gate_name.startswith("cx"):
                    break
                else:
                    topo_sort_gates.append((gate_name, [line]))
                    output_mapping[line] = output_mapping[line][1:]

        waiting: dict[int, int] = {}
        for line in output_mapping.keys():
            gates = output_mapping[line]
            if gates:
                binary_num, binary_name = gates[0]
                if binary_num in waiting.keys():
                    other_line = waiting[binary_num]
                    new_binary_name = "swap" if binary_name.startswith("swap") else "cx"
                    if binary_name.startswith("cx0"):
                        topo_sort_gates.append((new_binary_name, [line, other_line]))
                    else:
                        topo_sort_gates.append((new_binary_name, [other_line, line]))
                    output_mapping[line] = output_mapping[line][1:]
                    output_mapping[other_line] = output_mapping[other_line][1:]
                else:
                    waiting[binary_num] = line

    input_mapping = line_gate_mapping(input_circuit)
    reverse_initial: dict[int, int] = {p.id: l.id for l, p in initial_mapping.items()}

    for phys_gate_name, phys_lines in topo_sort_gates:
        binary = len(phys_lines) == 2
        if binary:
            phys_control = phys_lines[0]
            phys_target = phys_lines[1]

            if phys_gate_name.startswith("swap"):
                if ancillaries and (
                    phys_control not in reverse_initial.keys()
                    or phys_target not in reverse_initial.keys()
                ):
                    if phys_control not in reverse_initial.keys():
                        reverse_initial[phys_control] = reverse_initial[phys_target]
                        del reverse_initial[phys_target]
                    else:
                        reverse_initial[phys_target] = reverse_initial[phys_control]
                        del reverse_initial[phys_control]
                else:
                    tmp = reverse_initial[phys_control]
                    reverse_initial[phys_control] = reverse_initial[phys_target]
                    reverse_initial[phys_target] = tmp
                continue

            logi_control = reverse_initial[phys_control]
            logi_target = reverse_initial[phys_target]
            logi_control_gates = input_mapping[logi_control]
            logi_target_gates = input_mapping[logi_target]

            if logi_control_gates and logi_target_gates:
                _, logi_control_gate_name = logi_control_gates[0]
                _, logi_target_gate_name = logi_target_gates[0]

                logi_names_equiv = logi_control_gate_name.startswith(
                    "cx0"
                ) and logi_target_gate_name.startswith("cx1")
                if logi_names_equiv:
                    phys_logi_names_equiv = phys_gate_name.startswith(
                        "cx"
                    ) and logi_control_gate_name.startswith("cx")
                    if phys_logi_names_equiv:
                        input_mapping[logi_target] = input_mapping[logi_target][1:]
                        input_mapping[logi_control] = input_mapping[logi_control][1:]
                        continue
                    else:
                        print(
                            f"Types of gates do not match: {phys_gate_name} (on p_{phys_control} and p_{phys_target}) and {logi_control_gate_name} (on q_{logi_control} and q_{logi_target})."
                        )
                        return False
                else:
                    print(
                        f"Expected {phys_gate_name} at q_{logi_control} (p_{phys_control}) and q_{logi_target} (p_{phys_target}), but found {logi_control_gate_name} and {logi_target_gate_name}."
                    )
                    return False
            else:
                if not logi_control_gates:
                    print(
                        f"Expected a {phys_gate_name} gate on q_{logi_control}, but found nothing."
                    )
                else:
                    print(
                        f"Expected a {phys_gate_name} gate on q_{logi_target}, but found nothing."
                    )
                return False

        else:
            phys_line = phys_lines[0]
            logi_line = reverse_initial[phys_line]
            logi_gates = input_mapping[logi_line]
            if logi_gates:
                _, logi_gate_name = logi_gates[0]
                names_equiv = phys_gate_name == logi_gate_name
                if names_equiv:
                    input_mapping[logi_line] = input_mapping[logi_line][1:]
                    continue
                else:
                    print(
                        f"Types of gates do not match: {phys_gate_name} (on p_{phys_line}) and {logi_gate_name} (on q_{logi_line})."
                    )
                    return False
            else:
                print(
                    f"Expected a {phys_gate_name} gate on q_{logi_line}, but found nothing."
                )
                return False

    return True


# TODO:
# Setup mqt.qcec
# def check_qcec(
#     input_circuit: QuantumCircuit,
#     output_circuit: QuantumCircuit,
#     initial_mapping: dict[LogicalQubit, PhysicalQubit],
#     ancillaries: bool,
# ) -> bool:

#     output_mapping = line_gate_mapping(output_circuit)

#     mapped_output = QuantumCircuit(input_circuit.num_qubits)
#     output_circuit_data = output_circuit.data

#     reverse_initial = {p.id: l.id for l, p in initial_mapping.items()}

#     while not all(len(output_mapping[line]) == 0 for line in output_mapping.keys()):
#         for line in output_mapping.keys():
#             gates = output_mapping[line]
#             for gate_num, gate_name in gates:
#                 if gate_name.startswith("swap") or gate_name.startswith("cx"):
#                     break
#                 else:
#                     orig_instr = output_circuit_data[gate_num]
#                     instr = orig_instr.replace(
#                         qubits=[Qubit(register, reverse_initial[line])]
#                     )
#                     mapped_output.append(instr)
#                     output_mapping[line] = output_mapping[line][1:]

#         waiting = []
#         matching_binary_gates = []
#         for line in output_mapping.keys():
#             gates = output_mapping[line]
#             if gates:
#                 binary_num, _ = gates[0]
#                 if binary_num in waiting:
#                     waiting.remove(binary_num)
#                     matching_binary_gates.append(binary_num)
#                 else:
#                     waiting.append(binary_num)

#         for line in output_mapping.keys():
#             gates = output_mapping[line]
#             if gates:
#                 binary_num, binary_name = gates[0]
#                 if binary_num in matching_binary_gates:
#                     if binary_name.startswith("cx"):
#                         other_line = int(binary_name[4:])
#                         is_control = int(binary_name[2]) == 0

#                         orig_instr = output_circuit_data[binary_num]
#                         if is_control:
#                             instr = orig_instr.replace(
#                                 qubits=[
#                                     Qubit(register, reverse_initial[line]),
#                                     Qubit(register, reverse_initial[other_line]),
#                                 ]
#                             )
#                         else:
#                             instr = orig_instr.replace(
#                                 qubits=[
#                                     Qubit(register, reverse_initial[other_line]),
#                                     Qubit(register, reverse_initial[line]),
#                                 ]
#                             )
#                         mapped_output.append(instr)
#                         output_mapping[line] = output_mapping[line][1:]
#                         output_mapping[other_line] = output_mapping[other_line][1:]
#                     else:
#                         # SWAP
#                         other_line = int(binary_name[4:])
#                         output_mapping[line] = output_mapping[line][1:]
#                         output_mapping[other_line] = output_mapping[other_line][1:]
#                         if ancillaries and (
#                             line not in reverse_initial.keys()
#                             or other_line not in reverse_initial.keys()
#                         ):
#                             if line not in reverse_initial.keys():
#                                 reverse_initial[line] = reverse_initial[other_line]
#                                 del reverse_initial[other_line]
#                             else:
#                                 reverse_initial[other_line] = reverse_initial[line]
#                                 del reverse_initial[line]
#                         else:
#                             tmp = reverse_initial[line]
#                             reverse_initial[line] = reverse_initial[other_line]
#                             reverse_initial[other_line] = tmp

#     mapped_output.measure_all()
#     input_circuit.measure_all()

#     result = verify(input_circuit, mapped_output)

#     if result.equivalence == EquivalenceCriterion.equivalent:
#         return True
#     else:
#         return False
