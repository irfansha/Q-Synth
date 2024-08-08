# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from src.LayoutSynthesis.variable_dispatcher import VarDispatcher as vd
from pysat.solvers import Solver
from pysat.card import *
from pysat.formula import CNF

# Takes a model, mapping variables and the number of qubits, and extract the qubit mapping:
def extract_mapping(model, mapping_variables,num_pqubits,cur_p):
  for j in range(num_pqubits):
    if (mapping_variables[cur_p][j] in model):
      #print(f'p{cur_p} -> p{j}')
      return j
    else:
      assert(-mapping_variables[cur_p][j] in model)

# We assume that a part of the graph is already mapped, which is determined by the mapped_qubits
# Now we compute the isomorphic qubit set for the subgraph given:
def compute_isomorphic_qubits_to_single_qubit(mapped_pqubits,args,encoding_clauses,num_pqubits, mapping_variables):

    with Solver(use_timer=True, name=args.solver) as s:
      s.append_formula(encoding_clauses.clauses)

      # Add constraints for those qubits are mapped:
      for mapped_pqubit in mapped_pqubits:
        s.add_clause([mapping_variables[mapped_pqubit][mapped_pqubit]])

      computed_pqubits = []
      isomorphic_pqubits = []


      # for each pqubit which is not in the assumption, we find the isomorphic set of qubits: 
      for cur_p in range(num_pqubits):
        if (cur_p in computed_pqubits or cur_p in mapped_pqubits):
          continue
        single_qubit_isomorphic_pqubits = []
        # first adding itself to computed qubits:
        computed_pqubits.append(cur_p)
        # adding itself to the current isomorphic pqubits:
        single_qubit_isomorphic_pqubits.append(cur_p)

        status = True
        while(status):
          # adding assumptions to avoid already computed pqubits:
          assumptions = []
          for computed_qubit in computed_pqubits:
            assumptions.append(-mapping_variables[cur_p][computed_qubit])

          # for each qubit itself is also added as assumption:
          # testing for p0 not p0:
          assumptions.append(-mapping_variables[cur_p][cur_p])

          status = s.solve(assumptions)
          if (status == True):
            model = s.get_model()
            #print("Solved")
            #print(model)
            current_computed_pqubit = extract_mapping(model, mapping_variables, num_pqubits, cur_p)
            computed_pqubits.append(current_computed_pqubit)
            single_qubit_isomorphic_pqubits.append(current_computed_pqubit)

        # after computation adding current isomorphic qubits to the main list:
        isomorphic_pqubits.append(single_qubit_isomorphic_pqubits)
    return isomorphic_pqubits


# takes bi-coupling graph, number of physical qubits as main inputs
# and computes non-isomorphic implications for two pqubits as an ouput:
# performance can be improved further, by avoiding unnecessary work,
# some isomorphic qubit combinations are still allowed, to be pruned later (TODO)
def compute_isomporphic_physical_qubits(args, bi_coupling_map,num_pqubits):
    new_vars = vd()
    encoding_clauses = CNF()

    mapping_variables = []

    # Allocate variables for each qubit to qubit combination:
    for i in range(num_pqubits):
      mapping_variables.append(new_vars.get_vars(num_pqubits))

    # ExactlyOne constraints for horizontal slices:
    for i in range(num_pqubits):
      cur_slice = mapping_variables[i]
      cnf = CardEnc.equals(lits=cur_slice,top_id=new_vars.next_var-1,encoding=args.cardinality)
      if (cnf.nv+1 > new_vars.next_var):
        new_vars.set_next_var(cnf.nv+1)
      encoding_clauses.extend(cnf.clauses)

    # ExactlyOne constraints for vertical slices:
    for j in range(num_pqubits):
      cur_slice = []
      for i in range(num_pqubits):
        cur_slice.append(mapping_variables[i][j])
      cnf = CardEnc.equals(lits=cur_slice,top_id=new_vars.next_var-1,encoding=args.cardinality)
      if (cnf.nv+1 > new_vars.next_var):
        new_vars.set_next_var(cnf.nv+1)
      encoding_clauses.extend(cnf.clauses)

    # For each pair of qubits, we generate atleast one edge constraints on the mapped graph:
    unique_pairs = []
    # indicates if mapped qubits are also connected:
    indicator_variables = []
    for [x0,x1] in bi_coupling_map:
      if ([x1,x0] not in unique_pairs):
        unique_pairs.append([x0,x1])
        cur_vars = new_vars.get_vars(len(bi_coupling_map))
        indicator_variables.append(cur_vars)

        # we generate constraints for all the bi_coupling edges:
        for bi_coupling_index in range(len(bi_coupling_map)):
          pair_var = cur_vars[bi_coupling_index]
          [y0, y1] = bi_coupling_map[bi_coupling_index]
          mapping_var1 = mapping_variables[x0][y0]
          mapping_var2 = mapping_variables[x1][y1]
          encoding_clauses.extend([[-pair_var,mapping_var1],[-pair_var,mapping_var2],[-mapping_var1,-mapping_var2,pair_var]])
        
        # adding a disjunction for current indicator variables:
        encoding_clauses.extend([cur_vars])

    # we start with an empty, which is for the size 0:
    current_nonisomorphic_sets = [[]]

    isomorphic_implications = []

    # We generate non-isomorphic unique subgraphs of size k:
    for k in range(0,args.symmetry_breaking):

      #print(k,current_nonisomorphic_sets)

      nonisomorphic_pqubits_set = []
      for nonisomorphic_set in current_nonisomorphic_sets:
        #print(nonisomorphic_set)
        isomorphic_pqubits = compute_isomorphic_qubits_to_single_qubit(nonisomorphic_set,args,encoding_clauses,num_pqubits, mapping_variables)
        # for each nonisomorphic set we generate an implication:
        temp_clause = []
        for qubit in nonisomorphic_set:
          temp_clause.append(qubit)
        # we only compute first two qubit symmetries atmost:
        assert(len(temp_clause) <=1)
        cur_isomorphic_implication = []
        # extract non-isomorphic qubits one from each set:
        for pqubit_set in isomorphic_pqubits:
          pqubit_set = sorted(pqubit_set)
          cur_isomorphic_implication.append(pqubit_set[0])

          temp_nonisomorphic_qpubit_set = list(nonisomorphic_set)
          temp_nonisomorphic_qpubit_set.append(pqubit_set[0])
          nonisomorphic_pqubits_set.append(temp_nonisomorphic_qpubit_set)

        isomorphic_implications.append((temp_clause,cur_isomorphic_implication))
        if (args.verbose > 2):
          print("Isomorphic sets of current physical qubits: ", isomorphic_pqubits)

      current_nonisomorphic_sets = nonisomorphic_pqubits_set

    if (args.verbose > 1):
      print("Isomorphic implications: ",isomorphic_implications)
    return isomorphic_implications