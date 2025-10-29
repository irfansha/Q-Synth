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
    # if initial permutation is specified, not need to give identity matrix:
    if options.encoding != "gate_optimal-permute-init":
        # identity matrix:
        cells = "\n;; Destabilizer X Indentity matrix\n"
        for i in range(num_qubits):
            if options.encoding == "gate_optimal-permute":
                cells += f"(IX r{i} q{i})\n"
            else:
                cells += f"(X r{i} q{i})\n"

        cells += "\n;; Stabilizer Z Identity matrix\n"

        for i in range(num_qubits, (2 * num_qubits)):
            if options.encoding == "gate_optimal-permute":
                cells += f"(iZ r{i} q{i-num_qubits})\n"
            else:
                cells += f"(Z r{i} q{i-num_qubits})\n"

        pddl_lines.append(cells)
    else:
        # we need to specify the row pairs:
        for i in range(num_qubits):
            pddl_lines.append(f"(rpair r{i} r{i+num_qubits})\n")

    if "cnot_optimal" in options.encoding:
        # ordering qubits:
        for i in range(num_qubits):
            pddl_lines.append(";; ordering qubits\n")
            for j in range(i + 1, num_qubits):
                pddl_lines.append(f"(ordered q{i} q{j})\n")

    # If coupling graph is given then we add it to the initial state:
    if options.coupling_graph:
        for edge in options.coupling_graph:
            pddl_lines.append(f"  (connected q{edge[0]} q{edge[1]})\n")
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
    # if cnot_optimal, we need to disable all the qubits by applying the last layer:
    if "cnot_optimal" in options.encoding:
        pddl_lines.append(";; qubits to be disabled\n")
        for i in range(num_qubits):
            pddl_lines.append(f"(disabled q{i})\n")
    # for cnot_optimal_simple we do not need our qubits to be busy:
    if "cnot_optimal" == options.encoding:
        pddl_lines.append(";; qubits are not busy\n")
        for i in range(num_qubits):
            pddl_lines.append(f"(not (busy q{i}))\n")
        pddl_lines.append(";; no cnots to be appiled\n")
        for i in range(num_qubits):
            pddl_lines.append(f"(not (apply_cnot_gate q{i}))\n")
        pddl_lines.append(";; no single gates to be appiled\n")
        for i in range(num_qubits):
            pddl_lines.append(f"(not (apply_single_gate q{i}))\n")

    # if permutation applied, we specify that all maps are applied:
    if options.encoding == "gate_optimal-permute":
        pddl_lines.append("   ;; all mappings must be complete\n")
        for i in range(num_qubits):
            pddl_lines.append(f"(imapped q{i}) (mapped q{i})\n")
    elif options.encoding == "gate_optimal-permute-init":
        pddl_lines.append("   ;; all mappings must be complete\n")
        for i in range(num_qubits):
            pddl_lines.append(f"(qmapped q{i})\n")
        for i in range(2 * num_qubits):
            pddl_lines.append(f"(rmapped r{i})\n")
    pddl_lines.append("  )\n)\n")
    pddl_lines.append(")")
    return pddl_lines
