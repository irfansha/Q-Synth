# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus, 2023

from qiskit import QuantumCircuit
from src.LayoutSynthesis.mapped_unmapped import MappedUnmappedCircuit


class CircuitExtractionLocal:

    def extract(self, plan):
        for step_index in range(len(plan)):
            step = plan[step_index]
            if step[0] == "swap":
                (_, l1, l2, p1, p2) = step
                self.map_unmap.apply_swap(
                    int(l1[1:]), int(l2[1:]), int(p1[1:]), int(p2[1:])
                )
            elif step[0] == "swap-ancillary1":
                (_, l1, p1, p2) = step
                self.map_unmap.apply_swap(int(l1[1:]), None, int(p1[1:]), int(p2[1:]))
            elif step[0] == "swap-ancillary2":
                (_, l2, p1, p2) = step
                self.map_unmap.apply_swap(None, int(l2[1:]), int(p1[1:]), int(p2[1:]))
            elif "cnot" in step[0]:
                name1, name2, layer_index = step[0].split("_")
                assert name1 == "apply"
                assert name2 == "cnot"
                gate_index = int(layer_index[1:])
                l1 = self.circuit[gate_index].qubits[0]._index
                l2 = self.circuit[gate_index].qubits[1]._index
                p1 = int(step[1][1:])
                p2 = int(step[2][1:])
                self.map_unmap.apply_cnot(l1, l2, p1, p2, gate_index)
            elif step[0] == "map_initial":
                l1 = int(step[1][1:])
                p1 = int(step[2][1:])
                self.map_unmap.map_initial(l1, p1)
            else:
                print(f"Unexpected error: action {step[0]} in plan not understood")
                exit(-1)

    # uses the plan for extracting mapped circuit:
    def __init__(self, args, pddl_instance, plan):

        assert "local" in args.model or "sat" in args.model

        self.circuit = pddl_instance.logical_circuit

        self.map_unmap = MappedUnmappedCircuit(
            args,
            self.circuit,
            pddl_instance.num_physical_qubits,
            pddl_instance.coupling_map,
        )

        # adding initial map for sat encoding separately:
        if args.model == "sat":
            for lqubit, pqubit in pddl_instance.logical_physical_map.items():
                self.map_unmap.map_initial(lqubit, pqubit)

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
        print("Number of additional swaps:", self.map_unmap.number_of_swaps, report_h)
