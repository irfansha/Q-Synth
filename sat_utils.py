# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from circuit_utils import strict_dependencies, relaxed_dependencies, cancel_cnots, all_cx_gates, gate_get_qubit
from architecture import platform

from pysat.card import *  
from symmetry_breaking import compute_isomporphic_physical_qubits
import time

########################################################################################
# Helper functions:
########################################################################################

def AtmostOne_constraints(self, vars):
    cnf = CardEnc.atmost(lits=vars,top_id=self.new_vars.next_var-1,encoding=self.args.cardinality)
    if (cnf.nv+1 > self.new_vars.next_var):
      self.new_vars.set_next_var(cnf.nv+1)
    if (self.args.verbose > 2):
      print("Atmost One for ",vars)
    self.clause_list.extend(cnf.clauses)
  
def AtleastOne_constraints(self, vars):
    cnf = CardEnc.atleast(lits=vars,top_id=self.new_vars.next_var-1,encoding=self.args.cardinality)
    if (cnf.nv+1 > self.new_vars.next_var):
      self.new_vars.set_next_var(cnf.nv+1)
    if (self.args.verbose > 2):
      print("Atleast One for ",vars)
    self.clause_list.extend(cnf.clauses)

def ExactlyOne_constraints(self,vars):
    cnf = CardEnc.equals(lits=vars,top_id=self.new_vars.next_var-1,encoding=self.args.cardinality)
    if (cnf.nv+1 > self.new_vars.next_var):
      self.new_vars.set_next_var(cnf.nv+1)
    if (self.args.verbose > 2):
      print("Exactly One for ",vars)
    self.clause_list.extend(cnf.clauses)

def ExactlyTwo_constraints(self,vars):
    cnf = CardEnc.equals(lits=vars,top_id=self.new_vars.next_var-1,encoding=self.args.cardinality,bound=2)
    if (cnf.nv+1 > self.new_vars.next_var):
      self.new_vars.set_next_var(cnf.nv+1)
    if (self.args.verbose > 2):
      print("Exactly Two for ",vars)
    self.clause_list.extend(cnf.clauses)

def AtmostTwo_constraints(self,vars):
    cnf = CardEnc.atmost(lits=vars,top_id=self.new_vars.next_var-1,encoding=self.args.cardinality,bound=2)
    if (cnf.nv+1 > self.new_vars.next_var):
      self.new_vars.set_next_var(cnf.nv+1)
    if (self.args.verbose > 2):
      print("Atmost Two for ",vars)
    self.clause_list.extend(cnf.clauses)

def single_direction(in_pair,dict):
    # we extract the pair that exists:
    (p1,p2) = in_pair
    if ((p1,p2) in dict):
      out_pair = (p1,p2)
    else:
      out_pair = (p2,p1)
    return out_pair

def unit_clause(self,var):
   self.clause_list.append([var])

# single clause:
def or_clause(self,clause):
   self.clause_list.append(clause)

# single implication with the then list:
def if_then_clause(self,if_var,then_list):
    implication_clause = [-if_var]
    implication_clause.extend(then_list)
    self.clause_list.append(implication_clause)

# assumes if_vars are from conjunction clause:
def if_and_then_clause(self,if_vars,then_list):
    if_clause = []
    for var in if_vars:
      if_clause.append(-var)
    if_clause.extend(then_list)
    self.clause_list.append(if_clause)

# assumes if_vars are from conjunction clauses:
def if_and_then_equal_clauses(self,if_vars,x1,x2):
   if_and_then_clause(self,if_vars,[-x1, x2])
   if_and_then_clause(self,if_vars,[ x1, -x2])

# single implication with the then list and
# for each item in list, if apply reverse implication
def iff_clauses(self,if_var,then_list):
    if_then_clause(self,if_var,then_list)
    for var in then_list:
       self.clause_list.append([-var, if_var])

# one clause for each variable in the then_list:
def if_then_each_clause(self,if_var,then_list):
    for var in then_list:
      self.clause_list.append([-if_var,var])

def iff_then_each_clause(self,if_var,then_list):
    if_then_each_clause(self,if_var,then_list)
    temp_clause = [if_var]
    for var in then_list:
       temp_clause.append(-var)
    self.clause_list.append(temp_clause)

# one clause for each negated variable in the then_list:
def if_then_each_not_clause(self,if_var,then_list):
    for var in then_list:
      self.clause_list.append([-if_var,-var])

########################################################################################
# Parser and dependency functions:
########################################################################################

