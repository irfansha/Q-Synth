# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit

class CircuitExtractionGlobal:

  def extract(self,args,pddl_instance, plan):

    # parsing plan and generate a dict with time steps:
    plan_time_dict = {}
    # we update the logical and physical qubit mapping:
    self.logical_physical_map = {}
    self.measurement_copy = {}
    self.reverse_init_mapping = {}

    # first depth label for discrete/global model:
    if (args.model == "global"):
      cur_depth =  "d0"
    for step in plan:
      if ("map_initial" == step[0]):
        self.logical_physical_map[step[1]] = step[2]
        self.measurement_copy[step[1]] = step[2]
        self.reverse_init_mapping[step[2]] = step[1]
      elif ("move_depth" in step[0]):
        cur_depth = step[2]
        #print(step)
      elif ("apply_cnot" == step[0]):
        # we only need to remember the physical qubits the cnot/swap is applied:
        if (step[-1] not in plan_time_dict):
          plan_time_dict[step[-1]] = [step[:-1]]
        else:
          plan_time_dict[step[-1]].append(step[:-1])
      elif ("swap" in step[0]):
        if (args.model == "global"):
          if (cur_depth not in plan_time_dict):
            plan_time_dict[cur_depth] = [step]
          else:
            plan_time_dict[cur_depth].append(step)
        else:
          if (step[-1] not in plan_time_dict):
            plan_time_dict[step[-1]] = [step[:-1]]
          else:
            plan_time_dict[step[-1]].append(step[:-1])


    #print(plan_time_dict)
    # we maintain the current physical mapping of logical qubits, at each layer:
    
    # we add circuit layer by layer:
    self.mapped_circuit = []

    for i,layer in enumerate(pddl_instance.input_dag.layers()):
      subdag = layer['graph']
      # differentiating layers that are in the plan dict and that are not:
      layer_index =  "d" + str(i + 1)
      if (layer_index not in plan_time_dict):
        for node in subdag.op_nodes():
          #print(node.name, node.op.num_qubits, node.qargs, node.cargs)
          # we know there are no 2 bits operators or more here:
          if node.op.num_qubits != 1:
            print(f"Error: can only handle unary gates and CX gates. Found {node.name} on {node.op.num_qubits} qubits")
            exit(-1)
          if len(node.op.params) != 0:
            assert(len(node.op.params) == 1)
            self.mapped_circuit.append(node.name + "(" +str(node.op.params[0]) + ") q[" + str(self.logical_physical_map["l" + str(node.qargs[0].index)][1:]) + "];") 
          else:
            # using logical map for finding the right physical qubit after probable swapping:
            self.mapped_circuit.append(node.name + " q[" + str(self.logical_physical_map["l" + str(node.qargs[0].index)][1:]) + "];")
      else:
        for node in subdag.op_nodes():
          # single bit operators are not touched, even with swapping:
          if (node.op.num_qubits == 1):
            if (len(node.op.params) != 0):
              assert(len(node.op.params) == 1)
              self.mapped_circuit.append(node.name + "(" +str(node.op.params[0]) + ") q[" + str(self.logical_physical_map["l" + str(node.qargs[0].index)][1:]) + "];") 
            else:
              # using logical map for finding the right physical qubit after probable swapping:
              self.mapped_circuit.append(node.name + " q[" + str(self.logical_physical_map["l" + str(node.qargs[0].index)][1:]) + "];")
        # now we handle all the plan actions within step that covers all the 2 qubit operators:
        for plan_action in plan_time_dict[layer_index]:
          # for swap, we swap the qubits:
          if ("swap_ancillary" == plan_action[0]):
            # we increment the number of swaps:
            self.number_of_swaps += 1
            #print(self.logical_physical_map, plan_action)
            # first logical qubit is mapped to 2nd physical qubit:
            self.logical_physical_map[plan_action[1]] = plan_action[3]
            # connecting the physical qubits:
            self.mapped_circuit.append("swap q[" + str(plan_action[2][1:]) + "],q[" + str(plan_action[3][1:]) +"];")
            #print(self.logical_physical_map)
          elif ("swap" == plan_action[0]):
            # we increment the number of swaps:
            self.number_of_swaps += 1
            #print(self.logical_physical_map, plan_action)
            # first logical qubit is mapped to 2nd physical qubit:
            self.logical_physical_map[plan_action[1]] = plan_action[4]
            # second logical qubit is mapped to 1st physical qubit:
            self.logical_physical_map[plan_action[2]] = plan_action[3]
            # connecting the physical qubits:
            self.mapped_circuit.append("swap q[" + str(plan_action[3][1:]) + "],q[" + str(plan_action[4][1:]) +"];")
          elif("apply_cnot" == plan_action[0]):
            self.mapped_circuit.append("cx q[" + str(plan_action[3][1:]) + "],q[" + str(plan_action[4][1:]) +"];")


  def mapped_circuit_to_string(self, pddl_instance):

    self.mapped_circuit_string = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
    self.mapped_circuit_string += "qreg q[" + str(pddl_instance.num_physical_qubits) +"];\n"
    # for measurement if needed:
    self.mapped_circuit_string += "creg c[" + str(pddl_instance.num_physical_qubits) +"];\n"

    for instruction in self.mapped_circuit:
      self.mapped_circuit_string += instruction + "\n"

    # adding barrier:
    self.mapped_circuit_string += "\nbarrier q;\n"

    for lqubit,pqubit in self.logical_physical_map.items():
      self.mapped_circuit_string += "measure q["+ pqubit[1:] + "] -> c["+ lqubit[1:] +"];\n"

  # uses the plan for extracting mapped circuit:
  def __init__(self, args,pddl_instance, plan):

    self.number_of_swaps = 0

    self.extract(args,pddl_instance,plan)
    self.mapped_circuit_to_string(pddl_instance)
    mapped_circuit = QuantumCircuit.from_qasm_str(self.mapped_circuit_string)

    # writing circuit out if specified:
    if (args.circuit_out != None):
      QuantumCircuit.qasm(mapped_circuit,filename=args.circuit_out)

    #print(self.mapped_circuit_string)
    if (args.verbose > 0):
      print(mapped_circuit)
    print("Number of additional swaps: ", self.number_of_swaps)