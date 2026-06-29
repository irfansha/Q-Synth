# Irfansha Shaik, 17.09.2024, Aarhus

import dataclasses

all_visited_states = []
state_to_sequence_dict = {}


# we realize that any state can atmost have a XOR of 4 terms
# xi + xj + zi + zj, or any subset of this
# we will use this to keep track of the state and manipulate when XORs are applied:
@dataclasses.dataclass(unsafe_hash=True)
class xor_state:
    # by default false, we set required ones to true:
    xi: bool = False
    xj: bool = False
    zi: bool = False
    zj: bool = False

    def xor_xi(self):
        if self.xi == True:
            self.xi = False
        else:
            assert self.xi == False
            self.xi = True

    def xor_xj(self):
        if self.xj == True:
            self.xj = False
        else:
            assert self.xj == False
            self.xj = True

    def xor_zi(self):
        if self.zi == True:
            self.zi = False
        else:
            assert self.zi == False
            self.zi = True

    def xor_zj(self):
        if self.zj == True:
            self.zj = False
        else:
            assert self.zj == False
            self.zj = True

    def copy_update(self, other_xor):
        self.xi = other_xor.xi
        self.xj = other_xor.xj
        self.zi = other_xor.zi
        self.zj = other_xor.zj

    # updating current state by xoring with input control state:
    def xor_update(self, control_xor):
        if control_xor.xi:
            self.xor_xi()
        if control_xor.xj:
            self.xor_xj()
        if control_xor.zi:
            self.xor_zi()
        if control_xor.zj:
            self.xor_zj()

    def __str__(self) -> str:
        enabled_values = []
        if self.xi:
            enabled_values.append("xi")
        if self.xj:
            enabled_values.append("xj")
        if self.zi:
            enabled_values.append("zi")
        if self.zj:
            enabled_values.append("zj")
        return "+".join(enabled_values).ljust(12)


# Swaps x colum and z column:
def apply_h_gate(X, Z):
    X_copy = dataclasses.replace(X)
    X.copy_update(Z)
    Z.copy_update(X_copy)


# Column addition between x column and z column, so we do the same for the truth table:
def apply_p_gate(X, Z):
    Z.xor_update(X)


# Column additions between xi and xj columns; and zj and zi columns:
def apply_cnot_gate(Xi, Xj, Zi, Zj):
    Xj.xor_update(Xi)
    Zi.xor_update(Zj)

# CNOT is applied from i to j by default for now:
def apply_entangling_gate_sequences(
    qi, qj, qi_end, qj_end, Xi, Zi, Xj, Zj, flip_cnot=False
):
    # First on qubit i:
    for gate in qi:
        if gate == "H":
            apply_h_gate(X=Xi, Z=Zi)
        elif gate == "P":
            apply_p_gate(X=Xi, Z=Zi)
    # Second on qubit j:
    for gate in qj:
        if gate == "H":
            apply_h_gate(X=Xj, Z=Zj)
        elif gate == "P":
            apply_p_gate(X=Xj, Z=Zj)

    # print("precnot ",Xi, Zi, Xj, Zj)
    if flip_cnot:
        # apply cnot gate (j,i):
        apply_cnot_gate(Xi=Xj, Zi=Zj, Xj=Xi, Zj=Zi)
    else:
        # apply cnot gate (i,j):
        apply_cnot_gate(Xi=Xi, Zi=Zi, Xj=Xj, Zj=Zj)
    # print("postcnot ",Xi, Zi, Xj, Zj)

    # applying post qi and qj sequences:
    for gate in qi_end:
        if gate == "H":
            apply_h_gate(X=Xi, Z=Zi)
        elif gate == "P":
            apply_p_gate(X=Xi, Z=Zi)
    # Second on qubit j:
    for gate in qj_end:
        if gate == "H":
            apply_h_gate(X=Xj, Z=Zj)
        elif gate == "P":
            apply_p_gate(X=Xj, Z=Zj)