def compute_predecessors(self):
    self.cx_dict = {}
    self.lq_pair_list = []
    self.cx_predecessors = {}

    for gate_index in range(len(self.logical_circuit)):
      gate = self.logical_circuit[gate_index]
      if (len(gate.qubits) == 2):
        # for now asserting every 2 qubit operation is "cx":
        assert(gate.operation.name == "cx")
        ctrl = gate.qubits[0].index
        data = gate.qubits[1].index
        # getting qubit pairs:
        # assuming bidirectional for coupling graph:
        if ((ctrl, data) not in self.lq_pair_list and (data, ctrl) not in self.lq_pair_list):
          self.lq_pair_list.append((ctrl, data))
        self.cx_dict[gate_index] = (ctrl, data)
        # get dependencies from dictionary:
        (ctrl_dep, data_dep) = self.cnot_depends[gate_index]
        assert(gate_index not in self.cx_predecessors)
        # adding predecessors for control qubit:
        for single_ctrl_dep in ctrl_dep:
          self.cx_predecessors[gate_index] = [single_ctrl_dep]
        # adding predecessors for data qubit:
        for single_data_dep in data_dep:
          if (gate_index not in self.cx_predecessors):
            self.cx_predecessors[gate_index] = [single_data_dep]
          elif (single_data_dep not in self.cx_predecessors[gate_index]):
            self.cx_predecessors[gate_index].append(single_data_dep)        

        #add it self to predecessors:
        if gate_index not in self.cx_predecessors:
          self.cx_predecessors[gate_index] = [gate_index]
        else:
          self.cx_predecessors[gate_index].append(gate_index)

def compute_predecessors_successors(self):
    self.cx_dict = {}
    self.lq_pair_list = []
    self.cx_predecessors = {}
    self.cx_successors = {}

    for gate_index in range(len(self.logical_circuit)):
      gate = self.logical_circuit[gate_index]
      if (len(gate.qubits) == 2):
        # for now asserting every 2 qubit operation is "cx":
        assert(gate.operation.name == "cx")
        ctrl = gate.qubits[0].index
        data = gate.qubits[1].index
        # getting qubit pairs:
        # assuming bidirectional for coupling graph:
        if ((ctrl, data) not in self.lq_pair_list and (data, ctrl) not in self.lq_pair_list):
          self.lq_pair_list.append((ctrl, data))
        self.cx_dict[gate_index] = (ctrl, data)
        # get dependencies from dictionary:
        (ctrl_dep, data_dep) = self.cnot_depends[gate_index]
        assert(gate_index not in self.cx_predecessors)
        # adding successors and predecessors for control qubit:
        for single_ctrl_dep in ctrl_dep:
          self.cx_predecessors[gate_index] = [single_ctrl_dep]
          if single_ctrl_dep not in self.cx_successors:
            self.cx_successors[single_ctrl_dep] = [gate_index]
          elif(gate_index not in self.cx_successors[single_ctrl_dep]):
            self.cx_successors[single_ctrl_dep].append(gate_index)
        # adding successors and predecessors for data qubit:
        for single_data_dep in data_dep:
          if (gate_index not in self.cx_predecessors):
            self.cx_predecessors[gate_index] = [single_data_dep]
          elif (single_data_dep not in self.cx_predecessors[gate_index]):
            self.cx_predecessors[gate_index].append(single_data_dep)

          if single_data_dep not in self.cx_successors:
            self.cx_successors[single_data_dep] = [gate_index]
          elif(gate_index not in self.cx_successors[single_data_dep]):
            self.cx_successors[single_data_dep].append(gate_index)

# if two consequent cnots act on same qubits then no need for a swap between them
# thus we group them to be in the same block:
def group_cnots(self):
   self.group_cnot_dict = {}
   for cur_cnot, depends in self.cnot_depends.items():
      if (len(depends[0]) !=0 and len(depends[1]) != 0):
         if (depends[0][0] == depends[1][0]):
           self.group_cnot_dict[cur_cnot] = depends[0][0]

