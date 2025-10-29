# CNOT-Optimal Clifford Synthesis in Q-Synth (v5.0) via Command Line Interface

For choosing CNOT-Optimal Clifford (Re)Synthesis use the subcommand `clifford`.
For help, use the following command:

    ./q-synth.py clifford --help

## Strong and Weak Equivalence and Layout Restrictions

Given an input quantum Clifford circuit in OPENQASM 2.0 format, we provide 3 synthesis combinations:
- S   : output is an equivalent CNOT-Optimal Clifford circuit (strong equivalence).
- W   : output is an optimal CNOT-Optimal Clifford circuit equivalent up to a permutation of output qubits (weak equivalence).

If a coupling graph of a physical quantum platform is given as an input:
- S+R : output is an equivalent CNOT-Optimal Clifford circuit respecting the connectivity restrictions.

## Search Strategies

We allow two search strategies:
- Forward : outputs optimal Clifford circuit or timeouts.
- Backward : outputs the best Clifford circuit found within the time limit.

## Search space reduction

We employ two search reduction strategies for forward search:
- gate ordering: we fix the order on independent gates
- simple path restrictions: break cycles when reaching the target tableau (by default we break all 3-cycles)

## Peephole Optimization

Additionally, given an arbitrary quantum circuit (with gates beyond Clifford gates), Q-Synth performs peephole optimization.
We generate the Clifford slices in the given circuit and resynthesize them for the chosen synthesis combination and optimization metric.

Note: We do not guarantee Optimal CNOT-count or CNOT-depth when Peephole optimization is applied on arbitrary circuits.


## Installation

For detailed instructions on installation, see the [Installation Instructions](INSTALL.md).

## Usage

Q-Synth works by transforming each Clifford sub-circuit in a SAT, and solving it with an external solver.
The solution is translated back to reconstruct the corresponding CNOT-Optimal Clifford sub-circuit.

### Positional argument:

    INPUT.qasm                       input circuit file
    OUTPUT.qasm                      output circuit file: None (d)

### Choosing synthesis combination:

    -q, --qubit_permute              Allow any permutation of qubits in CNOT subcircuits
    -p, --platform                   Quantum platform: tenerife, melbourne (d), tokyo and others

### Optimization metric:

    --minimize                       Minimization metric for CNOT-Optimal Clifford synthesis:
                                       gates = minimizing number of CNOT gates (default)
                                       depth = CNOT-depth minimization

### Search space reduction:

    -g, --gate_ordering              Enable gate ordering 
    -r, --simple_path_restricitions  Restrict to only simple paths aka break cycles (default 3-cycles).

### Other options:
    -t, --time                       Solving time limit in seconds: 600 (d)
    -d, --disable_unused             Disable unused qubits (recommended in peephole setting for scalability)
    -v, --verbose                    Verbosity [-1/0/1/2]: 
                                       0=status (d), 1=visual, 2=extended, -1=silent
    -h, --help                       Help with detailed description of all options
    --aux_files                      Location for intermediate files: ./intermediate_files (d)

### Debug option

    --check                          Check correctness (equivalence, connectivty constraints) [0/1]: 0=no (default), 1=yes

## Examples for S synthesis i.e., without permutation:

Resynthesize the example from Clifford Synthesis paper, a 2-qubit Clifford circuit with 2 CNOT gates and 3 singles qubit gates, minimizing CNOT gate count.
Do this using the Cadical SAT solver:

    ./q-synth.py clifford -s cd --minimize cx-count -v 1 Benchmarks/Examples/sat25.qasm output.qasm

Our Clifford circuit with 2 CNOTs is replaced with an optimized circuit with only 1 CNOT gates. The optimized circuit is returned as output.qasm file.

Resynthesize the random 6-qubit Clifford circuit "6q50494" from Experiment 1, minimizing CNOT depth:

    ./q-synth.py clifford -s cd --minimize cx-depth -v 1 Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates/06q_50494.qasm

From original CNOT depth of 14, the optimized circuit depth reduced to only 5.

Instead of a Clifford circuit, resynthesize a 10-qubit vbe_adder_3.qasm circuit with 52 CNOT depth.
We disable unused qubits for efficiency using option `-d` (recommended for scalability):

    ./q-synth.py clifford -s cd --minimize cx-depth -d -v 1 Benchmarks/Feynman/state_phase_folded/vbe_adder_3.qasm

Now we have 16 slices with Clifford circuits, and the CNOT depth is reduced from 52 to 38.

## Examples for W synthesis i.e., with permutation:

Allowing qubit permutation can result in further CNOT gate and CNOT depth reduction.
Let us resynthesize the earlier vbe_adder_3.qasm now allowing qubit permutation (using flag `-q`):

    ./q-synth.py clifford -s cd --minimize cx-depth -v 1 -d -q Benchmarks/Feynman/state_phase_folded/vbe_adder_3.qasm

Instead of 38 CNOT depth from S synthesis, the final CNOT depth is only 36.

## Examples for S+R synthesis:

With S+R synthesis, we can resynthesize even optimally mapped circuits.
Let us resynthesize vbe_adder_3.qasm mapped to 54-qubit sycamore platform mapped by qiskit.
The qiskit mapped vbe_adder_3.qasm circuit is available in the benchmarks folder:

    Benchmarks/Feynman/mapped/sycamore-54/vbe_adder_3.qasm

For efficient resynthesis, we disable unused qubits (recommended), enable gate ordering and simple path restrictions using options `-d`, `-g`, and `-r`.
We can now resynthesize the circuit while taking layout restrictions (using option `-p sycamore`) into account using the following command:

     ./q-synth.py clifford -s cd --minimize cx-depth -p sycamore -d -g -r -v 1 Benchmarks/Feynman/mapped/sycamore-54/vbe_adder_3.qasm

The total CNOT depth from 79 is further reduced to 56.
One can also optimize the CNOT count while being layout aware similarly.

## Run Experiments:

Use the following bash scripts for running the SAT-2025 experiments:

    cd Scripts/SAT-25-CliffordSynthesis
    bash run_experiment1.sh
    bash run_experiment2.sh
    bash run_experiment3.sh


## Copyright

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024, 2025