def per_sequence_equivalence(qi_sequence, qj_sequence, flip_cnot=False, verbose=False):
    equivalent_sequences = []
    base_Xi = xor_state(xi=True)
    base_Zi = xor_state(zi=True)
    base_Xj = xor_state(xj=True)
    base_Zj = xor_state(zj=True)
    apply_entangling_gate_sequences(
        qi=qi_sequence,
        qj=qj_sequence,
        qi_end="",
        qj_end="",
        Xi=base_Xi,
        Zi=base_Zi,
        Xj=base_Xj,
        Zj=base_Zj,
        flip_cnot=False, # for base case, we always do not flip
    )
    for qi_start_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
        for qj_start_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
            for qi_end_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
                for qj_end_sequence in ["", "HP", "PH", "H", "P", "HPH"]:
                    # starting with xi, xj, zi, zj:
                    Xi = xor_state(xi=True)
                    Zi = xor_state(zi=True)
                    Xj = xor_state(xj=True)
                    Zj = xor_state(zj=True)
                    apply_entangling_gate_sequences(
                        qi=qi_start_sequence,
                        qj=qj_start_sequence,
                        qi_end=qi_end_sequence,
                        qj_end=qj_end_sequence,
                        Xi=Xi,
                        Zi=Zi,
                        Xj=Xj,
                        Zj=Zj,
                        flip_cnot=flip_cnot,
                    )
                    if qi_start_sequence == qi_sequence and qj_start_sequence == qj_sequence and qi_end_sequence == "" and qj_end_sequence == "" and flip_cnot == False:
                        assert base_Xi == Xi and base_Zi == Zi and base_Xj == Xj and base_Zj == Zj
                    if base_Xi == Xi and base_Zi == Zi and base_Xj == Xj and base_Zj == Zj:
                        equivalent_sequences.append((qi_start_sequence, qj_start_sequence, qi_end_sequence, qj_end_sequence))
                        #print(f"Equivalent found for {qi_sequence, qj_sequence} with {qi_end_sequence, qj_end_sequence}")
    return equivalent_sequences

def find_all_equivalents(verbose=False):
    unique_equivalents = {}
    valid_single_qubit_sequences = ["", "HP", "PH", "H", "P", "HPH"]
    for qi_sequence in valid_single_qubit_sequences:
        for qj_sequence in valid_single_qubit_sequences:
            equivalents = per_sequence_equivalence(qi_sequence, qj_sequence, flip_cnot=False, verbose=verbose)
            unique_equivalents[(qi_sequence, qj_sequence)] = equivalents
    return unique_equivalents
def find_all_equivalents_with_reverse(verbose=False):
    unique_equivalents = {}
    valid_single_qubit_sequences = ["", "HP", "PH", "H", "P", "HPH"]
    for qi_sequence in valid_single_qubit_sequences:
        for qj_sequence in valid_single_qubit_sequences:
            equivalents = per_sequence_equivalence(qi_sequence, qj_sequence, flip_cnot=True, verbose=verbose)
            unique_equivalents[(qi_sequence, qj_sequence)] = equivalents
    return unique_equivalents

unique_equivalents = find_all_equivalents()
unique_equivalents_with_reverse = find_all_equivalents_with_reverse()

def has_hp_or_ph(sequence_tuple):
    for seq in sequence_tuple:
        if seq == "HP" or seq == "PH" or seq == "hp" or seq == "ph":
            return True
    return False

def has_h(pair):
    for seq in pair:
        if seq == "H" or seq == "h":
            return True
    return False

def print_all_equivalents_for_hp_ph():
    for key, value in unique_equivalents.items():
        if has_hp_or_ph(key):
            print(f"Sequence {key}:")
            no_hp_ph_equivalents = [seq for seq in value if not has_hp_or_ph((seq[0], seq[1]))]
            no_hp_ph_equivalents_rev = [seq for seq in unique_equivalents_with_reverse[key] if not has_hp_or_ph((seq[0], seq[1]))]
            for equivalent in no_hp_ph_equivalents:
                print(f"  (d):                       {equivalent}")
            for equivalent in no_hp_ph_equivalents_rev:
                print(f"  (f):                       {equivalent}")

