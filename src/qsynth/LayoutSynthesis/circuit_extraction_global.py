# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from qsynth.LayoutSynthesis.mapped_unmapped import MappedUnmappedCircuit
from qsynth.LayoutSynthesis.circuit_utils import gate_get_qubit


class CircuitExtractionGlobal:

    # retrieve the gate names from the logical circuit
    def construct_gate_idx_map(self, args, pddl_instance):
        self.gateidx = dict()
        circuit = pddl_instance.logical_circuit
        gates_used = set()
        for d, layer in enumerate(pddl_instance.input_dag.layers()):
            subdag = layer["graph"]
            for node in subdag.op_nodes():
                if node.op.name == "cx":
                    l1 = node.qargs[0]._index
                    l2 = node.qargs[1]._index
                    # search for this gate in the circuit, but not in gates_used
                    idx = -1
                    for i in range(0, len(circuit)):
                        if (
                            i not in gates_used
                            and circuit[i].operation.name == "cx"
                            and gate_get_qubit(circuit[i], 0) == l1
                            and gate_get_qubit(circuit[i], 1) == l2
                        ):
                            idx = i
                            break  # found the gate at idx
                    if idx == -1:
                        print(f"Error: Node {node} not found")
                        exit(-1)
                    gates_used.add(idx)  # this CX gate should not be found again
                    if args.verbose > 2:
                        print(f"Identified CX-gate at depth ({l1},{l2},{d+1}) -> {idx}")
                    self.gateidx[(l1, l2, d + 1)] = idx

    def identify_first_depth(self, plan):
        cur_depth = -1
        for step in plan:
            if step[0] == "apply_cnot":
                cur_depth = step[5]
                break
        if cur_depth == -1:
            print("Error: Initial depth could not be identified from the plan")
            exit(-1)
        self.cur_depth = int(cur_depth[1:])

    def extract(self, plan):
        # Translate plan into physical circuit
        for step in plan:
            if "map_initial" == step[0]:
                logical = int(step[1][1:])
                physical = int(step[2][1:])
                self.map_unmap.map_initial(logical, physical)
            elif "move_depth" == step[0]:
                self.cur_depth = int(step[2][1:])
            elif "apply_cnot" == step[0]:
                # we only need to remember the physical qubits the cnot/swap is applied:
                (_, l1, l2, p1, p2, _) = step
                l1, l2, p1, p2 = int(l1[1:]), int(l2[1:]), int(p1[1:]), int(p2[1:])
                gate = self.gateidx[(l1, l2, self.cur_depth)]
                self.map_unmap.apply_cnot(l1, l2, p1, p2, gate)
            else:
                assert "swap" in step[0]
                l1 = None
                l2 = None
                if step[0] == "swap":
                    (_, l1, l2, p1, p2) = step
                    l1, l2, p1, p2 = int(l1[1:]), int(l2[1:]), int(p1[1:]), int(p2[1:])
                elif step[0] == "swap_ancillary1":
                    (
                        _,
                        l1,
                        p1,
                        p2,
                    ) = step
                    l1, p1, p2 = int(l1[1:]), int(p1[1:]), int(p2[1:])
                elif step[0] == "swap_ancillary2":
                    (
                        _,
                        l2,
                        p1,
                        p2,
                    ) = step
                    l2, p1, p2 = int(l2[1:]), int(p1[1:]), int(p2[1:])
                self.map_unmap.apply_swap(l1, l2, p1, p2)

    # uses the plan for extracting mapped circuit:
    def __init__(self, args, pddl_instance, plan):

        self.construct_gate_idx_map(args, pddl_instance)
        self.identify_first_depth(plan)
        self.map_unmap = MappedUnmappedCircuit(
            args,
            pddl_instance.logical_circuit,
            pddl_instance.num_physical_qubits,
            pddl_instance.coupling_map,
        )
        self.extract(plan)
        mapped_circuit = self.map_unmap.get_mapped_circuit()
        mapped_circuit = self.map_unmap.get_measured_circuit()

        if args.verbose > 0:
            if args.verbose > 2:
                print(QuantumCircuit.qasm(self.map_unmap.mapped_circuit))
            print("mapped circuit:")
            print(mapped_circuit)

        # we print this even in silent mode, since this is the main result
        report_h = (
            f"({self.map_unmap.number_of_h} extra H-gates)"
            if self.map_unmap.number_of_h > 0
            else ""
        )
        if args.verbose > -1:
            print(
                "Number of additional swaps:", self.map_unmap.number_of_swaps, report_h
            )
