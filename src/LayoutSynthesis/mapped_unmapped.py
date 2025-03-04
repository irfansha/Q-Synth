# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

from qiskit import QuantumCircuit
from src.LayoutSynthesis.circuit_utils import (
    gate_get_qubit,
    gate_set_qubit,
    all_cx_gates,
)


class MappedUnmappedCircuit:

    def init_data_structures(self):

        # compute cnot list
        self.cx_gates = all_cx_gates(self.lcircuit)

        # Compute unary gate list per qubit
        self.unary_gates = {}
        for bit in range(self.num_lqubits):
            self.unary_gates[bit] = []
        for gate_idx in range(len(self.lcircuit)):
            gate = self.lcircuit[gate_idx]
            if len(gate.qubits) == 1:
                qubit = gate_get_qubit(self.lcircuit[gate_idx], 0)
                self.unary_gates[qubit].append(gate_idx)

        # initialize map from logical to physical qubits:
        self.logical_physical_map = {}

        # initialize the reverse initial mapping from physical to logical qubits
        self.reverse_init_mapping = {}

        # initialize map from not mapped physical qubits to their origins
        # this is necessary to keep track of swaps with ancillary qubits
        self.track_ancillary = {}
        for pqubit in range(self.num_pqubits):
            self.track_ancillary[pqubit] = pqubit

        # Initialize the mapped circuit on phyisical qubits
        self.mapped_circuit = QuantumCircuit(self.num_pqubits, self.num_pqubits)

    # execute plan action map_initial
    def map_initial(self, lqubit, pqubit):
        self.logical_physical_map[lqubit] = pqubit
        # note: the _original_ physical qubit is initially mapped to lqubit
        original = self.track_ancillary[pqubit]
        self.reverse_init_mapping[original] = lqubit
        del self.track_ancillary[pqubit]
        if self.verbose > 2:
            print(f"...initially mapping l{lqubit} to p{original} (now p{pqubit})")

    # helper function: swap (l1,p1) to (l2,p2)
    def swap_half(self, lqubit1, lqubit2, pqubit1, pqubit2):
        if lqubit2 == None:  #
            self.track_ancillary[pqubit1] = self.track_ancillary[pqubit2]
            del self.track_ancillary[pqubit2]
            if self.verbose > 2:
                print(
                    f"...ancillary p{pqubit1} came from p{self.track_ancillary[pqubit1]}"
                )
        if lqubit1 != None:
            self.logical_physical_map[lqubit1] = pqubit2

    # Apply a swap on the physical qubits.
    # One of the logical qubits may be None (ancillary swap)
    def apply_swap(self, lqubit1, lqubit2, pqubit1, pqubit2):
        self.number_of_swaps += 1
        if self.verbose > 2:
            print(
                f"Apply swap #{self.number_of_swaps} to "
                f"(p{pqubit1}, p{pqubit2}), corresponding to (l{lqubit1}, l{lqubit2})"
            )

        # we add a swap gate to the circuit:
        if [pqubit1, pqubit2] in self.coupling_map or [
            pqubit2,
            pqubit1,
        ] in self.coupling_map:
            self.mapped_circuit.swap(pqubit1, pqubit2)
        else:
            print("Error: try to SWAP non-connected qubits")
            exit(-1)

        # currently, we don not handle a swap on two ancillary qubits
        assert not (lqubit1 == None and lqubit2 == None)
        self.swap_half(lqubit1, lqubit2, pqubit1, pqubit2)
        self.swap_half(lqubit2, lqubit1, pqubit2, pqubit1)

    # Apply all unary gates on lqubit before gate_idx to the mapped circuit
    def apply_unary_gates(self, lqubit, pqubit, gate_idx):
        gates = self.unary_gates[lqubit]  # this is not a copy (!)
        while len(gates) > 0:
            if gates[0] > gate_idx:
                break  # assuming gates is ordered, we have processed all unary gates before g
            gate = gates.pop(
                0
            )  # this removes gates[0] also from self.unary_gates[lqubit]
            newgate = gate_set_qubit(self.lcircuit[gate], pqubit, self.num_pqubits)
            self.mapped_circuit.append(newgate)
            if self.verbose > 2:
                print(
                    f"...applying unary gate #{gate_idx} ({newgate.operation.name}) to l{lqubit} on p{pqubit}"
                )

    # apply CNOT with gate_idx to the logical/physical qubits
    # also apply all unary gates until this index on these qubits
    def apply_cnot(self, lqubit1, lqubit2, pqubit1, pqubit2, gate_idx):
        if self.verbose > 2:
            print(
                f"Apply CNOT #{gate_idx} to "
                f"(l{lqubit1}, l{lqubit2}), mapped to (p{pqubit1}, p{pqubit2})"
            )

        if lqubit1 not in self.logical_physical_map:
            self.map_initial(lqubit1, pqubit1)
        if lqubit2 not in self.logical_physical_map:
            self.map_initial(lqubit2, pqubit2)
        assert self.logical_physical_map[lqubit1] == pqubit1
        assert self.logical_physical_map[lqubit2] == pqubit2

        # we apply the unary gates before this cnot
        self.apply_unary_gates(lqubit1, pqubit1, gate_idx)
        self.apply_unary_gates(lqubit2, pqubit2, gate_idx)

        # we add the cnot gate to the circuit
        if [pqubit1, pqubit2] in self.coupling_map:
            self.mapped_circuit.cx(pqubit1, pqubit2)
        elif [pqubit2, pqubit1] in self.coupling_map:
            if self.args.bidirectional == 1:
                self.mapped_circuit.cx(pqubit1, pqubit2)
            elif self.args.bidirectional == 2:  # Use H-swap-H
                self.mapped_circuit.h(pqubit1)
                self.mapped_circuit.h(pqubit2)
                self.mapped_circuit.cx(pqubit2, pqubit1)
                self.mapped_circuit.h(pqubit1)
                self.mapped_circuit.h(pqubit2)
                self.number_of_h += 4
                if self.verbose > 2:
                    print("...applied H-CNOT-H gates")
            else:
                print("Error: tried to connect CNOT gate in opposite direction")
                exit(-1)
        else:
            print("Error: tried to CNOT gate non-connected qubits")
            print(pqubit1, pqubit2, self.coupling_map)
            exit(-1)

    def apply_bridge(self, lqubit1, lqubit2, pqubit1, pqubit2, pqubit3, gate_idx):
        self.number_bridges += 1
        if self.verbose > 2:
            print(f"Apply Bridge for CNOT #{gate_idx} on (l{lqubit1}, l{lqubit2})")
            print(f"..CNOT p{pqubit1}, p{pqubit2}")
            print(f"..CNOT p{pqubit2}, p{pqubit3}")
            print(f"..CNOT p{pqubit1}, p{pqubit2}")
            print(f"..CNOT p{pqubit2}, p{pqubit3}")

        # For now, assuming that the logical qubits have been mapped already
        assert self.logical_physical_map[lqubit1] == pqubit1
        assert self.logical_physical_map[lqubit2] == pqubit3

        # we apply the unary gates before this cnot
        self.apply_unary_gates(lqubit1, pqubit1, gate_idx)
        self.apply_unary_gates(lqubit2, pqubit3, gate_idx)

        # we add the cnot gate to the circuit
        p12OK = [pqubit1, pqubit2] in self.coupling_map or (
            self.args.bidirectional == 1 and [pqubit2, pqubit1] in self.coupling_map
        )
        p23OK = [pqubit2, pqubit3] in self.coupling_map or (
            self.args.bidirectional == 1 and [pqubit3, pqubit2] in self.coupling_map
        )
        if p12OK and p23OK:
            self.mapped_circuit.cx(pqubit1, pqubit2)
            self.mapped_circuit.cx(pqubit2, pqubit3)
            self.mapped_circuit.cx(pqubit1, pqubit2)
            self.mapped_circuit.cx(pqubit2, pqubit3)
        else:
            print("Error: tried to BRIDGE through non-connected qubits")
            print(
                f"{pqubit1}-{pqubit2}-{pqubit3} is not a bridge in {self.coupling_map} (bidirectional={self.args.bidirectional})"
            )
            exit(-1)

    #
    def find_free_pqubit(self, lqubit):
        for pqubit in range(self.num_pqubits):
            if pqubit not in self.logical_physical_map.values():
                self.map_initial(lqubit, pqubit)
                return pqubit
        assert False  # no free physical qubit found

    # Finish the mapped circuit and return it
    def get_mapped_circuit(self):
        max_gate_idx = len(self.lcircuit) + 1
        for lqubit in range(self.num_lqubits):
            if lqubit in self.logical_physical_map:
                pqubit = self.logical_physical_map[lqubit]
            else:
                pqubit = self.find_free_pqubit(lqubit)
                if self.verbose > 2:
                    print(f"......mapped dangling l{lqubit} onto p{pqubit}")
            self.apply_unary_gates(lqubit, pqubit, max_gate_idx)
        return self.mapped_circuit

    # Return a copy of the mapped circuit including measurements
    # Should typically be called AFTER calling get_mapped_circuit
    def get_measured_circuit(self):
        circuit = self.mapped_circuit.copy()
        circuit.barrier()
        for logical, physical in self.logical_physical_map.items():
            circuit.measure([physical], [logical])
        return circuit

    # Compute and return the "unmapped" circuit without swaps
    # Should typically be called AFTER calling get_mapped_circuit
    # This can be used for validation
    def get_unmapped_circuit(self):
        unmapped_circuit = QuantumCircuit(
            self.num_lqubits, self.num_lqubits
        )  # or 0 classical?
        for gate in self.mapped_circuit:
            if gate.operation.name == "swap":
                q1 = gate_get_qubit(gate, 0)
                q2 = gate_get_qubit(gate, 1)
                # if presented we extract the earlier swapped value:
                if q1 not in self.reverse_init_mapping:
                    # q1 is an ancillary qubit:
                    assert q2 in self.reverse_init_mapping
                    self.reverse_init_mapping[q1] = self.reverse_init_mapping[q2]
                    del self.reverse_init_mapping[q2]
                elif q2 not in self.reverse_init_mapping:
                    self.reverse_init_mapping[q2] = self.reverse_init_mapping[q1]
                    del self.reverse_init_mapping[q1]
                else:  # swap
                    tmp = self.reverse_init_mapping[q1]
                    self.reverse_init_mapping[q1] = self.reverse_init_mapping[q2]
                    self.reverse_init_mapping[q2] = tmp

            elif gate.operation.name == "cx":
                q1 = gate_get_qubit(gate, 0)
                q2 = gate_get_qubit(gate, 1)
                # we update the qubit in the gate:
                newq1 = self.reverse_init_mapping[q1]
                newq2 = self.reverse_init_mapping[q2]
                unmapped_circuit.cx(newq1, newq2)
            else:
                # we update the qubit in the gate:
                assert len(gate.qubits) == 1
                q = gate_get_qubit(gate, 0)
                newq = self.reverse_init_mapping[q]
                newgate = gate_set_qubit(gate, newq, self.num_lqubits)
                unmapped_circuit.append(newgate)
        return unmapped_circuit

    def __init__(self, args, logical_circuit, num_physical_qubits, coupling_map):

        self.args = args
        self.lcircuit = logical_circuit
        self.num_pqubits = num_physical_qubits
        self.num_lqubits = len(self.lcircuit.qubits)
        self.number_of_swaps = 0
        self.number_bridges = 0
        self.number_of_h = 0
        self.verbose = args.verbose
        self.coupling_map = coupling_map
        self.init_data_structures()