# we iterate through cnot dependencies and gather connected lq pairs
# we use them for restricting physical qubit distances further:
def generate_distance_two_lq_pairs(self):
   self.distance_two_lq_pairs = {}
   self.distance_two_lq_pair_list = []
   for cur_cnot, depends in self.cnot_depends.items():
      cur_set = set(self.cx_dict[cur_cnot])
      if (len(depends[0]) != 0):
        ctrl_cnot = depends[0][0]
        ctrl_set = set(self.cx_dict[ctrl_cnot])
        if (cur_set != ctrl_set):
          lq_pair = tuple(sorted(cur_set.symmetric_difference(ctrl_set)))
          if (lq_pair not in self.distance_two_lq_pairs):
            self.distance_two_lq_pairs[lq_pair] = [(cur_set,ctrl_set)]
            self.distance_two_lq_pair_list.append(lq_pair)
          else:
            if ((cur_set,ctrl_set) not in self.distance_two_lq_pairs[lq_pair] and \
                (ctrl_set,cur_set) not in self.distance_two_lq_pairs[lq_pair]):
              self.distance_two_lq_pairs[lq_pair].append((cur_set,ctrl_set))
      if (len(depends[1]) != 0):
        data_cnot = depends[1][0]
        data_set = set(self.cx_dict[data_cnot])
        if (cur_set != data_set):
          lq_pair = tuple(sorted(cur_set.symmetric_difference(data_set)))
          if (lq_pair not in self.distance_two_lq_pairs):
            self.distance_two_lq_pairs[lq_pair] = [(cur_set,data_set)]
            self.distance_two_lq_pair_list.append(lq_pair)
          else:
            if ((cur_set,data_set) not in self.distance_two_lq_pairs[lq_pair] and \
                (data_set,cur_set) not in self.distance_two_lq_pairs[lq_pair]):
              self.distance_two_lq_pairs[lq_pair].append((cur_set,data_set))
   if (self.args.verbose > -1) :
     print("distance two lq pairs: ")
     print(self.distance_two_lq_pair_list)
     for k,v in self.distance_two_lq_pairs.items():
       print(k,v)

# Parse and compute cnot gate list with dependencies satisfied:
def parse_and_compute(self):

    # loading quantum circuit with qiskit:
    try:
      self.input_circuit = QuantumCircuit.from_qasm_file(self.args.circuit_in)
    except FileNotFoundError:
      print(f"Error: circuit_in file '{self.args.circuit_in}' not found")
      exit(-1)

    self.logical_circuit = self.input_circuit.copy()
    self.num_lqubits = len(self.input_circuit.qubits)
    if (self.args.verbose > 0):
      print(self.input_circuit)

    # cancel CNOTS
    if self.args.cnot_cancel == 1:
        deps = relaxed_dependencies(self.logical_circuit, verbose=self.args.verbose)
        self.logical_circuit = cancel_cnots(self.logical_circuit, deps, verbose=self.args.verbose)
    
    # extracting CNOT gates and computing dependencies
    if (self.args.relaxed == 0):
      self.cnot_depends = strict_dependencies(self.logical_circuit, verbose=self.args.verbose)
    else:
      self.cnot_depends = relaxed_dependencies(self.logical_circuit, verbose=self.args.verbose)

    # group cnots when enabled:
    if (self.args.group_cnots == 1):
      # for now only with strict dependencies:
      if(self.args.relaxed == 1):
        print("Error: grouping cnots is only handled with strict dependencies")
        exit(-1)
      group_cnots(self)
      if (self.args.verbose > 2):
        print("grouped cnots: ",self.group_cnot_dict)

    self.list_cx_gates = all_cx_gates(self.logical_circuit)
    if (self.args.twoway_sat == 0):
      compute_predecessors(self)
    else:
      compute_predecessors_successors(self)

    # for easy access of cnot gates positions, we generate a dict:
    self.cnot_dict = {}
    for i in range(len(self.list_cx_gates)):
      cx_gate = self.list_cx_gates[i]
      self.cnot_dict[cx_gate] = i

    if (self.args.verbose > 2):
      print("cnot gates: ",self.list_cx_gates)
      print("cnot position dict: ", self.cnot_dict)
      print("cnot to logical pair dict: ", self.cx_dict)
      print("cnot_depends dict:")
      for key,value in self.cnot_depends.items():
        print(key,value)
      print("cnot predecessors:")
      print(self.cx_predecessors)
      print("logical qubit pairs:")
      print(self.lq_pair_list)


def set_architecture(self):
    (self.coupling_map, self.bi_coupling_map, self.bridge_bicoupling_map, self.bridge_middle_pqubit_dict, self.reverse_swap_distance_dict, self.num_pqubits) \
      = platform(self.args.platform, self.args.bidirectional, self.args.verbose)

    self.scoupling = []
    # for swapping, we only need one of the directions in coupling:
    for [x1,x2] in self.coupling_map:
      if (([x1,x2] not in self.scoupling) and ([x2,x1] not in self.scoupling)):
        self.scoupling.append([x1,x2])

    # sorting coupling maps for consistency:
    for coupling in self.bi_coupling_map:
      coupling = sorted(coupling)
    self.bi_coupling_map = sorted(self.bi_coupling_map)
    for coupling in self.scoupling:
      coupling = sorted(coupling)
    self.scoupling = sorted(self.scoupling)

    # finding longest swaps neeeded in the coupling graph:
    self.max_swap_distance = max(k for k,v in self.reverse_swap_distance_dict.items())

    if (self.args.verbose > 1):
      print("single directional coupling map: ", self.scoupling)
      print("max swaps to connect any two physical qubits: ", self.max_swap_distance)


