# Irfansha Shaik, Aarhus, 15 January 2024.


def goal_x_and_z(matrix, matrix_predicate, pddl_lines, index_increment, num_qubits):
    for row_id in range(num_qubits):
        row_line = ""
        for column_id in range(num_qubits):
            cell = matrix[row_id][column_id]
            if cell == True:
                row_line += (
                    "     ("
                    + matrix_predicate
                    + f" r{index_increment+row_id} q{column_id}) "
                )
            else:
                assert cell == False
                row_line += (
                    "(not ("
                    + matrix_predicate
                    + f" r{index_increment+row_id} q{column_id}))"
                )
        pddl_lines.append(f" {row_line}\n")
    return pddl_lines

def generate_problem_specification(clifford_matrix, options, num_qubits):
    pddl_lines = []
    pddl_lines.append("(define (problem instance)\n")
    pddl_lines.append("  (:domain Clifford-Synthesis)\n")
    pddl_lines.append("  (:objects")
    if options.encoding == "rigidcnot":
        pddl_lines.append("    ;; Rigid CNOT encoding objects\n")
        # generating gates as objects:
        gates = "base_gate "
        for gate in options.gate_qubit_map.keys():
            gates += f"{gate} "
        pddl_lines.append(f"  {gates}- gate\n")
    # generating objects for rows/columns:
    qubits = ""
    for i in range(num_qubits):
        qubits += f"q{i} "
    pddl_lines.append(f"  {qubits}- qubit\n")

    rows = "\t     "
    for i in range((2 * num_qubits)):
        rows += f"r{i} "
    pddl_lines.append(f"  {rows}- row)\n")

    pddl_lines.append("(:init\n")
    # identity matrix:
    cells = "\n;; Destabilizer X Indentity matrix\n"
    for i in range(num_qubits):
        cells += f"(X r{i} q{i})\n"

    cells += "\n;; Stabilizer Z Identity matrix\n"

    for i in range(num_qubits, (2 * num_qubits)):
        cells += f"(Z r{i} q{i-num_qubits})\n"

    pddl_lines.append(cells)
    # If coupling graph is given then we add it to the initial state:
    if options.encoding != "rigidcnot": # only for non-rigid cnot encoding
        pddl_lines.append("\n;; Coupling graph connections\n")
        if options.coupling_graph:
            for edge in options.coupling_graph:
                if options.encoding == "normalform" and edge[0] >= edge[1]:
                    continue  # only add one direction for normalform
                pddl_lines.append(f"(connected q{edge[0]} q{edge[1]})\n")
        else:
            # fully connected graph:
            for i in range(num_qubits):
                for j in range(num_qubits):
                    if i == j or (options.encoding == "normalform" and i > j):
                        continue # skip cnots on same qubit and only one direction for normalform
                    pddl_lines.append(f"(connected q{i} q{j})\n")
    # We do not need cost for normalform encoding, so we add cost only for other encodings:
    if options.encoding != "normalform":
        pddl_lines.append("\n;; Initializing total cost \n")
        pddl_lines.append("(= (total-cost) 0)\n")
        if options.encoding != "rigidcnot":
            pddl_lines.append(f"(= (cnot-cost) {options.cnot_cost})\n")
    
    # We specify the static predicates for rigid cnot encoding:
    if options.encoding == "rigidcnot":
        pddl_lines.append("\n;; Rigid CNOT encoding static predicates\n")
        for gate, qubits in options.gate_qubit_map.items():
            if len(qubits) == 2:
                pddl_lines.append(
                    f"(cnot_gate {gate} q{qubits[0]} q{qubits[1]})\n"
                )
            else:
                pddl_lines.append(f"(oneq_gate {gate} q{qubits[0]})\n")
        # dependencies:
        pddl_lines.append("\n;; Rigid CNOT encoding dependencies\n")
        for gate, depends_on in options.dependencies.items():
            pddl_lines.append(f"(depends {gate} {depends_on})\n")
        # base gate is done by default : 
        pddl_lines.append(f"(done base_gate)\n")
        if options.flip_cnot:
            pddl_lines.append(f"(flip_cnot)\n")
    pddl_lines.append(")\n")

    pddl_lines.append("(:goal\n")

    # Destabilizer goal matrices:
    pddl_lines.append("  (and\n   ;; target destabilizer X matrix\n")
    pddl_lines = goal_x_and_z(clifford_matrix.destab_x, "X", pddl_lines, 0, num_qubits)
    pddl_lines.append("   ;; target destabilizer Z matrix\n")
    pddl_lines = goal_x_and_z(clifford_matrix.destab_z, "Z", pddl_lines, 0, num_qubits)

    # Stabilizer goal matrices, the row index starts from num_qubits:
    pddl_lines.append("   ;; target stabilizer X matrix\n")
    pddl_lines = goal_x_and_z(
        clifford_matrix.stab_x, "X", pddl_lines, num_qubits, num_qubits
    )
    pddl_lines.append("   ;; target stabilizer Z matrix\n")
    pddl_lines = goal_x_and_z(
        clifford_matrix.stab_z, "Z", pddl_lines, num_qubits, num_qubits
    )
    if options.encoding == "normalform":
        # all qubits should be disabled at the end:
        pddl_lines.append("  ;; disabling all qubits:\n")
        for i in range(num_qubits):
            pddl_lines.append(f"  (disabled q{i})\n")
    if options.encoding == "rigidcnot":
        # all gates should be done at the end:
        pddl_lines.append("  ;; all gates done:\n")
        for gate in options.gate_qubit_map.keys():
            pddl_lines.append(f"  (done {gate})\n")
    pddl_lines.append("  )\n)\n")
    if options.encoding != "normalform":
        pddl_lines.append("(:metric minimize (total-cost))\n")
    pddl_lines.append(")")
    return pddl_lines
