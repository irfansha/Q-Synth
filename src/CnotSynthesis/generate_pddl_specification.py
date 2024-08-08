# Irfansha Shaik, Aarhus, 15 January 2024.

def goal_x_and_z(matrix,matrix_predicate, pddl_lines, index_increment, num_qubits):
    for row_id in range(num_qubits):
      row_line = ""
      for column_id in range(num_qubits):
          cell = matrix[row_id][column_id]
          if (cell == True):
              row_line += "     (" + matrix_predicate + f" q{index_increment+row_id} q{column_id}) "
          else:
              assert(cell == False)
              row_line += "(not (" + matrix_predicate + f" q{index_increment+row_id} q{column_id}))"
      pddl_lines.append(f" {row_line}\n")
    return pddl_lines

def generate_problem_specification(clifford_matrix, options, num_qubits):
    pddl_lines = []
    pddl_lines.append("(define (problem instance)\n")
    pddl_lines.append("  (:domain Cnot-Synthesis)\n")
    pddl_lines.append("  (:objects")
    # generating objects for rows/columns:
    qubits = ""
    for i in range(num_qubits):
      qubits += f"q{i} "
    pddl_lines.append(f"  {qubits}- qubit)\n")

    pddl_lines.append("(:init\n")
    # identity matrix:
    cells = "\n;; Indentity matrix\n"
    for i in range(num_qubits):
      cells += f"(X q{i} q{i})\n"
    pddl_lines.append(cells)

    # If coupling graph is given then we add it to the initial state:
    if (options.coupling_graph):
      for edge in options.coupling_graph:
        pddl_lines.append(f"  (connected q{edge[0]} q{edge[1]})\n")
    pddl_lines.append(")\n")


    pddl_lines.append("(:goal\n")

    # Destabilizer goal matrices:
    pddl_lines.append("  (and\n   ;; target destabilizer X matrix\n")
    pddl_lines = goal_x_and_z(clifford_matrix.destab_x,"X", pddl_lines,0, num_qubits)      
    pddl_lines.append("  )\n)\n)")
    return pddl_lines
