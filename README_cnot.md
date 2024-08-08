# CNOT Synthesis

For choosing CNOT (Re)Synthesis use the subcommand 'cnot'.
For help, use the following command:

    ./q-synth.py cnot --help

Given an input quantum CNOT circuit in OPENQASM 2.0 format, we provide 4 synthesis combinations:
- S   : output is an equivalent optimal CNOT circuit.
- W   : output is an optimal CNOT circuit equivalent upto a permutation of output qubits.

If a coupling graph of a physical quantum platform is given as an input:
- S+R : output is an equivalent optimal CNOT circuit respecting the connectivity restrictions.
- W+R : output is an optimal CNOT circuit equivalent upto a permutation of output qubits while respecting the connectivity restricitions.

We employ Classical Planning, SAT and QBF encodings for synthesis.
We provide gate (CNOT count) and depth optimization metrics.
For each solving technique, we list the available synthesis combinations:
- SAT : all 4 combinations, both for gate and depth optimization.
- QBF : S and S+R combinations, both for gate and depth optimization.
- Planning : S and S+R combinations only for gate optimization.

Additionally, given an arbitrary quantum circuit (with gates other than CNOTs), we perform peephole optimization.
We generate CNOT slices in the given circuit and resynthesize them for chosen synthesis combination and optimization metric.

Note: W+R combination is not avaiable for non-CNOT circuits via peephole optimization.


## Dependencies:

- Qiskit : https://qiskit.org/
- QCEC : https://github.com/cda-tum/mqt-qcec (optional)
- rustworkx : https://github.com/Qiskit/rustworkx

For Planning:

- FastDownward : https://www.fast-downward.org/

For SAT-based:

- cadical : https://github.com/arminbiere/cadical

For QBF based:

- caqe : https://github.com/ltentrup/caqe
- bloqqer : https://fmv.jku.at/bloqqer/


## Installation:

### Step 1: Python venv (optional, recommended)
Make a clean python environment in QSynth folder:

    python3 -m venv QSynth-venv
    source QSynth-venv/bin/activate

#### For Daily Usage:

Activation: `source QSynth-venv/bin/activate`

Deactivation: `deactivate`

### Step 2: Requirements
Install python requirements:

    pip install -r requirements-cnot.txt

### Step 3: Solver Installation
Install appropriate solvers (at least one) for chosen solving techniques.

#### For Planning

FastDownward :

    git clone https://github.com/aibasel/downward.git downward
    cd downward
    ./build.py
    cd ..
    export PATH=$PWD/downward:$PATH

#### For SAT

Cadical :

    git clone https://github.com/arminbiere/cadical.git cadical
    cd cadical
    ./configure && make
    cd ..
    export PATH=$PWD/cadical/build:$PATH

### For QBF

Caqe :

    git clone https://github.com/ltentrup/caqe.git caqe
    cd caqe
    cargo build --release
    cd ..
    export PATH=$PWD/caqe/target/release:$PATH


Bloqqer :


    git clone https://github.com/rebryant/bloqqer.git bloqqer
    cd bloqqer
    ./configure && make
    cd ..
    export PATH=$PWD/bloqqer:$PATH

For more details on bloqqer installation, please refer to https://fmv.jku.at/bloqqer/

## USAGE

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
    --aux_files           location for intermediate files: ./intermediate_files (d)


### Debug option

    --check_equivalence   Check equivalence using qcec [0/1]: 0=no (default), 1=yes (*)

(*) requires installing QCEC, install via `pip install mqt.qcec==2.2.3`

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

With S+R resynthesis, we can resynthesis even optimally mapped circuits.
For demonstration, we first W synthesis barenco_tof_3.qasm and optimally map it onto 14-qubit melbourne platform using Q-Synth v2.0.
The optimally mapped barenco_tof_3.qasm circuit is available in the benchmarks folder:

    Benchmarks/ECAI-24/permuted_mapped/barenco_tof_3.qasm

We can resynthesis the circuit while taking layout restrictions (using option `-p melbourne`) into account using the following command:

    ./q-synth.py cnot -m sat -s cd --minimize gates -p melbourne -v 1 Benchmarks/ECAI-24/permuted_mapped/barenco_tof_3.qasm

The total CNOT gates from 44 is further reduced to 39.
One can also optimize the depth while being layout aware similarly.

## Examples for W+R synthesis:

We can only apply W+R synthesis for pure CNOT circuits.
Let us synthesize above example CNOT circuit while being layout aware.
Use the following command enabling both qubit permutation (flag `-q`) and platform option (`-p tenerife`):

    ./q-synth.py cnot -m sat -s cd --minimize gates -p tenerife -q -v 1 Benchmarks/Examples/ecai24.qasm

The optimized circuit now has 5 CNOTs instead of 6 while respecting the connectivity restrictions.

If we only used S+R synthesis for the same instance:

    ./q-synth.py cnot -m sat -s cd --minimize gates -p tenerife -v 1 Benchmarks/Examples/ecai24.qasm

We now need 6 CNOTs instead of 5.

## Run Experiments:

Use the following bash scripts for running the ECAI-2024 experiments:

    cd Scripts/ECAI-24
    bash run_experiment1.sh
    bash run_experiment2.sh


## Copyright

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024
