# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from mapped_unmapped import MappedUnmappedCircuit

class CircuitExtractionLifted:

  def extract(self, plan):

    for step in plan:
      if "apply_cnot" in step[0]:
        # we extract the arguments and apply the initial mapping(s)
        if step[0] == "apply_cnot_input_input":
          (_, l1, l2, p1, p2, gate_idx) = step
        elif step[0] == "apply_cnot_input_gate":
          (_, l1, l2, p1, p2, gate_idx, _) = step
        elif step[0] == "apply_cnot_gate_input":
          (_, l1, l2, p1, p2, gate_idx, _) = step
        else: 
          (_, l1, l2, p1, p2, gate_idx, _, _) = step

        self.map_unmap.apply_cnot(int(l1[1:]),int(l2[1:]),int(p1[1:]),int(p2[1:]),int(gate_idx[1:]))
      elif "swap" in step[0]:
        # we extract the arguments and update the mapping of logical to physical bits
          l1 = None
          l2 = None
          if step[0] in ("swap11","swap"):
            (_, l1, l2, p1, p2) = step
          elif step[0]=="swap10":
            (_, l1, p1, p2) = step
          elif step[0]=="swap01":
            (_, l2, p1, p2) = step
          to_int = lambda s : None if s==None else int(s[1:])
          (l1,l2,p1,p2) = map(to_int, (l1,l2,p1,p2))
          self.map_unmap.apply_swap(l1, l2, p1, p2)
      else:
        assert step[0]=="map_initial"
        l1 = int(step[1][1:])
        p1 = int(step[2][1:])
        self.map_unmap.map_initial(l1, p1)

  # uses the plan for extracting mapped circuit:
  def __init__(self, args, pddl_instance, plan):

    assert("lifted" in args.model)

    self.map_unmap = MappedUnmappedCircuit(args, pddl_instance.logical_circuit, pddl_instance.num_physical_qubits)

    self.extract(plan)
    mapped_circuit = self.map_unmap.get_mapped_circuit()
    mapped_circuit = self.map_unmap.get_measured_circuit()
    
    # writing circuit out if specified:
    if (args.circuit_out != None):
      QuantumCircuit.qasm(mapped_circuit,filename=args.circuit_out)

    if (args.verbose > 0):
      if (args.verbose > 2):
        print(QuantumCircuit.qasm(self.map_unmap.mapped_circuit))
      print("mapped circuit:")
      print(mapped_circuit)

    print("Number of additional swaps:", self.map_unmap.number_of_swaps)
