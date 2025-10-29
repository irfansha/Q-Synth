import math
from qiskit import QuantumCircuit, QuantumRegister, qasm2
from qiskit.circuit import Qubit, Instruction, CircuitInstruction
from itertools import takewhile


class LogicalQubit:
    def __init__(self, id: int):
        self.id = id

    def __str__(self):
        return f"q_{self.id}"

    def __eq__(self, other):
        if isinstance(other, LogicalQubit):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)


class PhysicalQubit:
    def __init__(self, id: int):
        self.id = id

    def __str__(self):
        return f"p_{self.id}"

    def __eq__(self, other):
        if isinstance(other, PhysicalQubit):
            return self.id == other.id
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)


class SynthesizerOutput:
    pass


class SynthesizerTimeout(SynthesizerOutput):
    def __str__(self):
        return "Timeout."


class SynthesizerNoSolution(SynthesizerOutput):
    def __str__(self):
        return "No solution found."


class SynthesizerSolution(SynthesizerOutput):
    __match_args__ = ("circuit", "initial_mapping", "time")

    def __init__(
        self,
        circuit: QuantumCircuit,
        mapping: dict[LogicalQubit, PhysicalQubit],
        time_breakdown: tuple[float, float, tuple[float, float] | None],
        depth: int,
        cx_depth: int,
        swaps: int,
    ):
        self.circuit = circuit
        self.initial_mapping = mapping
        self.total_time = time_breakdown[0]
        self.solver_time = time_breakdown[1]
        self.optional_times = time_breakdown[2]
        self.depth = depth
        self.cx_depth = cx_depth
        self.swaps = swaps

    def __str__(self):
        initial_mapping_str = "\n  ".join(
            sorted(
                f"{logical} -> {physical}"
                for logical, physical in self.initial_mapping.items()
            )
        )
        return f"Done!\n{self.circuit}\nDepth: {self.depth}, CX-depth: {self.cx_depth}, SWAPs: {self.swaps}\nInitial mapping: \n  {initial_mapping_str}\n"

    def report_time(self):
        time_str = (
            f"Solver time: {self.solver_time:.3f} seconds.\nTotal time (including preprocessing): {self.total_time:.3f} seconds."
            if self.optional_times == None
            else f"Solver time for optimal depth: {self.optional_times[0]:.3f} seconds.\nSolver time for optimal SWAPs: {self.optional_times[1]:.3f} seconds.\nTotal solver time: {self.solver_time:.3f} seconds.\nTotal time (including preprocessing): {self.total_time:.3f} seconds."
        )
        return time_str


def gate_line_dependency_mapping(
    circuit: QuantumCircuit,
) -> dict[int, tuple[str, list[int]]]:
    """
    Returns a mapping of gate index to the name of the gate and the qubits it acts on.

    Example
    -------
    Given circuit:
         ┌───┐
    q_0: ┤ X ├──■──
         ├───┤┌─┴─┐
    q_1: ┤ X ├┤ X ├
         └───┘├───┤
    q_2: ──■──┤ X ├
         ┌─┴─┐└───┘
    q_3: ┤ X ├─────
         └───┘

    The mapping would be:
    `{0: ('x', [0]), 1: ('x', [1]), 2: ('cx', [2, 3]), 3: ('cx', [0, 1]), 4: ('x', [2])}`
    """
    circuit_data = list(circuit.data)

    mapping = {}
    for i, instr in enumerate(circuit_data):
        name = instr.operation.name
        input_idxs = [qubit._index for qubit in instr.qubits]
        if name is None:
            raise ValueError(f"Gate at index {i} has no name.")

        if len(input_idxs) > 1 and name != "cx" and name != "swap":
            raise ValueError(
                f"Gate at index {i} is not a CX or SWAP but has multiple inputs. QuilLS can not handle multiple input gates other than CX or SWAP."
            )

        if any(idx is None for idx in input_idxs):
            raise ValueError(f"Gate at index {i} has an input with no index.")

        if name == "rx" or name == "rz":
            angle = instr.operation.params[0]
            name = f"{name}_{angle}"
        if name.startswith("u"):
            if name == "u" or name == "u3":
                theta = instr.operation.params[0]
                phi = instr.operation.params[1]
                lam = instr.operation.params[2]
                name = f"{name}_{theta}_{phi}_{lam}"
            elif name == "u2":
                theta = math.pi / 2
                phi = instr.operation.params[0]
                lam = instr.operation.params[1]
                name = f"{name}_{phi}_{lam}"
            elif name == "u1":
                theta = 0.0
                phi = 0.0
                lam = instr.operation.params[0]
                name = f"{name}_{lam}"
        mapping[i] = (name, input_idxs)

    return mapping


