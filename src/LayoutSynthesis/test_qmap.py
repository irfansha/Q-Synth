from mqt import qmap
from mqt.qmap.subarchitectures import SubarchitectureOrder
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import FakeTokyo
from qiskit.providers.fake_provider import FakeTenerife
from qiskit.providers.fake_provider import FakeMelbourne
import argparse
import textwrap


# Main:
if __name__ == '__main__':
    text = "A test script for qmap"
    parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--circuit_in", help="input circuit file", default = "Benchmarks/Testing/toggle.qasm")
    parser.add_argument("--provider", help=textwrap.dedent('''
                               provider name:
                               tenerife = FakeTenerife/IBM QX2, 5 qubit
                               melborne = FakeMelbourne, 14 qubit
                               tokyo = FakeTokyo, 20 qubit (default)'''),default = "tokyo")
    parser.add_argument("--model", help="[heuristic/exact]default=heuristic", default = "heuristic")
    parser.add_argument("--subsets", type=int , help="[0/1]default=0", default = 0)
    parser.add_argument("--bidirectional_coupling", type=int, help="[0/1] change coupling to bidirectional, default 0" ,default = 0)
    

    args = parser.parse_args()

    if (args.provider == "tokyo"):
      backend = FakeTokyo()
    elif(args.provider == "tenerife"):
      backend = FakeTenerife()
    elif(args.provider == "melbourne"):
      backend = FakeMelbourne()

    # load your own QASM file
    circuit_file = args.circuit_in
    #print(circuit_file)

    coupling_map = []

    # always bidirectional:
    extra_connections = []
  
    for [x1,x2] in backend.configuration().coupling_map:
      # first appending the existing connections:
      coupling_map.append([x1,x2])
      if [x2,x1] not in backend.configuration().coupling_map:
        if [x2,x1] not in extra_connections:
          extra_connections.append([x2,x1])

    if (args.bidirectional_coupling == 1):
      # adding the extra connections:
      coupling_map.extend(extra_connections)
      backend.configuration().coupling_map = coupling_map
      print(backend.configuration().coupling_map)


    if (args.subsets == 0):
      mapped_circuit, results = qmap.compile(circuit_file,backend,pre_mapping_optimizations=False,post_mapping_optimizations=False,method=args.model,encoding="commander",commander_grouping="fixed3",use_subsets=False)
      print(results)
    else:    
      # computing number of input qubits:
      input_circuit = QuantumCircuit()
      input_circuit_qiskit = input_circuit.from_qasm_file(args.circuit_in)
      nqubits = len(input_circuit_qiskit.qubits)
    
      ibm_melbourne = SubarchitectureOrder.from_coupling_map(backend.configuration().coupling_map)
    
      opt_cand = ibm_melbourne.optimal_candidates(nqubits)
    
      for i, cand in enumerate(opt_cand):
        print(i, cand.nodes())
        mapped_circuit, results = qmap.compile(circuit_file,backend,pre_mapping_optimizations=False,post_mapping_optimizations=False,method=args.model,encoding="commander",commander_grouping="fixed3",use_subsets=False,subgraph=set(cand.nodes()))
        print(results)