########################################################################################
# Core constraint functions:
########################################################################################

def extract_physical_qubit_slices(self,mapping_vars):
    horizontal_slice = []
    for i in range(self.num_pqubits):
      cur_list = []
      for j in range(self.num_lqubits):
        cur_list.append(mapping_vars[j][i])
      horizontal_slice.append(cur_list)
    return horizontal_slice



def initialize_ancillary_clauses(self, cur_mpvars):
    # for anciliary and non-anciliary swaps, we need to know if the physical qubits are mapped
    # we use mapped pvars to specify that:
    self.cur_sb.mapped_pvars = self.new_vars.get_vars(self.num_pqubits)

    # we need to update the status of mapped pvars based on the mapped physical qubits:
    # if one of the physical qubit is mapped then the mapped_pvar is true:
    for vars_id in range(len(cur_mpvars)):
      vars = cur_mpvars[vars_id]
      mapped_pvar = self.cur_sb.mapped_pvars[vars_id]
      if (self.args.constraints == 0):
        if_then_clause(self,mapped_pvar,vars)
      else:
        iff_clauses(self,mapped_pvar,vars)

def ancillary_constraints(self, tstep):
    # now we need to handle if the ancilliary swap can be used or not:
    for swap_ind in range(len(self.cur_sb.swaps)):
      cur_swap_var = self.cur_sb.swaps[swap_ind]
      # depending on the swap var index, we first get the swapping physical qubits var indexes:
      p1_index,p2_index = self.scoupling[swap_ind]
      mapped_p1var = self.blocks[tstep-1].mapped_pvars[p1_index]
      mapped_p2var = self.blocks[tstep-1].mapped_pvars[p2_index]
      if (self.args.ancillary == 0):
        # swap_pair(p1,p2) -> (mapped_pvar(p1) & mapped_pvar(p2))
        if_then_each_clause(self,cur_swap_var,[mapped_p1var,mapped_p2var])
      # if ancillary can be used, then atleast one of the qubits must be mapped:
      elif (self.args.ancillary == 1):
        # swap_pair(p1,p2) -> (mapped_pvar(p1) V mapped_pvar(p2))
        if_then_clause(self,cur_swap_var,[mapped_p1var,mapped_p2var])


    # if no ancillary is needed, then mapped physical qubits are not changed
    # we propagate this information using binary clauses:
    # using constraints 4, for initial experimentation (to see any difference if adding):
    if (self.args.constraints > 3 and self.args.ancillary == 0):
      for p_ind in range(self.num_pqubits):
        cur_mvar = self.cur_sb.mapped_pvars[p_ind]
        pre_mvar = self.blocks[tstep-1].mapped_pvars[p_ind]
        iff_clauses(self,cur_mvar,[pre_mvar])

def disable_distance_qubits(self):
    #print("disable distance qubits")
    for k,pairs in self.reverse_swap_distance_dict.items():
      if (k+1 > self.num_lqubits):
        for (p1,p2) in pairs:
          AtmostOne_constraints(self,[self.cur_sb.mapped_pvars[p1],self.cur_sb.mapped_pvars[p2]])

def swapp_exclusion_constraints(self):
    # in the physical swap auxiliary variables, we exclude the combinations of physical qubit that are not connected:
    for k,pairs in self.reverse_swap_distance_dict.items():
      if (k != 0):
        for (p1,p2) in pairs:
          p1_var,p2_var = self.cur_sb.swaps_p[p1],self.cur_sb.swaps_p[p2]
          # if p1_var is true, then p2_var is false:
          if_then_clause(self,p1_var,[-p2_var])

def lqubit_connection_constraints(self,pq_pair_vars,lq_pairs,bicoupling_map):
    # for each logical connected pair, we imply physical qubits are connected if physical pair is true:
    # p_pair -> (p1 & p2) & (p1 & p2) -> p_pair
    for l_index in range(len(self.lq_pair_list)):
      p_list = pq_pair_vars[l_index]
      l_qubit1, l_qubit2 = self.lq_pair_list[l_index]
      for p_index in range(len(bicoupling_map)):
        [p1_index,p2_index] = bicoupling_map[p_index]
        p_pair = p_list[p_index]
        p1,p2 = self.cur_sb.mlvars[l_qubit1][p1_index],self.cur_sb.mlvars[l_qubit2][p2_index]
        #print(p_pair,p1,p2)
        if (self.args.constraints == 0):
          if_then_each_clause(self,p_pair,[p1,p2])
        else:
          iff_then_each_clause(self,p_pair,[p1,p2])

    # for each logical connection, we add biimplies with all the physical connections:
    # l -> (p1 V ... V pk) & (p1 V ... V pk) -> l
    for l_index in range(len(self.lq_pair_list)):
      l_qubit = lq_pairs[l_index]
      p_qubit_connection_vars = pq_pair_vars[l_index]
      if (self.args.constraints == 0):
        if_then_clause(self,l_qubit,p_qubit_connection_vars)
      else:
        iff_clauses(self,l_qubit,p_qubit_connection_vars)

