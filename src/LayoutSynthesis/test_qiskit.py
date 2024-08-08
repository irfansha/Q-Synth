from qiskit import transpile
from qiskit import QuantumCircuit
from qiskit.tools.visualization import circuit_drawer
import argparse
import textwrap
from architecture import platform
import sys

from qiskit.transpiler import PassManager, CouplingMap
from qiskit.transpiler.passes import SabreLayout


# Main:
if __name__ == '__main__':
    text = "A test script for qiskit"
    parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--circuit_in", help="input circuit file", default = "Benchmarks/Testing/toggle.qasm")
    parser.add_argument("--circuit_out", help="input circuit file", default = "intermediate_files/out.qasm")
    parser.add_argument("--provider", help="various providers, sycamore(default)",default = "sycamore")
    parser.add_argument("--seed", type=int, help="seed for sabrelayout default 0" ,default = 0)
    parser.add_argument("--seed_upperbound", type=int, help="seeds to try <= upperbound for sabrelayout default 10" ,default = 10)
    parser.add_argument("--layout", help="Sabre/Lookahead" ,default = "Sabre")

    args = parser.parse_args()


    # load your own QASM file
    circuit_file = QuantumCircuit.from_qasm_file(args.circuit_in)
    #print(circuit_file)
    circuit_file.measure_all()

    file_name = args.circuit_in.split("/")[-1]

    _,coupling_map,_,_,_,_ = platform(args.provider, 1, -1)
    if (args.layout == "Sabre"):
      min_swaps = sys.maxsize
      for i in range(args.seed_upperbound):
        #print(backend.configuration().coupling_map)
        s_swap_pass = SabreLayout(CouplingMap(coupling_map),swap_trials=1,layout_trials=1,seed=args.seed)
        pm = PassManager(s_swap_pass)
        qc_basis = pm.run(circuit_file)
        if ('swap' in qc_basis.count_ops()):
          if (min_swaps > qc_basis.count_ops()['swap']):
            min_swaps = qc_basis.count_ops()['swap']
        else:
          min_swaps = 0
          break
      print("Iterations: ", args.seed_upperbound, "Minimum additonal swaps: ",min_swaps)
    else:
      assert(args.layout == "Lookahead")
      qc_basis = transpile(circuit_file, coupling_map=coupling_map) 
      if ('swap' in qc_basis.count_ops()):
        print('Additional swaps:', qc_basis.count_ops()['swap'])
      else:
        print('Additional swaps: 0')

    circuit_qasm = QuantumCircuit.qasm(qc_basis)
    with open(args.circuit_out, 'w') as f:
      f.write(circuit_qasm)