import math

from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap, PassManager
from qiskit.transpiler.passes import SabreLayout, SabreSwap

from qsynth.ReachabilitySolver.framework.reachability_encoding import Variable


def m(l, p, t):
    return Variable(name="m", params=[l, p], time_step=t)


def mp(p, t):
    return Variable(name="mp", params=[p], time_step=t)


def s(p1, p2, t):
    return Variable(name="s", params=[p1, p2], time_step=t)


def st(p, t):
    return Variable(name="st", params=[p], time_step=t)


def mc(i, t):
    return Variable(name="mc", params=[i], time_step=t)


def ac(i, t):
    return Variable(name="ac", params=[i], time_step=t)


def dc(i, t):
    return Variable(name="dc", params=[i], time_step=t)


def lp(l1, l2, t):
    return Variable(name="lp", params=[l1, l2], time_step=t)


def make_predecessor_and_successor_dictionaries(cnots: list[tuple[int, int]]):
    """
    Makes predecessor and successor dictionaries for the given CNOT gates. The dictionaries point to the immediate
    predecessors and successors of each gate. The predecessors are the last gates to have modified the control and
    target qubits respectively. The successors are the next gates to use the control and target qubits respectively.
    There can be at most 2 predecessors and 2 successors for each gate.
    Args:
        cnots: List of CNOT gates to compute predecessors and successors from.

    Returns:
        predecessors: Dictionary mapping CNOT gates to their immediate predecessors.
        successors: Dictionary mapping CNOT gates to their immediate successors.
    """
    dependency_dag = {i: set() for i in range(len(cnots))}
    last_modified = {}
    for i, (ctrl, trg) in enumerate(cnots):
        if ctrl in last_modified:
            dependency_dag[i].add(last_modified[ctrl])
        if trg in last_modified:
            dependency_dag[i].add(last_modified[trg])
        last_modified[ctrl] = i
        last_modified[trg] = i

    # This function computes all predecessors transitively which is unnecessary
    # predecessors = get_predecessor_dict_from_dependency_dag(dependency_dag)

    successors = {i: set() for i in range(len(cnots))}
    for i in dependency_dag:
        for j in dependency_dag[i]:
            successors[j].add(i)

    return dependency_dag, successors


def make_predecessor_dict_for_all_gates(circuit: QuantumCircuit):
    """
    Makes predecessor dictionary for all gates in the given circuit. Each gate maps to every (transitive) predecessor.
    """
    dependency_dag = {i: set() for i in range(len(circuit.data))}
    last_modified = {}
    for i, gate in enumerate(circuit.data):
        qubit_indices = [circuit.find_bit(q).index for q in gate.qubits]
        assert len(qubit_indices) in [1, 2], "Found gate with length > 2"
        for q in qubit_indices:
            if q in last_modified:
                dependency_dag[i].add(last_modified[q])
            last_modified[q] = i

    # Walk through gates in sorted order and add all transitive predecessors to every gate
    predecessors = {i: set() for i in dependency_dag.keys()}
    for i in dependency_dag.keys():
        for j in dependency_dag[i]:
            predecessors[i].add(j)
            for k in predecessors[j]:
                predecessors[i].add(k)

    return predecessors


def get_initial_mapping(initial_state, num_lqubits, num_pqubits):
    """
    Calculates the initial mapping between logical and physical qubits from the initial state of a solution to a
    layout synthesis reachability problem.
    Args:
        initial_state: List of true state variables in the initial state of a solution to a layout synthesis
                       reachability problem.
        num_lqubits: Number of logical qubits.
        num_pqubits: Number of physical qubits.

    Returns:
        l_to_p_mapping: Python dict mapping from logical to physical qubits
        p_to_l_mapping: Python dict mapping from physical to logical qubits
    """
    l_to_p_mapping = {var: None for var in range(num_lqubits)}
    p_to_l_mapping = {var: None for var in range(num_pqubits)}
    for var in initial_state:
        if var.name == "m":
            l, p = var.params
            assert l_to_p_mapping[l] is None
            assert p not in l_to_p_mapping.values()
            l_to_p_mapping[l] = p
            p_to_l_mapping[p] = l
    assert None not in l_to_p_mapping.values()
    return l_to_p_mapping, p_to_l_mapping