# instead of auxiliary variables, we give clauses directly for connectivity:
def lqubit_distance_constraints(self):
    for lq_ind in range(len(self.lq_pair_list)):
      l1, l2 = self.lq_pair_list[lq_ind]
      lq_var = self.cur_sb.lq_pairs[lq_ind]
      for i in range(self.max_swap_distance+1):
        if (i == 0):
          cur_lq_var = lq_var
        else:
          cur_lq_var = -lq_var
        for (p1,p2) in self.reverse_swap_distance_dict[i]:
          #print(l1,l2,p1,p2)
          # if l1 and l2 are mapped to distance p1, p2 then lq_pair var with (l1,l2) be always true/false:
          add_mapping_distance_var_clauses(self,l1,l2,p1,p2,cur_lq_var)

# instead of auxiliary variables, we give clauses directly for connectivity:
def lqubit_bridge_distance_constraints(self,tstep):
    for lq_ind in range(len(self.lq_pair_list)):
      l1, l2 = self.lq_pair_list[lq_ind]
      blq_var = self.cur_sb.bridge_lq_pairs[lq_ind]
      for i in range(1,self.max_swap_distance+1):
        if (i == 1):
          cur_blq_var = blq_var
        else:
          cur_blq_var = -blq_var
        for (p1,p2) in self.reverse_swap_distance_dict[i]:
          #print(l1,l2,p1,p2)
          # if l1 and l2 are mapped to distance p1, p2 then lq_pair var with (l1,l2) be always true/false:
          add_mapping_distance_var_clauses(self,l1,l2,p1,p2,cur_blq_var)


# implies var is (l1,l2) are mapped to (p1,p2), or if (l1,l2) to (p2,p1):
def add_mapping_distance_var_clauses(self,l1,l2,p1,p2,var):
    if_and_then_clause(self,[self.cur_sb.mlvars[l1][p1],self.cur_sb.mlvars[l2][p2]],[var])
    if_and_then_clause(self,[self.cur_sb.mlvars[l1][p2],self.cur_sb.mlvars[l2][p1]],[var])

# implies var is (l1,l2) are mapped to (p1,p2), or if (l1,l2) to (p2,p1):
def add_mapping_distance_var_t_clauses(self,l1,l2,p1,p2,var,t):
    if_and_then_clause(self,[self.blocks[t].mlvars[l1][p1],self.blocks[t].mlvars[l2][p2]],[var])
    if_and_then_clause(self,[self.blocks[t].mlvars[l1][p2],self.blocks[t].mlvars[l2][p1]],[var])


# we generate long distance constraints for lqqubit pairs:
def lqubit_long_distance_constraints(self,tstep):
    # setting max swap restriction distance:
    if (self.args.lp_distance == -1):
       max_distance = self.max_swap_distance
    else:
       max_distance = self.args.lp_distance
    # For each time step, we connect sdistance pairs to mapping vars:
    for lq_ind in range(len(self.lq_pair_list)):
      #print("==============================================",lq_ind)
      l1, l2 = self.lq_pair_list[lq_ind]
      cur_var = self.cur_sb.lq_pairs[lq_ind]
      for swap_distance in range(1,max_distance+1):
        # we go back wards to specify the lq vars are false upto swap distance - 1:
        #print("swap distance", swap_distance)
        for swapd_allowed in range(1,swap_distance):
          new_tstep = tstep - swapd_allowed
          if (new_tstep >= 0):
            #print(tstep, new_tstep, swapd_allowed)
            new_var = self.blocks[new_tstep].lq_pairs[lq_ind]
            # for every pair that is equal or more than swap distance, we know the lq pair var cannot be set to true:
            for k in range(swap_distance,self.max_swap_distance+1):
              #print("k,swap distance", k, swap_distance)
              for (p1,p2) in self.reverse_swap_distance_dict[k]:
                add_mapping_distance_var_clauses(self,l1,l2,p1,p2,-new_var)
                add_mapping_distance_var_t_clauses(self,l1,l2,p1,p2,-cur_var,new_tstep)


