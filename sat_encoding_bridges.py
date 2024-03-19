# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from sat_utils import *

from variable_dispatcher import VarDispatcher as vd
from sat_block import SatBlock as sb


from pysat.solvers import Solver
from pysat.card import *
from pysat.formula import CNF

class SatEncodingBridges:

  def swap_constraints(self, cur_mpvars, tstep):
    for ind in range(len(self.scoupling)):
      swap_var = self.cur_sb.swaps[ind]
      swapp_var1,swapp_var2 = self.cur_sb.swaps_p[self.scoupling[ind][0]],self.cur_sb.swaps_p[self.scoupling[ind][1]]
      if (self.args.constraints == 0):
        if_then_each_clause(self,swap_var,[swapp_var1,swapp_var2])
      else:
        # we add the following constraints: swap_var -> (swap_p1_var & swap_p2_var) & (swap_p1_var & swap_p2_var) -> swap_var:
        iff_then_each_clause(self,swap_var,[swapp_var1,swapp_var2])


    # exactly one of the swap variables must be true:
    AtmostOne_constraints(self,self.cur_sb.swaps)
    # exactly two auxiliary p variables are true:
    AtmostTwo_constraints(self,self.cur_sb.swaps_p)

    swap_comb_list = [self.cur_sb.swaps,self.cur_sb.swaps_p]

    for var_list in swap_comb_list:

      # we use swap indication var to force all vars to 0 if swap is not chosen:
      if_then_each_not_clause(self,-self.cur_sb.swap_ivar,var_list)

      if (self.args.constraints == 0):
        # Similarly, if swap indication var is true then one of the swap, p1, p2 vars must be true:
        if_then_clause(self,self.cur_sb.swap_ivar,var_list)
      else:
        # Similarly, if swap indication var is true iff one of the swap, p1, p2 vars are true:
        iff_clauses(self,self.cur_sb.swap_ivar,var_list)


    # exclusion clauses for swap p auxiliary variables:
    if (self.args.constraints > 1):
      swapp_exclusion_constraints(self)

    # if the physical qubits in mapping are not touched by swap, we propagate to the current mapping variables:
    for p_ind in range(self.num_pqubits):
      p = self.cur_sb.swaps_p[p_ind]
      prev_pvars = self.blocks[tstep-1].mpvars[p_ind]
      cur_pvars = cur_mpvars[p_ind]
      # we generate followling clauses for each pair of physical qubits in previous and current time step:
      # (-p) -> (previous_physical_vars[i] <==> current_physical_vars[i])
      for swap_l_index in range(self.num_lqubits):
        if_and_then_equal_clauses(self,[-p],prev_pvars[swap_l_index], cur_pvars[swap_l_index])

    # if swap is involved we need to swap different pairs of mapping qubits:
    for swap_ind in range(len(self.cur_sb.swaps)):
      cur_swap_var = self.cur_sb.swaps[swap_ind]
      # depending on the swap var index, we first get the swapping physical qubits var indexes:
      p1_index,p2_index = self.scoupling[swap_ind]
      for i in range(0,2):
        if (i == 0):
          # (cur_swap_var) -> (previous_p1_vars <==> current_p2_vars)
          prev_pvars = self.blocks[tstep-1].mpvars[p1_index]
          cur_pvars = cur_mpvars[p2_index]
        else:
          # (cur_swap_var) -> (previous_p2_vars <==> current_p1_vars)
          prev_pvars = self.blocks[tstep-1].mpvars[p2_index]
          cur_pvars = cur_mpvars[p1_index]
        for ind in range(self.num_lqubits):
          if_and_then_equal_clauses(self,[cur_swap_var],prev_pvars[ind], cur_pvars[ind])


  def cnot_to_lqubitpair_bridge_constraints(self,tstep):
    # for each cnot gate, we imply if the cnot is true then the corresponding logical qubit pair is connected or it is a bridge cnot gate:
    for i in range(len(self.list_cx_gates)):
      qubit_pair = single_direction(self.cx_dict[self.list_cx_gates[i]],self.cur_sb.lq_pair_dict)
      if_then_clause(self,self.cur_sb.cnot_vars[i],[self.cur_sb.lq_pair_dict[qubit_pair], self.cur_sb.bridge_cnots[i]])

      # we also constraint bridge cnot variables to bridge
      bridge_qubit_pair = single_direction(self.cx_dict[self.list_cx_gates[i]],self.cur_sb.bridge_lq_pair_dict)
      if_then_clause(self,self.cur_sb.bridge_cnots[i],[self.cur_sb.bridge_lq_pair_dict[bridge_qubit_pair]])

      if (self.args.constraints > 0):
        # we disable bridges if the cnot lpair is true and viceversa:
        AtmostOne_constraints(self,[self.cur_sb.lq_pair_dict[qubit_pair],self.cur_sb.bridge_lq_pair_dict[bridge_qubit_pair]])

    # atmost one constraints for the bridge cnot gates:
    AtmostOne_constraints(self,self.cur_sb.bridge_cnots)


    iff_clauses(self,self.cur_sb.bridge_ivar,self.cur_sb.bridge_cnots)
    
  # Parses domain and problem file:
  def __init__(self, args):
    self.args = args
    self.new_vars = vd()

    self.encoding_blocks = []
    self.blocks = []

    self.status = False
    tstep = -1

    if self.args.verbose > -1:
      print(f"Generating SAT encoding with bridges, solving with {self.args.solver}")

    parse_and_compute(self)
    set_architecture(self)

    # Number of logical qubits must be less than or equal to number of physical qubits:
    if (self.num_lqubits > self.num_pqubits):
      print(f"No solution: number of logical qubits is more than physical qubits ({self.num_lqubits} > {self.num_pqubits})")
      exit(-1)

    # computing isomorphic physical qubit sets:
    if (self.args.symmetry_breaking >= 1):
      assert(self.args.symmetry_breaking <= 2)
      initialise_symmetries(self)

    with Solver(use_timer=True, name=self.args.solver) as s:

      # We increment each block at a time, essentially it includes one additional swap from timestep 1:
      while (self.status == False):
        # we initialise for each time step:
        self.clause_list = CNF()

        tstep = tstep + 1
        if self.args.verbose > 0 and tstep >= args.start and (tstep - args.start) % args.step == 0 :
          print("Solving for time step: ", tstep, flush=True)
        self.cur_sb =  sb()
        self.cur_sb.tstep = tstep

        # Initial Mapping:
        #   We use a grid of variables with logical indexes on x axis and physical indexes on y axis
        cur_mlvars = []
        for i in range(self.num_lqubits):
          cur_mlvars.append(self.new_vars.get_vars(self.num_pqubits))

        # first block starts with 1:
        self.cur_sb.mlvars = cur_mlvars
        cur_mpvars = extract_physical_qubit_slices(self,cur_mlvars)
        self.cur_sb.mpvars = cur_mpvars


          # If symmetry breaking is opted, we restrict the first and second logical qubit:
        if (tstep == 0 and self.args.symmetry_breaking >= 1):
          # TODO: levels of constraints not added:
          break_symmetries(self,cur_mlvars)

        #  EQO for logical map variables
        #  AMO for physical map variables
        if (tstep == 0 or self.args.constraints > 1):
          for vars in cur_mlvars:
            AtmostOne_constraints(self,vars)
            if (self.args.constraints > 0):
              # if a model exists without mapping all logical qubits, that is allowed:
              # for stronger constraints we add atleast one constraints:
              AtleastOne_constraints(self,vars)
          for vars in cur_mpvars:
            AtmostOne_constraints(self,vars)

        if (tstep != 0):
          # we use a variable to indication swap application (useful when bridge constraints are added):
          self.cur_sb.swap_ivar = self.new_vars.get_single_var()
          # we add swap conditions, and propagation constraints for the mapping variables:
          # First for swap conditions, we allocate swap variables for non-symmetric physical connections:
          self.cur_sb.swaps = self.new_vars.get_vars(len(self.scoupling))
          self.cur_sb.swaps_p = self.new_vars.get_vars(self.num_pqubits)
          
          self.swap_constraints(cur_mpvars, tstep)


        # for any swaps, we do not need to generate this constraints:
        if (self.args.ancillary <= 1):
          initialize_ancillary_clauses(self,cur_mpvars)
          if (tstep != 0):
            ancillary_constraints(self,tstep)


        # variables for cnot qubits:
        self.cur_sb.cnot_vars = self.new_vars.get_vars(len(self.list_cx_gates))
        self.cur_sb.pred_cnot_vars = self.new_vars.get_vars(len(self.list_cx_gates))
        self.cur_sb.succ_cnot_vars = self.new_vars.get_vars(len(self.list_cx_gates))

        for i in range(len(self.list_cx_gates)):
          cnot = self.list_cx_gates[i]
          self.cur_sb.cnot_var_dict[cnot] = self.cur_sb.cnot_vars[i]
          self.cur_sb.pred_cnot_var_dict[cnot] = self.cur_sb.pred_cnot_vars[i]
          self.cur_sb.succ_cnot_var_dict[cnot] = self.cur_sb.succ_cnot_vars[i]

        # variables for connected logical qubits:
        self.cur_sb.lq_pairs = self.new_vars.get_vars(len(self.lq_pair_list))
        for i in range(len(self.lq_pair_list)):
          pair = self.lq_pair_list[i]
          self.cur_sb.lq_pair_dict[pair] =  self.cur_sb.lq_pairs[i]

        # we allocate variables:
        if (tstep != 0):
          self.cur_sb.bridge_ivar = self.new_vars.get_single_var()
          self.cur_sb.bridge_cnots = self.new_vars.get_vars(len(self.list_cx_gates))
          self.cur_sb.bridge_lq_pairs = self.new_vars.get_vars(len(self.lq_pair_list))
          for i in range(len(self.lq_pair_list)):
            pair = self.lq_pair_list[i]
            self.cur_sb.bridge_lq_pair_dict[pair] =  self.cur_sb.bridge_lq_pairs[i]

        # we do not need bridge constraints 0th time step:
        if (tstep == 0):
          cnot_to_lqubitpair_constraints(self)
        else:
          # we also need bridge constraints:
          self.cnot_to_lqubitpair_bridge_constraints(tstep)

        lqubit_distance_constraints(self)
        if (tstep != 0):
          #self.bridge_lqubit_connections_constraints()
          lqubit_bridge_distance_constraints(self,tstep)
          # for optimality, either swap or bridge can be applied in the same time step:
          if (self.args.near_optimal == 0):
            AtmostOne_constraints(self,[self.cur_sb.bridge_ivar,self.cur_sb.swap_ivar])
          if (self.args.constraints > 0):
            or_clause(self,[self.cur_sb.bridge_ivar,self.cur_sb.swap_ivar])
        #predecessor_constraints(self,tstep)
        twoway_constraints(self,tstep)

        if (self.args.group_cnots == 1):
          grouped_cnot_constraints(self)

        #self.cur_sb.cur_cnot_var = self.new_vars.get_single_var()
        self.cur_sb.cnot_ass_var = self.new_vars.get_single_var()
        #ALO_cnot_constraints(self,tstep)
        ALO_twoway_cnot_constraints(self,tstep)

        if (self.args.verbose > 2):
          print(self.cur_sb)

        # appending current clauses to the encoding blocks:
        self.encoding_blocks.append(self.clause_list)
        self.blocks.append(self.cur_sb)

        s.append_formula(self.clause_list.clauses)
        if tstep >= args.start and (tstep - args.start) % args.step == 0:
          self.status = s.solve([self.cur_sb.cnot_ass_var])
          if (self.status == True):
            self.model = s.get_model()
          if (self.args.verbose > 0):
            print(f'Finished step {tstep}. Time: {s.time():.4f}s. Result: {self.status}', flush=True)
          if (self.args.verbose > 1):
            print(s.accum_stats())