def swap_mapping(p1, p2, l_to_p_mapping, p_to_l_mapping):
    """
    Update the mapping between logical and physical qubits according to a SWAP on physical qubits p1 and p2.
    Mutates l_to_p_mapping and p_to_l_mapping.
    """
    l1, l2 = p_to_l_mapping[p1], p_to_l_mapping[p2]
    assert not (l1 is None and l2 is None), "Trying to swap two ancillary qubits"
    if l1 is None:
        l_to_p_mapping[l2] = p1
        p_to_l_mapping[p1] = l2
        p_to_l_mapping[p2] = None
    if l1 is not None:
        l_to_p_mapping[l1] = p2
    if l2 is not None:
        l_to_p_mapping[l2] = p1
    p_to_l_mapping[p1] = l2
    p_to_l_mapping[p2] = l1


def get_cnot_and_swap_sequence(action_sequence):
    """
    Returns CNOT sequence and SWAP sequence from an action sequence.
    Args:
        action_sequence: list of true action variables at each time step in the solution to a reachability problem

    Returns:
        cnot_sequence: list of CNOT gates applied at each time step sorted on gate index
        swap_sequence: list of the SWAP gate applied at each time step
    """
    cnot_sequence = []
    swap_sequence = []
    for timestep, vars in enumerate(action_sequence):
        cnots = []
        for var in vars:
            if var.name == "mc":
                i = var.params[0]
                cnots.append(i)
            elif var.name == "s":
                p1, p2 = var.params
                assert len(swap_sequence) == timestep
                swap_sequence.append((p1, p2))
            else:
                raise ValueError(f"Found unexpected variable name {var.name} in action sequence")
        cnot_sequence.append(sorted(cnots))
    return cnot_sequence, swap_sequence


def fast_upper_bound_on_swaps(circuit, coupling_graph, allow_ancillas=True):
    """Estimate upper bound on SWAPs needed for mapping."""
    coupling_map = CouplingMap(coupling_graph)
    if not allow_ancillas:
        # If ancillas are not allowed we make a coupling map with the same amount of qubits as the circuit
        coupling_map = coupling_map.reduce(list(range(circuit.num_qubits)))

    lowest_swaps = math.inf
    # We try 100 different seeds with 100 iterations on the layout pass and 50 trials on the swap pass,
    # and take the best result
    for seed in range(100):
        layout_pass = SabreLayout(coupling_map=coupling_map, seed=seed, max_iterations=100)
        swap_pass = SabreSwap(coupling_map=coupling_map, trials=50, seed=seed)
        pass_manager = PassManager([layout_pass, swap_pass])
        new_circuit = pass_manager.run(circuit)
        swaps = new_circuit.count_ops().get("swap", 0)
        lowest_swaps = min(swaps, lowest_swaps)
    return lowest_swaps


def test_predecessors_successors():
    cnots = [(2, 1), (0, 1), (2, 0), (2, 1), (2, 0), (0, 1)]
    pre, suc = make_predecessor_and_successor_dictionaries(cnots)

    print("predecessors:", pre)
    print("successors:", suc)

    init_state = ["m 0 1 0", "m 1 3 0", "m 2 2 0", "m 3 0 0"]
    l_to_p, p_to_l = get_initial_mapping(init_state, 4, 5)
    print("mapping:", l_to_p)

    print("swapping physical qubits 0 and 1")

    swap_mapping(0, 1, l_to_p, p_to_l)

    print("swapping physical qubit 3 with ancillary qubit 4")

    swap_mapping(3, 4, l_to_p, p_to_l)

    print("mapping:", l_to_p)