def predecessor_constraints(self,tstep):
    # predecessor constraints:
    # if a cnot var is true in timestep i, then itself and its predecessor cannot be true in all the coming time steps:
    for cnot_dep_timestep in range(0,tstep):
      previous_cnot_vars = self.blocks[cnot_dep_timestep].cnot_vars
      for key,predecessors in self.cx_predecessors.items():
        cnot_key_pos = self.cnot_dict[key]
        previous_cnot_var = previous_cnot_vars[cnot_key_pos]
        # for each of the predecessor, we say if this is true then later time step predcessor must be false:
        for predecessor in predecessors:
          predecessor_key = self.cnot_dict[predecessor]
          AtmostOne_constraints(self,[previous_cnot_var,self.cur_sb.cnot_vars[predecessor_key]])

def twoway_constraints(self,tstep):
    #print(self.list_cx_gates)
    #print(self.cx_predecessors)
    #print(self.cx_successors)
    for cnot_ind in range(len(self.list_cx_gates)):
      cnot = self.list_cx_gates[cnot_ind]
      predlist_cnot_var, cur_cnot_var, succlist_cnot_var = self.cur_sb.pred_cnot_var_dict[cnot], self.cur_sb.cnot_var_dict[cnot], self.cur_sb.succ_cnot_var_dict[cnot]
      #print(cnot,predlist_cnot_var, cur_cnot_var, succlist_cnot_var)
      # ExactlyOne constraints on P,C,S vars for each cnot:
      # every cnot must be true either in the same block or before or after:
      ExactlyOne_constraints(self,[predlist_cnot_var, cur_cnot_var, succlist_cnot_var])

      # predecessor constraints:

      # if tstep 0 then the predecessor list must be all zero:
      if (tstep == 0):
        unit_clause(self,-predlist_cnot_var)

      # if c is true, then each of its predecessor must be true in either same block
      # or in the predecessor list, which implies in some previous block:
      if (cnot in self.cx_predecessors):
        #print(cnot,self.cx_predecessors[cnot])
        for pred_cnot in self.cx_predecessors[cnot]:
          predlist_predcnot_var = self.cur_sb.pred_cnot_var_dict[pred_cnot]
          cur_predcnot_var = self.cur_sb.cnot_var_dict[pred_cnot]
          #print(cur_cnot_var, predlist_predcnot_var, cur_predcnot_var)
          if_then_clause(self,cur_cnot_var,[cur_predcnot_var,predlist_predcnot_var])

      # if p is true, then its own predecessors in the predecessor list are true within the same block:
      if (cnot in self.cx_predecessors):
        #print(cnot,self.cx_predecessors[cnot])
        for pred_cnot in self.cx_predecessors[cnot]:
          predlist_predcnot_var = self.cur_sb.pred_cnot_var_dict[pred_cnot]
          #print(predlist_predcnot_var)
          if_then_clause(self,predlist_cnot_var,[predlist_predcnot_var])

      #   interblock predecessor constraints:
      #   any p can only be true, iff it is true in previous predecessor list or previous cur cnot list:
      if (tstep > 0):
        previous_predlist_cnot_var = self.blocks[tstep-1].pred_cnot_var_dict[cnot]
        previous_cnot_var = self.blocks[tstep-1].cnot_var_dict[cnot]
        #print(previous_predlist_cnot_var,previous_cnot_var)
        if_then_clause(self,predlist_cnot_var,[previous_predlist_cnot_var,previous_cnot_var])
        if_then_clause(self,previous_predlist_cnot_var,[predlist_cnot_var])
        if_then_clause(self,previous_cnot_var,[predlist_cnot_var])


      # sucessor constraints:

      # last time step needs sucessor list to be all zero, but we add them as assumptions:

      # if c is true, then each of its successor must be true in either same block
      # or in the successor list, which implies in some later block:
      if (cnot in self.cx_successors):
        #print(cnot,self.cx_successors[cnot])
        for succ_cnot in self.cx_successors[cnot]:
          succlist_succnot_var = self.cur_sb.succ_cnot_var_dict[succ_cnot]
          cur_succnot_var = self.cur_sb.cnot_var_dict[succ_cnot]
          #print(cur_cnot_var, succlist_succnot_var, cur_succnot_var)
          if_then_clause(self,cur_cnot_var,[succlist_succnot_var, cur_succnot_var])


      # if s is true, then its own sucessors must be true in the successor list within the same block:
      if (cnot in self.cx_successors):
        #print(cnot,self.cx_successors[cnot])
        for succ_cnot in self.cx_successors[cnot]:
          succlist_succcnot_var = self.cur_sb.succ_cnot_var_dict[succ_cnot]
          #print(succlist_succcnot_var)
          if_then_clause(self,succlist_cnot_var,[succlist_succcnot_var])


      #   interblock successor constraints:
      #   any s can only be true, iff it is true in next successor list or next cur cnot list:
      # since we do incremental, previous timestep successor cnot is true iff current cnot is true or current successor is true:
      if (tstep > 0):
        previous_succcnot_var = self.blocks[tstep-1].succ_cnot_var_dict[cnot]
        #print(previous_succcnot_var,cur_cnot_var, succlist_cnot_var)
        if_then_clause(self,previous_succcnot_var,[cur_cnot_var, succlist_cnot_var])
        if_then_clause(self,cur_cnot_var,[previous_succcnot_var])
        if_then_clause(self,succlist_cnot_var,[previous_succcnot_var])


      # pushing all the cnots to top whenever possible:
      # if a cnots predecessors are not postponed, then cnot cannot be postponed unless logical qubit pair is not connected:
      if (cnot in self.cx_predecessors):
        #print(cnot,self.cx_predecessors[cnot])
        if_cond_list = []
        for pred_cnot in self.cx_predecessors[cnot]:
          # not in the successor list means the predecessor is not postponed:
          if_cond_list.append(-self.cur_sb.succ_cnot_var_dict[pred_cnot])
        # if current cnot is postponed:
        if_cond_list.append(succlist_cnot_var)
        # implies that the logical qubit pair is not connected:
        qubit_pair = single_direction(self.cx_dict[cnot],self.cur_sb.lq_pair_dict)
        if_and_then_clause(self,if_cond_list,[-self.cur_sb.lq_pair_dict[qubit_pair]])