def gate_direct_dependency_mapping(circuit: QuantumCircuit) -> dict[int, list[int]]:
    """
    Returns a mapping of gate index to the indices of the gates that it directly depends on.

    The algorithm is O(n^2) and it works like this:
    - It calculates the line dependency mapping.
    - Do a reverse traversal of the line dependency mapping (starting with the largest gate index)
        - Take a given physical qubit line in the line dependency mapping for the current gate
            - Find the largest gate index that depends on the current physical qubit line and note the gate index

    Example
    -------
    Given circuit:
         ┌───┐
    q_0: ┤ X ├──■──
         ├───┤┌─┴─┐
    q_1: ┤ X ├┤ X ├
         └───┘├───┤
    q_2: ──■──┤ X ├
         ┌─┴─┐└───┘
    q_3: ┤ X ├─────
         └───┘

    The mapping would be:
    `{4: [2], 3: [1, 0], 2: [], 1: [], 0: []}`
    """
    line_dependency_mapping = gate_line_dependency_mapping(circuit)

    mapping = {}
    for i in range(len(line_dependency_mapping) - 1, -1, -1):
        gate_lines = line_dependency_mapping[i][1]
        mapping[i] = []
        for j in range(i - 1, -1, -1):
            other_gate_lines = line_dependency_mapping[j][1]
            for qubit in gate_lines:
                if qubit in other_gate_lines:
                    mapping[i].append(j)

            for other_qubit in other_gate_lines:
                if other_qubit in gate_lines:
                    gate_lines.remove(other_qubit)

            if len(gate_lines) == 0:
                break

    return mapping


def gate_dependency_mapping(circuit: QuantumCircuit) -> dict[int, list[int]]:
    """
    Returns a mapping of gate index to the indices of the gates that it depends on.
    """
    direct_dependency_mapping = gate_direct_dependency_mapping(circuit)
    dependency_mapping: dict[int, set[int]] = {}
    for i in range(len(direct_dependency_mapping)):
        if direct_dependency_mapping[i] == []:
            dependency_mapping[i] = set()
            continue

        dependency_mapping[i] = set()
        for dep in direct_dependency_mapping[i]:
            dependency_mapping[i].add(dep)
            dependency_mapping[i] = dependency_mapping[i].union(dependency_mapping[dep])

    return {gate: list(deps) for gate, deps in dependency_mapping.items()}


def gate_direct_successor_mapping(circuit: QuantumCircuit) -> dict[int, list[int]]:
    """
    Returns a mapping of gate index to the indices of the gates that directly depend on it.

    The algorithm is O(n^2) and it works like this:
    - It calculates the line dependency mapping.
    - Do a traversal of the line dependency mapping (starting with the smallest gate index)
        - Take a given physical qubit line in the line dependency mapping for the current gate
            - Find the smallest gate index that depends on the current physical qubit line and note the gate index

    Example
    -------
    Given circuit:
         ┌───┐
    q_0: ┤ X ├──■──
         ├───┤┌─┴─┐
    q_1: ┤ X ├┤ X ├
         └───┘├───┤
    q_2: ──■──┤ X ├
         ┌─┴─┐└───┘
    q_3: ┤ X ├─────
         └───┘

    The mapping would be:
    `{0: [3], 1: [3], 2: [4], 3: [], 4: []}`
    """
    line_dependency_mapping = gate_line_dependency_mapping(circuit)

    mapping = {}
    for i in range(len(line_dependency_mapping)):
        gate_lines = line_dependency_mapping[i][1]
        mapping[i] = []
        for j in range(i + 1, len(line_dependency_mapping)):
            other_gate_lines = line_dependency_mapping[j][1]
            for qubit in gate_lines:
                if qubit in other_gate_lines:
                    mapping[i].append(j)

            for other_qubit in other_gate_lines:
                if other_qubit in gate_lines:
                    gate_lines.remove(other_qubit)

            if len(gate_lines) == 0:
                break

    return mapping


def gate_successor_mapping(circuit: QuantumCircuit) -> dict[int, list[int]]:
    """
    Returns a mapping of gate index to the indices of the gates that depend on it.
    """
    direct_successor_mapping = gate_direct_successor_mapping(circuit)
    successor_mapping: dict[int, set[int]] = {}
    for i in range(len(direct_successor_mapping) - 1, -1, -1):
        if direct_successor_mapping[i] == []:
            successor_mapping[i] = set()
            continue

        successor_mapping[i] = set()
        for dep in direct_successor_mapping[i]:
            successor_mapping[i].add(dep)
            successor_mapping[i] = successor_mapping[i].union(successor_mapping[dep])

    return {gate: list(deps) for gate, deps in successor_mapping.items()}


