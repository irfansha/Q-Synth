# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag

class TestingMappedCircuit:

    # Input is a list which represents the mapped circuit
    # output is a list representing mapped circuit after removing the swaps:
    def remove_swaps(self):
        # first initialising physical qubits with logical qubit reverse mapping:
        updated_physical_qubits = {}
        for key,val in self.reverse_init_mapping.items():
            updated_physical_qubits["q[" + key[1:] + "]"] = "q[" + val[1:] + "]"
        if (self.args.verbose  > 2):
          print("reverse initial mapping:")
          for (key,value) in updated_physical_qubits.items():
            print(f"{key} -> {value}")

        self.mapped_circuit_without_swaps = []
        for gate in self.mapped_circuit:
            split_gate = gate.strip(";").split(" ")
            #print(split_gate, updated_physical_qubits)
            if (split_gate[0] == "swap"):
                first_qubit,second_qubit = split_gate[1].split(",")
                # if presented we extract the earlier swapped value:
                if (first_qubit not in updated_physical_qubits):
                  # this is because of ancillary qubits:
                  first_value = "ancillary"
                else:
                  first_value = ''.join(updated_physical_qubits[first_qubit])
                # if presented we extract the earlier swapped value:
                if (second_qubit not in updated_physical_qubits):
                   # this is because of ancillary qubits:
                   second_value = "ancillary"
                else:
                  second_value = ''.join(updated_physical_qubits[second_qubit])

                # now we map the updated physical qubits with each other:
                if (second_value != "ancillary"):
                  updated_physical_qubits[first_qubit] = second_value
                if (first_value != "ancillary"):
                  updated_physical_qubits[second_qubit] = first_value
                #print(split_gate, updated_physical_qubits)
            elif(split_gate[0] == "cx"):
                first_qubit,second_qubit = split_gate[1].split(",")
                #print(first_qubit, second_qubit)
                # we update the qubit in the gate:
                first_mapped_qubit = updated_physical_qubits[first_qubit]
                second_mapped_qubit = updated_physical_qubits[second_qubit]
                self.mapped_circuit_without_swaps.append(split_gate[0] + " " + first_mapped_qubit + "," + second_mapped_qubit + ";")
            else:
                # we update the qubit in the gate:
                mapped_qubit = updated_physical_qubits[split_gate[1]]
                self.mapped_circuit_without_swaps.append(split_gate[0] + " " + mapped_qubit + ";")
            #print(self.mapped_circuit_without_swaps[-1])




    def compare_layers(self):
        mapped_swapless_layers = list(self.mapped_circuit_without_swaps_qiskit_dag.layers())
        orginal_layers = list(self.original_dag.layers())
        assert(len(mapped_swapless_layers) == len(orginal_layers))
        num_layers = len(orginal_layers)
        # first mapped and swapless dag:
        for i in range(num_layers):
            if (self.args.verbose  > 1):
              print("Printing operators layer by layer:")
              print("layer number:",i+1)
            assert(len(mapped_swapless_layers[i]['graph'].op_nodes()) == len(orginal_layers[i]['graph'].op_nodes()))
            num_nodes = len(orginal_layers[i]['graph'].op_nodes())
            # asserting nodes are same:
            for j in range(num_nodes):
                cur_mapped_swapless_node = mapped_swapless_layers[i]['graph'].op_nodes()[j]
                if (self.args.verbose  > 1):
                  print(cur_mapped_swapless_node.name, cur_mapped_swapless_node.op.num_qubits, cur_mapped_swapless_node.qargs)
                cur_original_node = orginal_layers[i]['graph'].op_nodes()[j]
                if (self.args.verbose  > 1):
                  print(cur_original_node.name, cur_original_node.op.num_qubits, cur_original_node.qargs)
                # arity must match:
                assert(cur_mapped_swapless_node.op.num_qubits == cur_original_node.op.num_qubits)
                # names must match:
                assert(cur_mapped_swapless_node.name == cur_original_node.name)
                # args must match:
                assert(cur_mapped_swapless_node.qargs == cur_original_node.qargs)
            if (self.args.verbose  > 1):
              print("===========================================")

    # Tests the mapped circuit with the original circuit
    # First generates mapped circuit without swaps using remove_swaps function
    # Then generates layers from the circuits, mapped circuit without swaps and orginal circuit using qiskit QuantumCircuit
    # Then compares the layers from the circuits, according to the physical mapping
    def test_mapped_circuit(self):


        prefix_string = "OPENQASM 2.0;\ninclude \"qelib1.inc\";\n"

        # since we are recovering the original mapping, we use logical qubits not physical:
        prefix_string += "qreg q[" + str(self.num_qubits) +"];\n"
       # for measurement if needed:
        prefix_string += "creg c[" + str(self.num_qubits) +"];\n"

        # first generating a string from the mapped circuit without swaps:
        mapped_circuit_without_swaps_string = str(prefix_string)
        for gate in self.mapped_circuit_without_swaps:
            mapped_circuit_without_swaps_string += gate + "\n"
        if (self.args.verbose  > 2):
            print("mapped circuit without swaps and reconstruction with initial mapping")
            print(mapped_circuit_without_swaps_string)
        # extracting layers using qiskit:
        mapped_circuit_without_swaps_qiskit = QuantumCircuit.from_qasm_str(mapped_circuit_without_swaps_string)
        if (self.args.verbose  > 1):
          print("original circuit, printing using qiskit")
          print(self.input_circuit)
          print()
          print("mapped circuit without swaps and reconstructed initial mapping, printing using qiskit")
          print(mapped_circuit_without_swaps_qiskit)

        # now create layers and check both layers:
        self.mapped_circuit_without_swaps_qiskit_dag = circuit_to_dag(mapped_circuit_without_swaps_qiskit)
        self.compare_layers()

    # initialize:
    def __init__(self, pddl_instance, mapped_circuit, map_extract):

      self.args = pddl_instance.args
      self.num_qubits = pddl_instance.num_lqubits
      self.reverse_init_mapping = map_extract.reverse_init_mapping
      self.input_circuit = pddl_instance.input_circuit
      self.original_dag = pddl_instance.input_dag
      self.mapped_circuit = mapped_circuit

      # # circuit was already printed...
      # if (self.args.verbose  > 1):
      #   print("mapped circuit:")
      #   for line in self.mapped_circuit:
      #      print(line)

      self.remove_swaps()
      self.test_mapped_circuit()
      if self.args.verbose > -1:
        print("Assertions complete, mapped circuit is same as the original one")