def ALO_twoway_cnot_constraints(self, tstep):

    # if tstep is 0, then one of the cnots is true:
    if tstep == 0:
      AtleastOne_constraints(self,self.cur_sb.cnot_vars)

    # we imply using the assumption cnot var:
    # TODO check if it makes a difference, if not remove:
    if (self.args.constraints == 0):
      if_then_clause(self,self.cur_sb.cnot_ass_var,self.cur_sb.cnot_vars)

    # if assumption var is true, then all the successor vars are false:
    if_then_each_not_clause(self,self.cur_sb.cnot_ass_var,self.cur_sb.succ_cnot_vars)

    # previous cnot assumption var must be false:
    if tstep > 0:
      unit_clause(self,-self.blocks[tstep-1].cnot_ass_var)

      
# equality clauses for grouped cnots:
def grouped_cnot_constraints(self):
    for cur_cnot in self.list_cx_gates:
      cur_cnot_var = self.cur_sb.cnot_var_dict[cur_cnot]
      if (cur_cnot in self.group_cnot_dict):
        dep_cnot = self.group_cnot_dict[cur_cnot]
        dep_cnot_var = self.cur_sb.cnot_var_dict[dep_cnot]
        if_then_clause(self,cur_cnot_var,[dep_cnot_var])
        if_then_clause(self,dep_cnot_var,[cur_cnot_var])

def ALO_cnot_constraints(self, tstep):

    # we only imply using the cnot var:
    # Note: using assumption var directly might be faster:
    if (self.args.constraints == 0):
      if_then_clause(self,self.cur_sb.cur_cnot_var,self.cur_sb.cnot_vars)
    else:
      iff_clauses(self,self.cur_sb.cur_cnot_var,self.cur_sb.cnot_vars)
    # if tstep is 0, then one of the cnots is true:
    if tstep == 0:
      unit_clause(self,self.cur_sb.cur_cnot_var)

    # in the current time step, we use the assumption var to imply atleast one cnot var (for incremental solving):
    if_then_clause(self,self.cur_sb.cnot_ass_var, [self.cur_sb.cur_cnot_var])

    # every cnot must be true in atleast one of the time steps:
    for cnot_index in range(len(self.list_cx_gates)):
      # we imply every clause only if the assumption var is true,
      # useful for incremental solving:
      single_cnot_clause = []
      for i_index in range(0,tstep):
        single_cnot_clause.append(self.blocks[i_index].cnot_vars[cnot_index])
      single_cnot_clause.append(self.cur_sb.cnot_vars[cnot_index])
      if_then_clause(self,self.cur_sb.cnot_ass_var,single_cnot_clause)

    # previous cnot assumption var must be false:
    if tstep > 0:
      unit_clause(self,-self.blocks[tstep-1].cnot_ass_var)


def cnot_to_lqubitpair_constraints(self):
    # for each cnot gate, we imply if the cnot is true then the corresponding logical qubit pair is connected:
    for i in range(len(self.list_cx_gates)):
      qubit_pair = single_direction(self.cx_dict[self.list_cx_gates[i]],self.cur_sb.lq_pair_dict)
      if_then_clause(self,self.cur_sb.cnot_vars[i],[self.cur_sb.lq_pair_dict[qubit_pair]])

########################################################################################
# Techniques for search space reduction:
########################################################################################