def remove_all_non_cx_gates(circuit: QuantumCircuit) -> QuantumCircuit:
    """
    Remove all non-CX gates from the circuit.
    """
    num_qubits = circuit.num_qubits
    qubit_name = circuit.qregs[0].name
    new_circuit = QuantumCircuit(QuantumRegister(num_qubits, qubit_name))
    for instr in circuit.data:
        if instr.name == "cx":
            new_circuit.append(instr.operation, instr.qubits)

    return new_circuit


def remove_all_non_swap_gates(circuit: QuantumCircuit) -> QuantumCircuit:
    """
    Remove all non-SWAP gates from the circuit.
    """
    num_qubits = circuit.num_qubits
    qubit_name = circuit.qregs[0].name
    new_circuit = QuantumCircuit(QuantumRegister(num_qubits, qubit_name))
    for instr in circuit.data:
        if instr.name.startswith("swap"):
            new_circuit.append(instr.operation, qargs=instr.qubits)

    return new_circuit


def line_gate_mapping(
    circuit: QuantumCircuit,
) -> dict[int, list[tuple[int, str]]]:
    """
    Returns a mapping of qubits to the ids and names of the gates that are executed on that qubit in order.
    SWAP gates are named 'swapi' where 'i' is the qubit on the other side of the SWAP.
    CX gates are named 'cx0-i' or 'cx1-i' depending on if they are the control or target qubit,
    where 'i' is the qubit on the other side of the CX.

    Example
    -------
    Given circuit:
         ┌───┐
    q_0: ┤ X ├──■──
         ├───┤┌─┴─┐
    q_1: ┤ X ├┤ X ├
         └───┘├───┤
    q_2: ──■──┤ X ├
         ┌─┴─┐└───┘
    q_3: ┤ X ├─────
         └───┘

    The mapping would be:
    `{0: [(0, 'x'),(3, 'cx0-1')], 1: [(1, 'x'),(3, 'cx1-0')], 2: [(2, 'cx0-3'),(4, 'x')], 3: [(2, 'cx1-2')]}`
    """
    gate_line_mapping = gate_line_dependency_mapping(circuit)
    mapping = {}

    for gate, (name, lines) in gate_line_mapping.items():
        for i, line in enumerate(lines):
            if not line in mapping.keys():
                mapping[line] = []
            if name == "swap":
                gate_name = f"{name}{lines[i-1]}"
            elif name == "cx":
                gate_name = f"{name}{i}-{lines[i-1]}"
            else:
                gate_name = name
            mapping[line].append((gate, gate_name))

    return mapping


