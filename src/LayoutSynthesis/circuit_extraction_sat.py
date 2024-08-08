# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from src.LayoutSynthesis.mapped_unmapped import MappedUnmappedCircuit
from src.LayoutSynthesis.circuit_utils import gate_get_qubit

class CircuitExtractionSAT:

  def extract(self, sat_instance):

    for t in range(len(sat_instance.blocks)):
      # we extract swap actions:
      if (t != 0):
        if (sat_instance.args.bridge == 0 or sat_instance.model[sat_instance.blocks[t].swap_ivar-1] > 0):
          for ind in range(len(sat_instance.scoupling)):
            swap_var = sat_instance.blocks[t].swaps[ind]
            if (sat_instance.model[swap_var-1] > 0):
              swap_p1_index,swap_p2_index = sat_instance.scoupling[ind][0],sat_instance.scoupling[ind][1]
                    
              # finding the logical qubits that are being swapped, we need the values from last time step:
              p1_logical_vars = sat_instance.blocks[t-1].mpvars[swap_p1_index]
              p2_logical_vars = sat_instance.blocks[t-1].mpvars[swap_p2_index]

              l1 = None
              l2 = None
              for l_index in range(sat_instance.num_lqubits):
                if (sat_instance.model[p1_logical_vars[l_index]-1] > 0):
                  l1 =  l_index
                if (sat_instance.model[p2_logical_vars[l_index]-1] > 0):
                  l2 =  l_index
              self.map_unmap.apply_swap(l1, l2, swap_p1_index, swap_p2_index)
        else:
          # if we allow bridges, empty swaps are allowed:
          assert(sat_instance.args.bridge == 1)
      else:
        # initial mapping:
        for l_index in range(sat_instance.num_lqubits):
          cur_physical_vars = sat_instance.blocks[t].mlvars[l_index]
          for p_index in range(sat_instance.num_pqubits):
            if (sat_instance.model[cur_physical_vars[p_index]-1] > 0):
              self.map_unmap.map_initial(l_index, p_index)

      cur_cnot_vars = sat_instance.blocks[t].cnot_vars
      for cur_cnot_index in range(len(cur_cnot_vars)):
        cur_cnot = cur_cnot_vars[cur_cnot_index]
        if(sat_instance.model[cur_cnot-1] > 0):
          # also computing mapped physical qubits:
          cur_gate = sat_instance.logical_circuit[sat_instance.list_cx_gates[cur_cnot_index]]

          l1 = gate_get_qubit(cur_gate,0)
          l1_physical_vars = sat_instance.blocks[t].mlvars[l1]
          l2 = gate_get_qubit(cur_gate,1)
          l2_physical_vars = sat_instance.blocks[t].mlvars[l2]

          # the var which is true is the mapped physical qubit:
          for p_index in range(sat_instance.num_pqubits):
            if (sat_instance.model[l1_physical_vars[p_index]-1] > 0):
              p1 = p_index
            if (sat_instance.model[l2_physical_vars[p_index]-1] > 0):
              p2 = p_index

          if ([p1,p2] in sat_instance.bi_coupling_map):
            self.map_unmap.apply_cnot(l1,l2,p1,p2,sat_instance.list_cx_gates[cur_cnot_index])
          else:
            assert([p1,p2] in sat_instance.bridge_bicoupling_map)
            # get first middle pqubit:
            if ((p1,p2) in sat_instance.bridge_middle_pqubit_dict):
              middle_p =  sat_instance.bridge_middle_pqubit_dict[(p1,p2)][0]
            else:
              assert((p2,p1) in sat_instance.bridge_middle_pqubit_dict)
              middle_p =  sat_instance.bridge_middle_pqubit_dict[(p2,p1)][0]
            self.map_unmap.apply_bridge(l1,l2,p1,middle_p,p2,sat_instance.list_cx_gates[cur_cnot_index])


  # uses the plan for extracting mapped circuit:
  def __init__(self,args,sat_instance):

    assert(args.model == "sat")

    self.map_unmap = MappedUnmappedCircuit(args, sat_instance.logical_circuit, sat_instance.num_pqubits, sat_instance.coupling_map)

    self.extract(sat_instance)
    mapped_circuit = self.map_unmap.get_mapped_circuit()
    mapped_circuit = self.map_unmap.get_measured_circuit()
    
    if (args.verbose > 0):
      if (args.verbose > 2):
        print(QuantumCircuit.qasm(self.map_unmap.mapped_circuit))
      print("mapped circuit:")
      print(mapped_circuit)

    # we print this even in silent mode, since this is the main result
    report_h = f"({self.map_unmap.number_of_h} extra H-gates)" if self.map_unmap.number_of_h > 0 else ""
    report_b = f"({self.map_unmap.number_bridges} bridges)" if  self.map_unmap.number_bridges > 0 else ""
    print("Number of additional swaps:", self.map_unmap.number_of_swaps, report_b, report_h)
