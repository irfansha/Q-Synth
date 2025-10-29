from typing import Optional
from qsynth.DepthOptimal.synthesizers.planning.synthesizer import (
    PlanningSynthesizer,
)
from qsynth.DepthOptimal.util.circuits import (
    SynthesizerOutput,
    gate_line_dependency_mapping,
    gate_direct_dependency_mapping,
    LogicalQubit,
    PhysicalQubit,
)
from qiskit import QuantumCircuit
from qsynth.DepthOptimal.util.logger import Logger
from qsynth.DepthOptimal.util.pddl import (
    PDDLInstance,
    PDDLAction,
    PDDLPredicate,
    object_,
    not_,
)
from qsynth.DepthOptimal.synthesizers.planning.solvers import Solver
from qsynth.DepthOptimal.platform import Platform


class LocalClockIncrementalPlanningSynthesizer(PlanningSynthesizer):
    description = "Incremental synthesizer based on planning using local vector clocks for each qubit to keep track of depth."
    is_optimal = False
    uses_conditional_effects = False

    def create_instance(
        self,
        circuit: QuantumCircuit,
        platform: Platform,
        maximum_depth: int | None = None,
    ) -> PDDLInstance:

        if maximum_depth == None:
            raise ValueError(
                "'maximum_depth' should always be given for incremental encodings"
            )

        num_pqubits = platform.qubits
        num_lqubits = circuit.num_qubits
        num_gates = circuit.size()
        # Added one to off-set that the last depth cannot have any gates
        maximum_depth = maximum_depth + 1

        class pqubit(object_):
            pass

        class gate(object_):
            pass

        class depth(object_):
            pass

        class lqubit(gate):
            pass

        p = [pqubit(f"p{i}") for i in range(num_pqubits)]
        l = [lqubit(f"l{i}") for i in range(num_lqubits)]
        g = [gate(f"g{i}") for i in range(num_gates)]
        d = [depth(f"d{i}") for i in range(maximum_depth)]

        @PDDLPredicate()
        def occupied(p: pqubit):
            pass

        @PDDLPredicate()
        def mapped(l: lqubit, p: pqubit):
            pass

        @PDDLPredicate()
        def connected(p1: pqubit, p2: pqubit):
            pass

        @PDDLPredicate()
        def done(g: gate):
            pass

        @PDDLPredicate()
        def clock(p: pqubit, d: depth):
            pass

        @PDDLPredicate()
        def next_depth(d1: depth, d2: depth):
            pass

        @PDDLPredicate()
        def next_swap_depth(d1: depth, d2: depth):
            pass

        @PDDLAction()
        def swap(l1: lqubit, l2: lqubit, p1: pqubit, p2: pqubit, d1: depth, d2: depth):
            preconditions = [
                mapped(l1, p1),
                mapped(l2, p2),
                connected(p1, p2),
                next_swap_depth(d1, d2),
                clock(p1, d1),
                clock(p2, d1),
            ]
            effects = [
                not_(mapped(l1, p1)),
                not_(mapped(l2, p2)),
                mapped(l1, p2),
                mapped(l2, p1),
                not_(clock(p1, d1)),
                not_(clock(p2, d1)),
                clock(p1, d2),
                clock(p2, d2),
            ]
            return preconditions, effects

        @PDDLAction()
        def swap_input(
            l1: lqubit, l2: lqubit, p1: pqubit, p2: pqubit, d1: depth, d2: depth
        ):
            preconditions = [
                mapped(l1, p1),
                not_(occupied(p2)),
                not_(done(l2)),
                connected(p1, p2),
                next_swap_depth(d1, d2),
                clock(p1, d1),
                clock(p2, d1),
            ]
            effects = [
                not_(mapped(l1, p1)),
                mapped(l1, p2),
                not_(occupied(p1)),
                occupied(p2),
                not_(clock(p1, d1)),
                not_(clock(p2, d1)),
                clock(p1, d2),
                clock(p2, d2),
            ]
            return preconditions, effects

        @PDDLAction()
        def nop(p: pqubit, d1: depth, d2: depth):
            preconditions = [next_depth(d1, d2), clock(p, d1)]
            effects = [clock(p, d2), not_(clock(p, d1))]
            return preconditions, effects

        @PDDLAction()
        def nop_swap(p: pqubit, d1: depth, d2: depth):
            preconditions = [next_swap_depth(d1, d2), clock(p, d1)]
            effects = [clock(p, d2), not_(clock(p, d1))]
            return preconditions, effects

        gate_line_mapping = gate_line_dependency_mapping(circuit)
        gate_direct_mapping = gate_direct_dependency_mapping(circuit)

        gate_actions = []
        for gate_id, (gate_type, gate_logical_qubits) in gate_line_mapping.items():
            no_gate_dependency = gate_direct_mapping[gate_id] == []
            direct_predecessor_gates = gate_direct_mapping[gate_id]

            match gate_type:
                case "cx":
                    one_gate_dependency = len(gate_direct_mapping[gate_id]) == 1
                    if no_gate_dependency:
                        l1 = l[gate_logical_qubits[0]]
                        l2 = l[gate_logical_qubits[1]]

                        @PDDLAction(name=f"apply_cx_g{gate_id}")
                        def apply_gate(p1: pqubit, p2: pqubit, d1: depth, d2: depth):
                            preconditions = [
                                next_depth(d1, d2),
                                clock(p1, d1),
                                clock(p2, d1),
                                not_(done(g[gate_id])),
                                connected(p1, p2),
                                not_(occupied(p1)),
                                not_(occupied(p2)),
                                not_(done(l1)),
                                not_(done(l2)),
                            ]
                            effects = [
                                done(g[gate_id]),
                                occupied(p1),
                                occupied(p2),
                                done(l1),
                                done(l2),
                                mapped(l1, p1),
                                mapped(l2, p2),
                                clock(p1, d2),
                                clock(p2, d2),
                                not_(clock(p1, d1)),
                                not_(clock(p2, d1)),
                            ]

                            return preconditions, effects

                    elif one_gate_dependency:
                        earlier_gate = direct_predecessor_gates[0]
                        _, earlier_gate_logical_qubits = gate_line_mapping[earlier_gate]
                        occupied_logical_qubit = (
                            set(gate_logical_qubits)
                            .intersection(earlier_gate_logical_qubits)
                            .pop()
                        )

                        @PDDLAction(name=f"apply_cx_g{gate_id}")
                        def apply_gate(p1: pqubit, p2: pqubit, d1: depth, d2: depth):
                            occupied_physical_qubit = (
                                p1
                                if gate_logical_qubits.index(occupied_logical_qubit)
                                == 0
                                else p2
                            )
                            unoccupied_physical_qubit = (
                                p2
                                if gate_logical_qubits.index(occupied_logical_qubit)
                                == 0
                                else p1
                            )
                            unoccupied_logical_qubit = gate_logical_qubits[
                                1 - gate_logical_qubits.index(occupied_logical_qubit)
                            ]

                            preconditions = [
                                next_depth(d1, d2),
                                clock(p1, d1),
                                clock(p2, d1),
                                not_(done(g[gate_id])),
                                connected(p1, p2),
                                done(g[earlier_gate]),
                                mapped(
                                    l[occupied_logical_qubit],
                                    occupied_physical_qubit,
                                ),
                                not_(occupied(unoccupied_physical_qubit)),
                                not_(done(l[unoccupied_logical_qubit])),
                            ]
                            effects = [
                                done(g[gate_id]),
                                occupied(unoccupied_physical_qubit),
                                done(l[unoccupied_logical_qubit]),
                                mapped(
                                    l[unoccupied_logical_qubit],
                                    unoccupied_physical_qubit,
                                ),
                                clock(p1, d2),
                                clock(p2, d2),
                                not_(clock(p1, d1)),
                                not_(clock(p2, d1)),
                            ]

                            return preconditions, effects

                    else:

                        @PDDLAction(name=f"apply_cx_g{gate_id}")
                        def apply_gate(p1: pqubit, p2: pqubit, d1: depth, d2: depth):
                            control_qubit = l[gate_logical_qubits[0]]
                            target_qubit = l[gate_logical_qubits[1]]

                            preconditions = [
                                next_depth(d1, d2),
                                clock(p1, d1),
                                clock(p2, d1),
                                not_(done(g[gate_id])),
                                connected(p1, p2),
                                *[done(g[dep]) for dep in direct_predecessor_gates],
                                mapped(control_qubit, p1),
                                mapped(target_qubit, p2),
                            ]
                            effects = [
                                done(g[gate_id]),
                                clock(p1, d2),
                                clock(p2, d2),
                                not_(clock(p1, d1)),
                                not_(clock(p2, d1)),
                            ]

                            return preconditions, effects

                case _:
                    logical_qubit = l[gate_logical_qubits[0]]
                    if no_gate_dependency:

                        @PDDLAction(name=f"apply_gate_g{gate_id}")
                        def apply_gate(p: pqubit, d1: depth, d2: depth):
                            preconditions = [
                                next_depth(d1, d2),
                                clock(p, d1),
                                not_(done(g[gate_id])),
                                not_(occupied(p)),
                                not_(done(logical_qubit)),
                            ]
                            effects = [
                                done(g[gate_id]),
                                occupied(p),
                                done(logical_qubit),
                                mapped(logical_qubit, p),
                                clock(p, d2),
                                not_(clock(p, d1)),
                            ]

                            return preconditions, effects

                    else:

                        @PDDLAction(name=f"apply_gate_g{gate_id}")
                        def apply_gate(p: pqubit, d1: depth, d2: depth):
                            direct_predecessor_gate = g[direct_predecessor_gates[0]]
                            preconditions = [
                                next_depth(d1, d2),
                                clock(p, d1),
                                not_(done(g[gate_id])),
                                done(direct_predecessor_gate),
                                mapped(logical_qubit, p),
                            ]
                            effects = [
                                done(g[gate_id]),
                                clock(p, d2),
                                not_(clock(p, d1)),
                            ]

                            return preconditions, effects

            gate_actions.append(apply_gate)

        return PDDLInstance(
            types=[pqubit, lqubit, gate, depth],
            constants=[*l, *g, *d],
            objects=[*p],
            predicates=[
                occupied,
                mapped,
                connected,
                done,
                clock,
                next_depth,
                next_swap_depth,
            ],
            actions=[
                swap,
                swap_input,
                nop,
                nop_swap,
                *gate_actions,
            ],
            initial_state=[
                *[connected(p[i], p[j]) for i, j in platform.connectivity_graph],
                *[next_depth(d[i], d[i + 1]) for i in range(maximum_depth - 1)],
                *[next_swap_depth(d[i], d[i + 3]) for i in range(1, maximum_depth - 3)],
                *[clock(pi, d[0]) for pi in p],
            ],
            goal_state=[
                *[done(gi) for gi in g],
            ],
        )

    def synthesize(
        self,
        logical_circuit: QuantumCircuit,
        platform: Platform,
        solver: Solver,
        time_limit_s: int,
        logger: Logger,
        cx_optimal: bool = False,
        depth_bound: Optional[int] = None,
    ) -> SynthesizerOutput:
        min_plan_length_lambda = lambda depth: logical_circuit.size()
        max_plan_length_lambda = lambda depth: logical_circuit.num_qubits * depth
        min_layers_lambda = lambda depth: depth
        max_layers_lambda = lambda depth: depth

        return super().synthesize_incremental(
            logical_circuit,
            platform,
            solver,
            time_limit_s,
            logger,
            min_plan_length_lambda,
            max_plan_length_lambda,
            min_layers_lambda,
            max_layers_lambda,
            cx_optimal,
            depth_bound=depth_bound,
        )

    def parse_solution(
        self,
        original_circuit: QuantumCircuit,
        platform: Platform,
        solver_solution: list[str],
    ) -> tuple[QuantumCircuit, dict[LogicalQubit, PhysicalQubit]]:

        return super().parse_solution_grounded(
            original_circuit, platform, solver_solution
        )
