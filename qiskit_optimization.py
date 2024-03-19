# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

'''
Takes a mapped circuit and a coupling graph to use qiskit optimization
We simply map it again with given optimization level 
'''

from qiskit import transpile


def qiskit_optimization(original_circuit, mapped_circuit, coupling_map, initial_map, level, verbose):

    if verbose > 0:
      print("Qiskit Optimization:")

    used_gates = set()
    for gate in mapped_circuit:
      used_gates.add(gate.operation.name)
    if verbose > 2:
      print(f"Qiskit optimization level {level} using basic gates: {used_gates}")
      print(f"Coupling_map: {coupling_map}")

    opt_circuit = transpile(mapped_circuit, 
                            basis_gates=used_gates, 
                            coupling_map=coupling_map, 
                            initial_layout=initial_map, 
                            optimization_level=level)

    if verbose > 0:
      print(opt_circuit)

    if verbose > 2:
      print('Original circuit no of operators:', list(original_circuit.count_ops().items()))
      print('Mapped circuit no of operators:  ', list(mapped_circuit.count_ops().items()))
      print('Optimized no of operators:       ', list(opt_circuit.count_ops().items()))

    if verbose > 0:
      # we report if there is any change:
      if (mapped_circuit.depth() != opt_circuit.depth()):
        print('Mapped depth: ', mapped_circuit.depth(), '. Optimized Depth: ', opt_circuit.depth())
      if (opt_circuit.count_ops()['cx'] != mapped_circuit.count_ops()['cx']):
        print(f'Change in CX gates: {mapped_circuit.count_ops()["cx"]}->{opt_circuit.count_ops()["cx"]}')
      if ("swap" in mapped_circuit.count_ops()):
        if (opt_circuit.count_ops()['swap'] != mapped_circuit.count_ops()['swap']):
          print(f'Change in SWAP gates: {mapped_circuit.count_ops()["swap"]}->{opt_circuit.count_ops()["swap"]}')

    return opt_circuit