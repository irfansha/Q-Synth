# CNOT Synthesis in Q-Synth (v3.0)

For choosing CNOT (Re)Synthesis use the subcommand `cnot`.
For help, use the following command:

    ./q-synth.py cnot --help

## Strong and Weak Equivalence and Layout Restrictions

Given an input quantum CNOT circuit in OPENQASM 2.0 format, we provide 4 synthesis combinations:
- S   : output is an equivalent optimal CNOT circuit (strong equivalence).
- W   : output is an optimal CNOT circuit equivalent up to a permutation of output qubits (weak equivalence).

If a coupling graph of a physical quantum platform is given as an input:
- S+R : output is an equivalent optimal CNOT circuit respecting the connectivity restrictions.
- W+R : output is an optimal CNOT circuit equivalent up to a permutation of output qubits while respecting the connectivity restrictions.

## Encodings in Planning, SAT and QBF

We employ Classical Planning, SAT and QBF encodings for synthesis.
We provide gate (CNOT count) and depth optimization metrics.
For each solving technique, we list the available synthesis combinations:
- SAT: all 4 combinations, both for gate and depth optimization.
- QBF: S and S+R combinations, both for gate and depth optimization.
- Planning: S and S+R combinations only for gate optimization.

## Peephole Optimization

Additionally, given an arbitrary quantum circuit (with gates beyond CNOT gates), Q-Synth performs peephole optimization.
We generate the CNOT slices in the given circuit and resynthesize them for the chosen synthesis combination and optimization metric.

Note: W+R combination is not available for non-CNOT circuits via peephole optimization.

## Installation

For detailed instructions on installation, see the [Installation Instructions](INSTALL.md).

## Usage

Q-Synth works by transforming each CNOT sub-circuit in a planning, SAT, or QBF instance, and solving it with an external solver.
The solution is translated back to reconstruct the corresponding optimal CNOT sub-circuit.

### Positional argument:

    INPUT.qasm            input circuit file
    OUTPUT.qasm           output circuit file: None (d)

### Choosing synthesis combination:

    -q, --qubit_permute   Allow any permutation of qubits in CNOT subcircuits
    -p, --platform        Quantum platform: tenerife, melbourne (d), tokyo and others

### Choosing solving technique and solvers:

    -m , --model          Encoding to use: planning, sat, qbf
    -s, --solver          Solvers to use :
                            for planning : fd-ms, lama
                            for sat      : cadical
                            for qbf      : caqe

### Optimization metric:

    --minimize            Minimization metric for CNOT synthesis:
                            gates = minimizing number of gates (default)
                            depth = depth minimization (only for qbf and sat solvers)

### Other options:
    -t, --time            Solving time limit for each CNOT slicein seconds: 600 (d)
    -v, --verbose         Verbosity [-1/0/1/2]: 
                            0=status (d), 1=visual, 2=extended, -1=silent
    -h, --help            Help with detailed description of all options
    --aux_files           Location for intermediate files: ./intermediate_files (d)


### Debug option

    --check               Check correctness (equivalence, connectivty constraints) [0/1]: 0=no (default), 1=yes

## Examples for S synthesis:

Resynthesize the example from ECAI-2024 paper, a 4-qubit CNOT circuit with 6 CNOT gates, minimizing gate count.
Do this using the planning model, with planner FastDownward with Merge-and-Shrink:

    ./q-synth.py cnot -m planning -s fd-ms --minimize gates -v 1 Benchmarks/Examples/ecai24.qasm output.qasm

Our 6 CNOT circuit is replaced with an optimized circuit with only 3 CNOT gates. The optimized circuit is returned as output.qasm file.

To minimize depth of the circuit instead of gate count.
Instead of planning, we use a sat solver cadical using the following command:

    ./q-synth.py cnot -m sat -s cd --minimize depth -v 1 Benchmarks/Examples/ecai24.qasm

From original depth of 6, the optimized circuit depth reduced to only 3.

Instead of a CNOT circuit, resynthesize a 5-qubit barenco_tof_3.qasm circuit with 52 CNOTs and 28 single qubit gates.
Use the following command to use the qbf solver caqe:

    ./q-synth.py cnot -m qbf -s caqe --minimize gates -v 1 Benchmarks/ECAI-24/tpar-optimized/barenco_tof_3.qasm

Now we have 14 slices with CNOT circuits, and the CNOT gate count is reduced from 52 to 41.

## Examples for W synthesis:

Allowing qubit permutation can result in further gate and depth reduction.
Let us resynthesize the earlier barenco_tof_3.qasm now allowing qubit permutation (using flag `-q`).
Since only sat encoding allows permutation, we sat model with the following command:

    ./q-synth.py cnot -m sat -s cd --minimize gates -q -v 1 Benchmarks/ECAI-24/tpar-optimized/barenco_tof_3.qasm

Instead of 41 CNOT gates from S synthesis, the final CNOT count is only 26.

## Examples for S+R synthesis:

With S+R synthesis, we can resynthesize even optimally mapped circuits.
For demonstration, we first W synthesis barenco_tof_3.qasm and optimally map it onto 14-qubit melbourne platform using Q-Synth v2.0.
The optimally mapped barenco_tof_3.qasm circuit is available in the benchmarks folder:

    Benchmarks/ECAI-24/permuted_mapped/barenco_tof_3.qasm

We can resynthesize the circuit while taking layout restrictions (using option `-p melbourne`) into account using the following command:

    ./q-synth.py cnot -m sat -s cd --minimize gates -p melbourne -v 1 Benchmarks/ECAI-24/permuted_mapped/barenco_tof_3.qasm

The total CNOT gates from 44 is further reduced to 39.
One can also optimize the depth while being layout aware similarly.

## Examples for W+R synthesis:

We can only apply W+R synthesis for pure CNOT circuits.
First we map it to some platform of our choice (`-p tenerife`) using layout synthesis:

    ./q-synth.py layout -m sat -s cd -p tenerife -v 1 Benchmarks/Examples/ecai24.qasm ecai24_mapped.qasm

Let us (re)synthesize above mapped CNOT circuit with 6 CNOTs while being layout aware.
Use the following command enabling both qubit permutation (flag `-q`) and platform option (`-p tenerife`):

    ./q-synth.py cnot -m sat -s cd --minimize gates -p tenerife -q -v 1 ecai24_mapped.qasm

The optimized circuit now has 2 CNOTs instead of 6 while respecting the connectivity restrictions.

If we only used S+R synthesis for the same instance:

    ./q-synth.py cnot -m sat -s cd --minimize gates -p tenerife -v 1 ecai24_mapped.qasm

We now need 3 CNOTs instead of 2.

## Run Experiments:

Use the following bash scripts for running the ECAI-2024 experiments:

    cd Scripts/ECAI-24
    bash run_experiment1.sh
    bash run_experiment2.sh


## Copyright

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024, 2025
