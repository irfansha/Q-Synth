# Irfansha Shaik, 31.01.2024, Aarhus

from src.CnotSynthesis.circuit_utils.variables_dispatcher import VarDispatcher as vd
from src.CnotSynthesis.circuit_utils.constraints import Constraints
from pysat.solvers import Solver
from pysat.card import *
from pysat.formula import CNF

def extract_swaps(model, num_qubits, swap1_vars, swap2_vars, plan_length, plan):
  
  for i in range(plan_length):
    p1, p2 = None, None
    for qid in range(num_qubits):
      if (swap1_vars[i][qid] in model):
        p1 = qid
      if (swap2_vars[i][qid] in model):
        p2 = qid
    plan.append(("swap", 'q'+str(p1), 'q'+str(p2)))
  return plan
  

def Exactly_One_constraints(variables, constraints, num_qubits, new_vars):
    # ExactlyOne constraints for row matrix elements:
    for i in range(num_qubits):
      cur_slice = variables[i]
      constraints.ExactlyOne_constraints(cur_slice)

    # ExactlyOne constraints for column matrix elements:
    for j in range(num_qubits):
      cur_slice = []
      for i in range(num_qubits):
        cur_slice.append(variables[i][j])
      constraints.ExactlyOne_constraints(cur_slice)
    return constraints

def generate_initial_gate(variables, num_qubits, constraints):
  # we start with an initial diagonal mapping:
  for qid in range(num_qubits):
    constraints.unit_clause(variables[qid][qid])
  return constraints

def generate_goal_gate(variables, num_qubits, constraints, qubit_map):
  # we need to reach the matrix with qubit mapping:
  for qid,row_id in qubit_map.items():
    constraints.unit_clause(variables[row_id][qid])
  return constraints  

def generate_transition(vars_t1, vars_t2, swap1_vars, swap2_vars, constraints, num_qubits):
  # we swap on different qubits:
  for qid in range(num_qubits):
    constraints.or_clause([-swap1_vars[qid], -swap2_vars[qid]])

  # we apply exactly one swap1 and swap2 vars:
  constraints.ExactlyOne_constraints(swap1_vars)
  constraints.ExactlyOne_constraints(swap2_vars)

  for swap1 in range(num_qubits):
    for swap2 in range(num_qubits):
      if (swap1 == swap2):
        continue
      # Forall rows, we add the cell update clauses:
      for row_id in range(num_qubits):
        # if the swap1, swap2 are true, and control cell is also true, then the target cell is set to true:
        constraints.if_and_then_equal_clauses([swap1_vars[swap1], swap2_vars[swap2]], vars_t1[row_id][swap1], vars_t2[row_id][swap2])

  # if the control and target qubit is not used then the corresponding cell is propagated to the next time step:
  for qid in range(num_qubits):
    # Forall rows, we add the cell update clauses:
    for row_id in range(num_qubits):
      constraints.if_and_then_equal_clauses([-swap1_vars[qid], -swap2_vars[qid]], vars_t1[row_id][qid],vars_t2[row_id][qid])
  return constraints
  

# takes qubit mapping and encodes a sat encoding with parallel swaps
# appends the swaps that arrage the initial matrix to the qubit mapping matrix:
def extract_swaps_for_initial_mapping(qubit_map, plan, num_qubits):
    # we assume that 
    status = False
    plan_length = -1

    while(status != True):
      # increment plan_length:
      plan_length += 1
      #print(plan_length)
      new_vars = vd()
      encoding_clauses = CNF()
      constraints = Constraints(encoding_clauses)

      matrix_variables = []
      for i in range(plan_length+1):
        cur_matrix_variables = []
        # Allocate variables for each qubit to qubit combination:
        for i in range(num_qubits):
          cur_matrix_variables.append(new_vars.get_vars(num_qubits))
        matrix_variables.append(cur_matrix_variables)
      #print(matrix_variables)

      swap1_variables = []
      swap2_variables = []
      for i in range(plan_length):
        swap1_variables.append(new_vars.get_vars(num_qubits))
        swap2_variables.append(new_vars.get_vars(num_qubits))

      #print(swap1_variables)
      #print(swap2_variables)

      constraints = generate_initial_gate(matrix_variables[0], num_qubits, constraints)

      for i in range(plan_length):
        # initialize action vara
        constraints = generate_transition(matrix_variables[i],matrix_variables[i+1], swap1_variables[i], swap2_variables[i], constraints, num_qubits)
        constraints = Exactly_One_constraints(matrix_variables[i], constraints, num_qubits, new_vars)

      constraints = generate_goal_gate(matrix_variables[-1], num_qubits, constraints, qubit_map)
      # we need exactly one constraints also in the goal matrix:
      constraints = Exactly_One_constraints(matrix_variables[-1], constraints, num_qubits, new_vars)

      with Solver(use_timer=True, name="cd15") as s:
        s.append_formula(constraints.clause_list.clauses)
        status = s.solve()

        if (status):
          #print("Swaps generated")
          model = s.get_model()
          plan = extract_swaps(model, num_qubits, swap1_variables, swap2_variables, plan_length, plan)

    return plan