def reinsert_unary_gates(
    original_circuit: QuantumCircuit,
    cx_circuit: QuantumCircuit,
    initial_mapping: dict[LogicalQubit, PhysicalQubit],
    ancillaries: bool,
):
    """
    Reinserts the unary gates from the original circuit into the CX circuit.
    """

    def get_gates_on_line(
        gates: list[tuple[int, str]], mapping: dict[int, tuple[str, list[int]]]
    ):
        def short_name(name: str):
            if name.startswith("cx"):
                return "cx"
            if name.startswith("swap"):
                return "swap"
            return name

        return [(short_name(g[1]), mapping[g[0]][1]) for g in gates]

    def consume_line_until_binary_gate(gate_list: list[tuple[str, list[int]]]):
        unary_gates = list(takewhile(lambda g: g[0] not in ["cx", "swap"], gate_list))
        rest = gate_list[len(unary_gates) :]
        return unary_gates, rest

    original_gate_line_dependency_mapping = gate_line_dependency_mapping(
        original_circuit
    )
    original_gate_list = {
        line: get_gates_on_line(gates, original_gate_line_dependency_mapping)
        for line, gates in line_gate_mapping(original_circuit).items()
    }
    cx_gate_line_dependency_mapping = gate_line_dependency_mapping(cx_circuit)
    cx_gate_list = {
        line: get_gates_on_line(gates, cx_gate_line_dependency_mapping)
        for line, gates in line_gate_mapping(cx_circuit).items()
    }

    register = QuantumRegister(cx_circuit.num_qubits, "p")
    result_circuit = QuantumCircuit(register)
    mapping = {k.id: v.id for k, v in initial_mapping.items()}
    all_pqubits_in_mapping = len(set(mapping.values())) == len(mapping.values())
    all_lqubits_in_mapping = len(set(mapping.keys())) == len(mapping.keys())
    if not all_pqubits_in_mapping or not all_lqubits_in_mapping:
        raise ValueError(
            f"Initial mapping '{mapping}' does not contain all logical and physical qubits. Perhaps the encoding is wrong?"
        )
    while not all(len(gates) == 0 for gates in original_gate_list.values()):
        # insert unary gates
        for line in range(original_circuit.num_qubits):
            original_line = (
                original_gate_list[line] if line in original_gate_list.keys() else []
            )
            unary_gates, rest = consume_line_until_binary_gate(original_line)
            original_gate_list[line] = rest
            physical_line = mapping[line]
            for unary_gate in unary_gates:
                gate_name, _ = unary_gate
                match gate_name:
                    case "x":
                        result_circuit.x(physical_line)
                    case "h":
                        result_circuit.h(physical_line)
                    case "t":
                        result_circuit.t(physical_line)
                    case "tdg":
                        result_circuit.tdg(physical_line)
                    case "s":
                        result_circuit.s(physical_line)
                    case "sdg":
                        result_circuit.sdg(physical_line)
                    case "y":
                        result_circuit.y(physical_line)
                    case "z":
                        result_circuit.z(physical_line)
                    case "sx":
                        result_circuit.sx(physical_line)
                    case name if name.startswith("rx"):
                        theta = float(name.split("_")[1])
                        result_circuit.rx(theta, physical_line)
                    case name if name.startswith("rz"):
                        phi = float(name.split("_")[1])
                        result_circuit.rz(phi, physical_line)
                    case name if name.startswith("u_"):
                        theta = float(name.split("_")[1])
                        phi = float(name.split("_")[2])
                        lam = float(name.split("_")[3])
                        result_circuit.u(theta, phi, lam, physical_line)
                    case name if name.startswith("u3"):
                        theta = float(name.split("_")[1])
                        phi = float(name.split("_")[2])
                        lam = float(name.split("_")[3])
                        instr = CircuitInstruction(
                            operation=Instruction(
                                name="u3",
                                num_qubits=1,
                                num_clbits=0,
                                params=[theta, phi, lam],
                            ),
                            qubits=(Qubit(register, physical_line),),
                            clbits=(),
                        )
                        result_circuit.append(instr)
                    case name if name.startswith("u2"):
                        phi = float(name.split("_")[1])
                        lam = float(name.split("_")[2])
                        instr = CircuitInstruction(
                            operation=Instruction(
                                name="u2",
                                num_qubits=1,
                                num_clbits=0,
                                params=[phi, lam],
                            ),
                            qubits=(Qubit(register, physical_line),),
                            clbits=(),
                        )
                        result_circuit.append(instr)
                    case name if name.startswith("u1"):
                        lam = float(name.split("_")[1])
                        instr = CircuitInstruction(
                            operation=Instruction(
                                name="u1",
                                num_qubits=1,
                                num_clbits=0,
                                params=[lam],
                            ),
                            qubits=(Qubit(register, physical_line),),
                            clbits=(),
                        )
                        result_circuit.append(instr)
                    case _:
                        raise ValueError(
                            f"Unknown unary gate: '{gate_name}'... Perhaps you should add it to the match statement?"
                        )

        def gate_with_unpacked_qubits(gate):
            name, lines = gate
            return name, lines[0], lines[1]

        def instructions_with_two_occurences(instrs: list[tuple[str, int, int]]):
            return {
                instr
                for instr in instrs
                if sum(1 for instr2 in instrs if instr2 == instr) == 2
            }

        # find binary gates to add
        next_instructions = [
            gate_with_unpacked_qubits(gates[0])
            for gates in cx_gate_list.values()
            if gates
        ]
        binary_gates_to_add = instructions_with_two_occurences(next_instructions)

        # pop relevant elements from cx_gate_list
        for line in cx_gate_list:
            empty = len(cx_gate_list[line]) == 0
            if empty:
                continue
            is_to_be_added = (
                gate_with_unpacked_qubits(cx_gate_list[line][0]) in binary_gates_to_add
            )
            if is_to_be_added:
                cx_gate_list[line].pop(0)

        # pop relevant elements from original_gate_list
        for line in original_gate_list:
            empty = len(original_gate_list[line]) == 0
            if empty:
                continue
            name, first, second = gate_with_unpacked_qubits(original_gate_list[line][0])
            is_to_be_added = (
                name,
                mapping[first],
                mapping[second],
            ) in binary_gates_to_add
            if is_to_be_added:
                original_gate_list[line].pop(0)

        # insert binary gates
        for gate in binary_gates_to_add:
            gate_name, first, second = gate
            if gate_name == "cx":
                result_circuit.cx(first, second)
            elif gate_name == "swap":
                result_circuit.swap(first, second)

                # fix mapping
                reverse_mapping = {v: k for k, v in mapping.items()}
                if ancillaries and (
                    first not in reverse_mapping.keys()
                    or second not in reverse_mapping.keys()
                ):
                    if first not in reverse_mapping.keys():
                        second_logical = reverse_mapping[second]
                        mapping[second_logical] = first
                    else:
                        first_logical = reverse_mapping[first]
                        mapping[first_logical] = second
                else:
                    first_logical = reverse_mapping[first]
                    second_logical = reverse_mapping[second]
                    tmp = mapping[first_logical]
                    mapping[first_logical] = mapping[second_logical]
                    mapping[second_logical] = tmp

    return result_circuit


