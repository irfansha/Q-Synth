# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit.converters import circuit_to_dag
from mqt import qcec

class TestingMappedCircuitNew:

    def compare_layers(self):
        original_dag = circuit_to_dag(self.input_circuit)
        unmapped_dag = circuit_to_dag(self.unmapped_circuit)
        original_layers = list(original_dag.layers())
        unmapped_layers = list(unmapped_dag.layers())
        if len(unmapped_layers) != len(original_layers):
           print(f"Error: number of layers is different")
           exit(-1)
        # first mapped and swapless dag:
        for i in range(len(original_layers)):
            if (self.args.verbose  > 2):
              print("Testing operations in layer number:", i+1)

            # extract the relevant information (name + qubits) from the DAG nodes
            get_info = lambda node: (node.name, tuple(map(lambda q: q.index, node.qargs)))
            original_gates = list(map(get_info, original_layers[i]['graph'].op_nodes()))
            unmapped_gates = list(map(get_info, unmapped_layers[i]['graph'].op_nodes()))
               
            if len(original_gates) != len(unmapped_gates):
               print(f"Error: number of gates in layer {i} is different")
               exit(1)
            
            # asserting all gates in the sorted layers are same:
            for gate in original_gates:
              if self.args.verbose > 2:
                print(f"Checking gate {gate[0]} on ({', '.join(map(lambda y: f'q{y}',gate[1]))})")
              if gate in unmapped_gates:
                unmapped_gates.remove(gate)
              else:
                print(f"Error: gate {gate} in layer {i} appears in original but not in unmapped circuit")
                exit(1)

            if self.args.verbose  > 2:
              print("=======================================")

    # Tests the mapped circuit with the original circuit
    # First generates mapped circuit without swaps using remove_swaps function
    # Then generates layers from the circuits, mapped circuit without swaps and orginal circuit using qiskit QuantumCircuit
    # Then compares the layers from the circuits, according to the physical mapping
    def test_mapped_circuit(self):

        # extracting layers using qiskit:
        if (self.args.verbose  > 1):
          print("original circuit:")
          print(self.input_circuit)
          print()
          print("mapped circuit without swaps:")
          print(self.unmapped_circuit)

        self.compare_layers()
        if self.args.verbose > -1:
          print("Assertions complete, mapped circuit has the same layers as the original one")

    def __init__(self, pddl_instance, mapped_unmapped):

      self.args = pddl_instance.args
      self.input_circuit  = pddl_instance.input_circuit      # original circuit, before pre-optimization
      self.mapped_circuit = mapped_unmapped.mapped_circuit

      self.unmapped_circuit = mapped_unmapped.get_unmapped_circuit()
      self.test_mapped_circuit()