def print_all_equivalents():
    for key, value in unique_equivalents.items():
        print(f"Sequence {key}:")
        for equivalent in value:
            print(f"  (d):                       {equivalent}")
        for equivalent in unique_equivalents_with_reverse[key]:
            print(f"  (f):                       {equivalent}")

#print_all_equivalents()


def generate_clauses_for_unique_normalforms(allow_flips=False):
    from pysat.formula import Atom, And, Or, CNF, Formula
    from pysat.solvers import Solver
    from pysat.formula import CNF
    ctrl_i, trg_i = Atom('ctrl_i'), Atom('trg_i')
    ctrl_h, trg_h = Atom('ctrl_h'), Atom('trg_h')
    ctrl_p, trg_p = Atom('ctrl_p'), Atom('trg_p')
    ctrl_hp, trg_hp = Atom('ctrl_hp'), Atom('trg_hp')
    ctrl_ph, trg_ph = Atom('ctrl_ph'), Atom('trg_ph')
    ctrl_hph, trg_hph = Atom('ctrl_hph'), Atom('trg_hph')
    ctrl_var_dict = {
        "": ctrl_i,
        "H": ctrl_h,
        "P": ctrl_p,
        "HP": ctrl_hp,
        "PH": ctrl_ph,
        "HPH": ctrl_hph,
    }
    trg_var_dict = {
        "": trg_i,
        "H": trg_h,
        "P": trg_p,
        "HP": trg_hp,
        "PH": trg_ph,
        "HPH": trg_hph,
    }
    per_key_clauses = []
    for key, value in unique_equivalents.items():
        disjunction_clauses = []
        for equivalent in value:
            #print(f"  (d):                       {equivalent}")
            #print(ctrl_var_dict[equivalent[0]], trg_var_dict[equivalent[1]])
            disjunction_clauses.append(And(ctrl_var_dict[equivalent[0]], trg_var_dict[equivalent[1]]))
        if allow_flips:
            rev_value = unique_equivalents_with_reverse[key]
            for equivalent in rev_value:
                #print(f"  (f):                       {equivalent}")
                #print(ctrl_var_dict[equivalent[0]], trg_var_dict[equivalent[1]])
                disjunction_clauses.append(And(ctrl_var_dict[equivalent[0]], trg_var_dict[equivalent[1]]))
        print("Clause for (d) and (f): ", Or(*disjunction_clauses))
        per_key_clauses.append(Or(*disjunction_clauses))
    
    formula = And(*per_key_clauses)
    formula.clausify()
    cnf = CNF(from_clauses=formula.clauses)
    print("CNF clauses:", cnf.clauses)
    
    # Get the variable mapping
    vpool = Formula.export_vpool()
    var_dict = vpool.id2obj
    print("Variable mapping (int to Atom):", var_dict)
    
    # Get original variable IDs
    original_var_ids = []
    for k, v in var_dict.items():
        if isinstance(v, Atom):
            obj = getattr(v, 'object', None)
            if obj and isinstance(obj, str) and (obj.startswith('ctrl_') or obj.startswith('trg_')):
                original_var_ids.append(k)
    print("Original var IDs:", original_var_ids)
    solutions_ctrls_targets = []
    # Solve the CNF
    with Solver(bootstrap_with=formula) as solver:
        if solver.solve():
            model = solver.get_model()
            print("SAT solution found:", model)
            true_atoms = [var_dict[lit].object for lit in model if lit > 0 and lit in original_var_ids]
            controls = [atom.replace('ctrl_', '') for atom in true_atoms if atom.startswith('ctrl_')]
            targets = [atom.replace('trg_', '') for atom in true_atoms if atom.startswith('trg_')]
            print("True original atoms: Controls:", controls, "Targets:", targets)
            # Optionally, enumerate all solutions
            solutions = []
            for i, sol in enumerate(solver.enum_models()):
                solutions.append(sol)
            print(f"All SAT solutions ({len(solutions)} found):")
            for i, sol in enumerate(solutions):
                true_atoms_sol = [var_dict[lit].object for lit in sol if lit > 0 and lit in original_var_ids]
                controls_sol = [atom.replace('ctrl_', '') for atom in true_atoms_sol if atom.startswith('ctrl_')]
                targets_sol = [atom.replace('trg_', '') for atom in true_atoms_sol if atom.startswith('trg_')]
                controls_str = str(controls_sol)
                targets_str = str(targets_sol)
                solutions_ctrls_targets.append((controls_sol, targets_sol))
                print(f"  Solution {i+1}: Controls: {controls_str:<35} Targets: {targets_str}")
        else:
            print("UNSAT")
    return solutions_ctrls_targets