def initialise_symmetries(self):
      start_symmetry_breaking_time = time.perf_counter()
      self.isomorphic_implications = compute_isomporphic_physical_qubits(self.args, self.bi_coupling_map, self.num_pqubits)
      symmetry_breaking_time = time.perf_counter() - start_symmetry_breaking_time
      if self.args.verbose > -1:
        print("Symmetry Breaking time: " + str(symmetry_breaking_time))

def break_symmetries(self, cur_mlvars):
    # by default we break symmetry on the first and second logical qubit:
    first_lqubit = 0
    second_lqubit = 1
    for isomorphic_implication in self.isomorphic_implications:
      cur_clause = []
      (conditions,implications) = isomorphic_implication
      # Either the implications are for the first qubit where the condition is empty or
      if (len(conditions) == 0):
        # adding the constraints for the first qubit directly:
        for implication in implications:
          cur_clause.append(cur_mlvars[first_lqubit][implication])
        or_clause(self,cur_clause)
      # for the second qubit when the conditions are non empty:
      else:
        assert(len(conditions) == 1)
        # implication with first qubit:
        for implication in implications:
          cur_clause.append(cur_mlvars[second_lqubit][implication])
        # TODO: use binary clauses instead:
        if_then_clause(self,cur_mlvars[first_lqubit][conditions[0]],cur_clause)

# TODO bug found, to be fixed
# Restricts swaps by holding two conditions:
# - every sequence of swaps must repair atleast one CNOT/Logical pair
# - every swap in such a sequence must act on either of the logical pair
def restrict_swaps(self,tstep):
    # Part 1:
    # Exactly one witness is true (TODO can relax it to atleast one):
    ExactlyOne_constraints(self,self.cur_sb.witness_lpair_vars)

    # exactly one witness cnot is true if atleast one cnot is true:
    AtmostOne_constraints(self,self.cur_sb.witness_cnot_vars)
    if_then_clause(self,self.cur_sb.cur_cnot_var,self.cur_sb.witness_cnot_vars)
    # if no cnot is used then all witness cnots are forced to 0:
    if_then_each_not_clause(self,-self.cur_sb.cur_cnot_var,self.cur_sb.witness_cnot_vars)

    # start/restart logical qubit witness
    # if atleast one of the cnot is applied in previous block
    # then there exists a witness logical qubit pair which indicates previous logical qubit pair which is not satisfied:
    for lq_ind in range(len(self.lq_pair_list)):
      cur_wlq_var = self.cur_sb.witness_lpair_vars[lq_ind]
      pre_lq_var = self.blocks[tstep-1].lq_pairs[lq_ind]
      if_and_then_clause(self,[self.blocks[tstep-1].cur_cnot_var,cur_wlq_var],[-pre_lq_var])

    if (tstep > 1):
      # propagate witness
      # if no cnot is applied in the previous time step
      # then propagate witness logical qubit pairs from last time step to this time step:
      for lq_ind in range(len(self.lq_pair_list)):
        pre_wlq_var = self.blocks[tstep-1].witness_lpair_vars[lq_ind]
        cur_wlq_var = self.cur_sb.witness_lpair_vars[lq_ind]
        if_and_then_equal_clauses(self,[-self.blocks[tstep-1].cur_cnot_var],pre_wlq_var,cur_wlq_var)

    # witness is satisfied:
    # if a witness cnot is true then the corresponding cnot, witness logical pair and logical pair are all true: 
    for i in range(len(self.list_cx_gates)):
      wq_pair = single_direction(self.cx_dict[self.list_cx_gates[i]],self.cur_sb.witness_lq_pair_dict)
      wlq_var = self.cur_sb.witness_lq_pair_dict[wq_pair]
      lq_var = self.cur_sb.lq_pair_dict[wq_pair]
      if_then_each_clause(self,self.cur_sb.witness_cnot_vars[i],[self.cur_sb.cnot_vars[i],wlq_var,lq_var])

    # swaps are always consistent with the witness logical variables
    # in each block, every swap applied must act on one of the witness logical variables:
    for l_index in range(len(self.lq_pair_list)):
      l1, l2 = self.lq_pair_list[l_index]
      witness_lq = self.cur_sb.witness_lpair_vars[l_index]
      for p_index in range(len(self.scoupling)):
        [p1,p2] = self.scoupling[p_index]
        swap_var = self.cur_sb.swaps[p_index]
        # witness (l1,l2) and swap (p1,p2) -> (mlvars[l1][p1] V mlvars[l1][p2] V mlvars[l2][p1] V mlvars[l2][p2])
        if_and_then_clause(self,[witness_lq,swap_var],[self.cur_sb.mlvars[l1][p1],self.cur_sb.mlvars[l1][p2],self.cur_sb.mlvars[l2][p1],self.cur_sb.mlvars[l2][p2]])

    # TODO: Avoiding redundant swaps
