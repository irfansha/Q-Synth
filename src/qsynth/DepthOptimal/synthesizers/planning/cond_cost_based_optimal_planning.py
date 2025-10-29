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
    increase_cost,
    when,
    forall,
)
from qsynth.DepthOptimal.synthesizers.planning.solvers import Solver
from qsynth.DepthOptimal.platform import Platform


class ConditionalCostBasedOptimalPlanningSynthesizer(PlanningSynthesizer):
    description = "Optimal cost-based synthesizer based on planning. Uses conditional effects and forall quantifiers."
    is_optimal = True
    uses_conditional_effects = True

    def create_instance(
        self, circuit: QuantumCircuit, platform: Platform
    ) -> PDDLInstance:
        num_pqubits = platform.qubits
        num_lqubits = circuit.num_qubits
        num_gates = circuit.size()

        class pqubit(object_):
            pass

        class gate(object_):
            pass

        class lqubit(gate):
            pass

        p = [pqubit(f"p{i}") for i in range(num_pqubits)]
        l = [lqubit(f"l{i}") for i in range(num_lqubits)]
        g = [gate(f"g{i}") for i in range(num_gates)]

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
        def idle(l: lqubit):
            pass

        @PDDLPredicate()
        def busy(l: lqubit):
            pass

        @PDDLPredicate()
        def swap1(l: lqubit):
            pass

        @PDDLPredicate()
        def swap2(l: lqubit):
            pass

        @PDDLAction()
        def map_initial(l: lqubit, p: pqubit):
            preconditions = [
                not_(occupied(p)),
                not_(done(l)),
            ]
            effects = [
                mapped(l, p),
                occupied(p),
                done(l),
                increase_cost(1),
            ]
            return preconditions, effects

        @PDDLAction()
        def swap(l1: lqubit, l2: lqubit, p1: pqubit, p2: pqubit):
            preconditions = [
                mapped(l1, p1),
                mapped(l2, p2),
                connected(p1, p2),
                idle(l1),
                idle(l2),
            ]
            effects = [
                not_(mapped(l1, p1)),
                not_(mapped(l2, p2)),
                mapped(l1, p2),
                mapped(l2, p1),
                swap1(l1),
                swap1(l2),
                not_(idle(l1)),
                not_(idle(l2)),
                increase_cost(1),
            ]
            return preconditions, effects

        @PDDLAction()
        def advance():
            preconditions = []

            def advance_busy(l: lqubit):
                return [when([busy(l)], [not_(busy(l)), idle(l)])]

            def advance_swap1(l: lqubit):
                return [when([swap1(l)], [not_(swap1(l)), swap2(l)])]

            def advance_swap2(l: lqubit):
                return [when([swap2(l)], [not_(swap2(l)), busy(l)])]

            effects = [
                forall(advance_busy),
                forall(advance_swap1),
                forall(advance_swap2),
                increase_cost(num_lqubits),
            ]
            return preconditions, effects

        gate_line_mapping = gate_line_dependency_mapping(circuit)
        gate_direct_mapping = gate_direct_dependency_mapping(circuit)

        gate_actions = []
        for gate_id, (gate_type, gate_logical_qubits) in gate_line_mapping.items():
            direct_predecessor_gates = gate_direct_mapping[gate_id]

            match gate_type:
                case "cx":

                    @PDDLAction(name=f"apply_cx_g{gate_id}")
                    def apply_gate(p1: pqubit, p2: pqubit):
                        control_qubit = l[gate_logical_qubits[0]]
                        target_qubit = l[gate_logical_qubits[1]]

                        preconditions = [
                            not_(done(g[gate_id])),
                            connected(p1, p2),
                            *[done(g[dep]) for dep in direct_predecessor_gates],
                            mapped(control_qubit, p1),
                            mapped(target_qubit, p2),
                            idle(control_qubit),
                            idle(target_qubit),
                        ]
                        effects = [
                            done(g[gate_id]),
                            busy(l[gate_logical_qubits[0]]),
                            busy(l[gate_logical_qubits[1]]),
                            not_(idle(l[gate_logical_qubits[0]])),
                            not_(idle(l[gate_logical_qubits[1]])),
                            increase_cost(1),
                        ]

                        return preconditions, effects

                case _:
                    logical_qubit = l[gate_logical_qubits[0]]

                    @PDDLAction(name=f"apply_gate_g{gate_id}")
                    def apply_gate(p: pqubit):
                        preconditions = [
                            not_(done(g[gate_id])),
                            *[done(g[dep]) for dep in direct_predecessor_gates],
                            mapped(logical_qubit, p),
                            idle(logical_qubit),
                        ]
                        effects = [
                            done(g[gate_id]),
                            busy(logical_qubit),
                            not_(idle(logical_qubit)),
                            increase_cost(1),
                        ]

                        return preconditions, effects

            gate_actions.append(apply_gate)

        return PDDLInstance(
            types=[pqubit, lqubit, gate],
            constants=[*l, *g],
            objects=[*p],
            predicates=[occupied, mapped, connected, done, busy, idle, swap1, swap2],
            actions=[
                map_initial,
                swap,
                advance,
                *gate_actions,
            ],
            initial_state=[
                *[connected(p[i], p[j]) for i, j in platform.connectivity_graph],
                *[idle(lq) for lq in l],
            ],
            goal_state=[
                *[done(gi) for gi in g],
                *[not_(swap1(li)) for li in l],
                *[not_(swap2(li)) for li in l],
            ],
            cost_function=True,
        )

    def synthesize(
        self,
        logical_circuit: QuantumCircuit,
        platform: Platform,
        solver: Solver,
        time_limit_s: int,
        logger: Logger,
        cx_optimal: bool = False,
    ) -> SynthesizerOutput:

        min_plan_length = logical_circuit.size()
        maximum_depth = logical_circuit.size() * (1 + platform.qubits) + 1
        max_plan_length = logical_circuit.num_qubits * maximum_depth

        return super().synthesize_optimal(
            logical_circuit,
            platform,
            solver,
            time_limit_s,
            logger,
            min_plan_length,
            max_plan_length,
            min_plan_length,
            max_plan_length,
            cx_optimal,
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
