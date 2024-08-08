import argparse
from qiskit import QuantumCircuit
from architecture import platform

from pytket.qasm import circuit_from_qasm
from pytket.architecture import Architecture
from pytket.mapping import MappingManager
from pytket.mapping import LexiLabellingMethod, LexiRouteRoutingMethod
#from pytket.passes import RemoveRedundancies, CliffordSimp
from pytket.circuit import display
#from pytket.passes import FullPeepholeOptimise, DefaultMappingPass, SynthesiseTket, RebaseTket
from pytket.extensions.qiskit import qiskit_to_tk, tk_to_qiskit

# Main:
if __name__ == '__main__':
    text = "A test script for tket"
    parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--circuit_in", help="input circuit file", default = "Benchmarks/Testing/toggle.qasm")
    parser.add_argument("--provider", help="various providers, sycamore(default)",default = "sycamore")
    parser.add_argument("--lookahead_depth",type=int, help="lookahead depth for LexiRouteROutingMethod, 10(default)",default = 10)

    args = parser.parse_args()


    # load your own QASM file
    circuit_file = QuantumCircuit.from_qasm_file(args.circuit_in)
    #print(circuit_file)
    circuit_file.measure_all()
    circ = qiskit_to_tk(circuit_file)


    file_name = args.circuit_in.split("/")[-1]

    _,coupling_map,_,_,_,_ = platform(args.provider, 1, -1)

    arch = Architecture(coupling_map)

    lexi_label = LexiLabellingMethod()
    lexi_route = LexiRouteRoutingMethod(10)

    mapping_manager = MappingManager(arch)

    mapping_manager.route_circuit(circ, [lexi_label, lexi_route])
    mapped_circ = tk_to_qiskit(circ)
    #print(mapped_circ)

    if ('swap' in mapped_circ.count_ops()):
      #print("Original operators:",circuit_file.count_ops())
      #print("Final operators:",mapped_circ.count_ops())
      additional_cnots = mapped_circ.count_ops()['cx'] - circuit_file.count_ops()['cx']
      print('Additional swaps/bridges :', mapped_circ.count_ops()['swap'] + float(additional_cnots)/3)

    else:
      print('Additional swaps: 0')
    '''
    #CliffordSimp().apply(c)
    #RemoveRedundancies().apply(c)
    PlacementPass(GraphPlacement(arch)).apply(c)
    CustomRoutingPass(arch, [LexiLabellingMethod(), LexiRouteRoutingMethod(15)]).apply(c)

    print(cnot_count(tk_to_qiskit(c)))
    '''