def with_swaps_as_cnots(circuit: QuantumCircuit, register_name: str):
    """
    Replaces all SWAP gates with CNOT gates.
    """
    new_circuit = QuantumCircuit(QuantumRegister(circuit.num_qubits, register_name))
    for instr in circuit.data:

        if instr.name.startswith("swap"):
            new_circuit.cx(instr.qubits[0]._index, instr.qubits[1]._index)
            new_circuit.cx(instr.qubits[1]._index, instr.qubits[0]._index)
            new_circuit.cx(instr.qubits[0]._index, instr.qubits[1]._index)
        else:
            new_circuit.append(instr.operation, instr.qubits)

    return new_circuit


def count_swaps(circuit: QuantumCircuit):
    """
    Counts SWAP gates in a circuit.
    """
    swaps = 0
    for instr in circuit.data:
        if instr.name.startswith("swap"):
            swaps += 1

    return swaps


def make_final_mapping(
    circuit: QuantumCircuit,
    initial_mapping: dict[LogicalQubit, PhysicalQubit],
    ancillaries: bool,
) -> dict[LogicalQubit, PhysicalQubit]:
    reverse_mapping: dict[PhysicalQubit, LogicalQubit] = {
        p: q for q, p in initial_mapping.items()
    }
    only_swaps_circuit = remove_all_non_swap_gates(circuit)
    for instr in only_swaps_circuit.data:
        physical1 = PhysicalQubit(instr.qubits[0]._index)
        physical2 = PhysicalQubit(instr.qubits[1]._index)
        if ancillaries and (
            physical1 not in reverse_mapping.keys()
            or physical2 not in reverse_mapping.keys()
        ):
            if physical1 not in reverse_mapping.keys():
                reverse_mapping[physical1] = reverse_mapping[physical2]
                del reverse_mapping[physical2]
            else:
                reverse_mapping[physical2] = reverse_mapping[physical1]
                del reverse_mapping[physical1]
        else:
            tmp = reverse_mapping[physical1]
            reverse_mapping[physical1] = reverse_mapping[physical2]
            reverse_mapping[physical2] = tmp

    final_mapping = {q: p for p, q in reverse_mapping.items()}
    return final_mapping


def create_mapping_from_file(file_string: str) -> dict[LogicalQubit, PhysicalQubit]:
    result: dict[LogicalQubit, PhysicalQubit] = {}
    f = open(file_string, "r")
    for line in f.readlines():
        log, phys = line.split(" -> ")
        logical = LogicalQubit(int(log))
        physical = PhysicalQubit(int(phys))
        result[logical] = physical
    return result


def save_circuit(
    circuit: QuantumCircuit,
    file_path: str,
    num_qubits: int | None = None,
):
    if num_qubits == None:
        register = QuantumRegister(circuit.num_qubits, "q")
    else:
        register = QuantumRegister(num_qubits, "q")
    output_circuit = QuantumCircuit(register)
    for instr in circuit.data:
        new_instr = instr.replace(
            qubits=[Qubit(register, q._index) for q in instr.qubits]
        )
        output_circuit.append(new_instr)
    circuit_file = open(file_path, "w")
    qasm2.dump(output_circuit, circuit_file)
    circuit_file.close()


def save_initial_mapping(
    initial_mapping: dict[LogicalQubit, PhysicalQubit],
    file_path: str,
):
    f = open(file_path, "w")
    for logical, physical in initial_mapping.items():
        f.write(f"{logical.id} -> {physical.id}\n")
    f.close()


def get_lq_pairs(circuit: QuantumCircuit) -> list[tuple[int, int]]:
    """
    Returns a list of pairs of logical qubits that are involved in a CX gate.
    """
    lq_pairs = []
    for instr in circuit.data:
        if instr.name == "cx":
            lq_pairs.append((instr.qubits[0]._index, instr.qubits[1]._index))
    return lq_pairs
