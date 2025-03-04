# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from src.LayoutSynthesis.mapped_unmapped import MappedUnmappedCircuit


class CircuitExtractionLifted:

    def extract(self, plan, relaxed):

        for step in plan:
            if "apply_cnot" in step[0]:
                if relaxed == 0:  # strict dependencies
                    # we extract the arguments and apply the initial mapping(s)
                    if step[0] == "apply_cnot_input_input":
                        (_, l1, l2, p1, p2, gate_idx) = step
                    elif step[0] == "apply_cnot_input_gate":
                        (_, l1, l2, p1, p2, gate_idx, _) = step
                    elif step[0] == "apply_cnot_gate_input":
                        (_, l1, l2, p1, p2, gate_idx, _) = step
                    else:
                        (_, l1, l2, p1, p2, gate_idx, _, _) = step
                else:  # relaxed dependencies
                    # we extract the arguments and apply the initial mapping(s)
                    (_, l1, l2, p1, p2, gate_idx) = step
                self.map_unmap.apply_cnot(
                    int(l1[1:]),
                    int(l2[1:]),
                    int(p1[1:]),
                    int(p2[1:]),
                    int(gate_idx[1:]),
                )
            elif "swap" in step[0]:
                # we extract the arguments and update the mapping of logical to physical bits
                l1 = None
                l2 = None
                if step[0] in ("swap11", "swap"):
                    (_, l1, l2, p1, p2) = step
                elif step[0] == "swap10":
                    (_, l1, p1, p2) = step
                elif step[0] == "swap01":
                    (_, l2, p1, p2) = step
                to_int = lambda s: None if s == None else int(s[1:])
                (l1, l2, p1, p2) = map(to_int, (l1, l2, p1, p2))
                self.map_unmap.apply_swap(l1, l2, p1, p2)
            elif step[0] == "map_initial":
                l1 = int(step[1][1:])
                p1 = int(step[2][1:])
                self.map_unmap.map_initial(l1, p1)
            elif step[0] == "bridge":
                l1 = int(step[1][1:])
                l2 = int(step[2][1:])
                p1 = int(step[3][1:])
                p2 = int(step[4][1:])
                p3 = int(step[5][1:])
                gate = int(step[6][1:])
                self.map_unmap.apply_bridge(l1, l2, p1, p2, p3, gate)
            elif step[0] != "dummy":
                print(f"Unexpected error: action {step[0]} in plan not understood")
                exit(-1)

    # uses the plan for extracting mapped circuit:
    def __init__(self, args, pddl_instance, plan):

        assert args.model == "lifted"

        self.map_unmap = MappedUnmappedCircuit(
            args,
            pddl_instance.logical_circuit,
            pddl_instance.num_physical_qubits,
            pddl_instance.coupling_map,
        )

        self.extract(plan, args.relaxed)
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
        report_b = (
            f"({self.map_unmap.number_bridges} bridges)"
            if self.map_unmap.number_bridges > 0
            else ""
        )
        print(
            "Number of additional swaps:",
            self.map_unmap.number_of_swaps,
            report_b,
            report_h,
        )
