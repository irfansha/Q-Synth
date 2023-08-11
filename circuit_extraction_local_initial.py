# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit

class CircuitExtractionLocalOld:

  def extract(self,args,pddl_instance, plan):
    # parsing plan and generate a dict with time steps:
    plan_time_dict = {}
    # we update the logical and physical qubit mapping:
    self.logical_physical_map = {}
    self.measurement_copy = {}
    self.reverse_init_mapping = {}

    # we add circuit layer by layer:
    self.mapped_circuit = []

    for step_index in range(len(plan)):
      step = plan[step_index]
      if ("map_initial" in step[0]):
        self.logical_physical_map[step[1]] = step[2]
        self.measurement_copy[step[1]] = step[2]
        self.reverse_init_mapping[step[2]] = step[1]
      elif ("swap" in  step[0]):
        # we increment the number of swaps:
        self.number_of_swaps += 1
        # first logical qubit is mapped to 2nd physical qubit:
        self.logical_physical_map[step[1]] = step[-1]
        # second logical qubit is mapped to 1st physical qubit:
        # we only map if the swap is a full swap, not if ancillary swap:
        if (len(step) == 5):
          self.logical_physical_map[step[2]] = step[-2]
        # connecting the physical qubits:
        self.mapped_circuit.append("swap q[" + str(step[-2][1:]) + "],q[" + str(step[-1][1:]) +"];")
      elif ("cnot" in step[0]):
        name1, name2, first_qubit, second_qubit,layer_index = step[0].split("_")
        int_first_qubit = int(first_qubit[1:])
        int_second_qubit = int(second_qubit[1:])
        int_layer_index = int(layer_index[1:])
        assert(name1 == "apply")
        assert(name2 == "cnot")
        # gathering single qubits before first qubit:
        # mapping logical qubit to the number:
        remove_list = []
        for (instruction_index,qubit) in pddl_instance.single_qubit_timestep_map[int_first_qubit]:
          if (instruction_index < int_layer_index):
            if (len(qubit.operation.params) != 0):
              assert(len(qubit.operation.params) == 1)
              self.mapped_circuit.append(qubit.operation.name + "(" +str(qubit.operation.params[0]) + ") q[" + str(self.logical_physical_map["l" + str(qubit.qubits[0].index)][1:]) + "];") 
            else:
              # using logical map for finding the right physical qubit after probable swapping:
              self.mapped_circuit.append(qubit.operation.name + " q[" + str(self.logical_physical_map["l" + str(qubit.qubits[0].index)][1:]) + "];")

            #print(qubit.operation.name,qubit.qubits[0].index)
            # we remember and remove after cnot operation:
            # this way we do not duplicate:
            remove_list.append((instruction_index,qubit))
        # removing each of the instruction:
        for pair in remove_list:
          pddl_instance.single_qubit_timestep_map[int_first_qubit].remove(pair)
        # emptying remove_list:
        remove_list = []
        # gathering single qubits before second qubit:
        # mapping logical qubit to the number:
        for (instruction_index,qubit) in pddl_instance.single_qubit_timestep_map[int_second_qubit]:
          if (instruction_index < int_layer_index):
            if (len(qubit.operation.params) != 0):
              assert(len(qubit.operation.params) == 1)
              self.mapped_circuit.append(qubit.operation.name + "(" +str(qubit.operation.params[0]) + ") q[" + str(self.logical_physical_map["l" + str(qubit.qubits[0].index)][1:]) + "];") 
            else:
              # using logical map for finding the right physical qubit after probable swapping:
              self.mapped_circuit.append(qubit.operation.name + " q[" + str(self.logical_physical_map["l" + str(qubit.qubits[0].index)][1:]) + "];")
            
            #print(qubit.operation.name,qubit.qubits[0].index)
            # we remember and remove after cnot operation:
            # this way we do not duplicate:
            remove_list.append((instruction_index,qubit))
        # removing each of the instruction:
        for pair in remove_list:
          pddl_instance.single_qubit_timestep_map[int_second_qubit].remove(pair)
        self.mapped_circuit.append("cx q[" + str(step[1][1:]) + "],q[" + str(step[2][1:]) +"];")
    
    # we need to list the last single qubit gates, i.e. the remaining ones:
    for qubit_id,lst in pddl_instance.single_qubit_timestep_map.items():
      for (instruction_id,qubit) in lst:
        if (len(qubit.operation.params) != 0):
          assert(len(qubit.operation.params) == 1)
          self.mapped_circuit.append(qubit.operation.name + "(" +str(qubit.operation.params[0]) + ") q[" + str(self.logical_physical_map["l" + str(qubit.qubits[0].index)][1:]) + "];") 
        else:
          # using logical map for finding the right physical qubit after probable swapping:
          self.mapped_circuit.append(qubit.operation.name + " q[" + str(self.logical_physical_map["l" + str(qubit.qubits[0].index)][1:]) + "];")


  def mapped_circuit_to_string(self, pddl_instance):

    self.mapped_circuit_string = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"
    self.mapped_circuit_string += "qreg q[" + str(pddl_instance.num_physical_qubits) +"];\n"
    # for measurement if needed:
    self.mapped_circuit_string += "creg c[" + str(pddl_instance.num_physical_qubits) +"];\n"

    for instruction in self.mapped_circuit:
      self.mapped_circuit_string += instruction + "\n"


    # adding barrier:
    self.mapped_circuit_string += "barrier q;\n"

    #print(self.logical_physical_map)

    for lqubit,pqubit in self.logical_physical_map.items():
      self.mapped_circuit_string += "measure q["+ pqubit[1:] + "] -> c["+ lqubit[1:] +"];\n"


  # uses the plan for extracting mapped circuit:
  def __init__(self, args,pddl_instance, plan):

    assert args.model == "local_initial" # TODO: handle this one in circuit_extraction_local.py?

    self.number_of_swaps = 0

    self.extract(args,pddl_instance,plan)
    self.mapped_circuit_to_string(pddl_instance)
    mapped_circuit = QuantumCircuit.from_qasm_str(self.mapped_circuit_string)

    # writing circuit out if specified:
    if (args.circuit_out != None):
      QuantumCircuit.qasm(mapped_circuit,filename=args.circuit_out)
    
    #print(self.mapped_circuit_string)
    if (args.verbose > 2):
      print(self.mapped_circuit_string)
    if (args.verbose > 0):
      print(mapped_circuit)
    print("Number of additional swaps: ", self.number_of_swaps)