#all_normalforms = generate_clauses_for_unique_normalforms(allow_flips=False)

# minimal normal forms:
# if normal form 1 has (c1, t1) and normal form 2 has (c2, t2)
# and if c1 and t1 are subsets or equal to c2 and t2 respectively,
# then normal form 1 is more minimal than normal form 2

def is_subset_normalform(form1, form2):
    c1, t1 = set(form1[0]), set(form1[1])
    c2, t2 = set(form2[0]), set(form2[1])
    return c1.issubset(c2) and t1.issubset(t2)

def get_minimal_normalforms(all_forms):
    minimal_forms = []
    for i, form1 in enumerate(all_forms):
        is_minimal = True
        for j, form2 in enumerate(all_forms):
            if i != j and is_subset_normalform(form1, form2):
                # If form1 is a subset of form2 but not equal, and form2 is not more minimal
                if form1 != form2:
                    is_minimal = is_minimal and True
            elif i != j and is_subset_normalform(form2, form1):
                # If form2 is a subset of form1, form1 is not minimal
                if form1 != form2:
                    is_minimal = False
                    break
        if is_minimal:
            minimal_forms.append(form1)
    return minimal_forms
all_normalforms = generate_clauses_for_unique_normalforms(allow_flips=True)
minimal_normalforms = get_minimal_normalforms(all_normalforms)
print("\nMinimal Normal Forms:")
for i, (controls, targets) in enumerate(minimal_normalforms):
    print(f"  {i+1}: Controls: {controls} Targets: {targets}")
#"""
# Gate cost dictionary: {sequence: (rx_cost, rz_cost)}
gate_costs = {
    "i":    (0, 0),
    "p":   (0, 1),
    "h":   (1, 2),
    "hp":  (1, 1),
    "ph":  (1, 1),
    "hph": (1, 0),
}

min_rx_cost = None
min_rz_cost = None

for i, (controls, targets) in enumerate(minimal_normalforms):
    controls_str = str(controls)
    targets_str = str(targets)
    rx_cost = 0
    rz_cost = 0
    for seq in (controls):
        rx, rz = gate_costs[seq][0], gate_costs[seq][1]
        rx_cost += rx
        rz_cost += rz
    for seq in (targets):
        rx, rz = gate_costs[seq][0], gate_costs[seq][1]
        rx_cost += rx
        rz_cost += rz
    #print(controls, targets)
    #print(f"Total cost for Normal form {i+1}: RX: {rx_cost}, RZ: {rz_cost}")
    if min_rx_cost is None or rx_cost < min_rx_cost:
        min_rx_cost = rx_cost
    if min_rz_cost is None or rz_cost < min_rz_cost:
        min_rz_cost = rz_cost
    if rx_cost <= 2:
        print(f"  -- Minimal {i+1}: Controls: {controls_str:<35} Targets: {targets_str}")
        print(f"    Cost: RX: {rx_cost}, RZ: {rz_cost}")
print(f"\nMinimum RX cost among minimal normal forms: {min_rx_cost}")
print(f"Minimum RZ cost among minimal normal forms: {min_rz_cost}")
#"""