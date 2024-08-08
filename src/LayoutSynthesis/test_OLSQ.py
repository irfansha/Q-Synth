from olsq import OLSQ
from qiskit.providers.fake_provider import FakeTokyo
from qiskit.providers.fake_provider import FakeTenerife
from qiskit.providers.fake_provider import FakeMelbourne
from olsq.device import qcdevice
from qiskit import QuantumCircuit
import argparse
import textwrap

# Main:
if __name__ == '__main__':
    text = "A test script for OSLQ"
    parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--circuit_in", help="input circuit file", default = "Benchmarks/Testing/toggle.qasm")
    parser.add_argument("--provider", help=textwrap.dedent('''
                               provider name:
                               tenerife = FakeTenerife/IBM QX2, 5 qubit
                               melborne = FakeMelbourne, 14 qubit
                               tokyo = FakeTokyo, 20 qubit (default)'''),default = "tokyo")
    parser.add_argument("--model", help="[normal/transition(default)]", default = "transition")
    parser.add_argument("--bidirectional_coupling", type=int, help="[0/1] change coupling to bidirectional, default 0" ,default = 0)
    args = parser.parse_args()

    # initiate olsq with depth as objective, in normal mode
    #lsqc_solver = OLSQ("swap", "normal")
    lsqc_solver = OLSQ("swap", args.model)

    if (args.provider == "tokyo"):
      arch = FakeTokyo()
    elif(args.provider == "tenerife"):
      arch = FakeTenerife()
    elif(args.provider == "melbourne"):
      arch = FakeMelbourne()


    coupling_map = []

    # always bidirectional:
    extra_connections = []
  
    for [x1,x2] in arch.configuration().coupling_map:
      # first appending the existing connections:
      coupling_map.append([x1,x2])
      if [x2,x1] not in arch.configuration().coupling_map:
        if [x2,x1] not in extra_connections:
          extra_connections.append([x2,x1])

    if (args.bidirectional_coupling == 1):
      # adding the extra connections:
      coupling_map.extend(extra_connections)

      #print(coupling_map)

    # directly construct a device from properties needed by olsq
    lsqc_solver.setdevice( qcdevice(name=arch.configuration().backend_name, nqubits=arch.configuration().n_qubits, 
        connection=coupling_map, swap_duration=3) )


    # load your own QASM file
    circuit_file = open(args.circuit_in, "r").read()

    lsqc_solver.setprogram(circuit_file)

    # solve LSQC
    #result = lsqc_solver.solve("IR")
    result = lsqc_solver.solve()

    print("mapped physical qubits:", result[1])
    print(result)

    final_circuit = QuantumCircuit.from_qasm_str(result[0])

    print(final_circuit)