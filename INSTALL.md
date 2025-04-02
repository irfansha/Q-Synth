# Installing Q-Synth Dependencies

For running `./q-synth layout`, one only needs to install some Python
dependencies, preferrably in a virtual environment (venv).
This corresponds to Step 1 and Step 2 below.

To use more features of Q-synth requires installing external solvers.
In particular, to run `./q-synth cnot` requires installing at least
one planner, one SAT solver, or one QBF solver.
Similarly, to run `./q-synth clifford` requires installing one SAT solver.
This corresponds to Steps 3a, 3b and/or 3c below.

| Task              | Classical Planning         | SAT     | QBF            |
| ---               | ---                        | ---     | ---            |
| q-synth layout    | FastDownward or Madagascar | PySat   | --             |
| q-synth cnot      | FastDownward or Madagascar | Cadical | Caqe + Bloqqer |
| q-synth clifford  | --                         | Cadical | --             |


## Step 1: Python venv

Make a clean python environment in the QSynth folder (first time only):

    python3 -m venv QSynth-venv
    source QSynth-venv/bin/activate

### For Daily Usage:

Activation: `source QSynth-venv/bin/activate`

Deactivation: `deactivate`

## Step 2: Requirements -- Python module dependencies

Install all Python requirements at once:

    pip install -r requirements.txt

This will install the following dependencies:

- Qiskit: https://qiskit.org/
- rustworkx: https://github.com/Qiskit/rustworkx
- pysat: https://pysathq.github.io/
- python-constraint: https://pypi.org/project/python-constraint/
- pytest: https://pypi.org/project/pytest/ 

### Test Python dependencies

SAT based layout synthesis (v2.0) is now ready to use.
Use the following command to test the installation:

    ./q-synth.py layout -v1 -p melbourne Benchmarks/ICCAD-23/or.qasm

Maps the 3-qubit circuit `or.qasm` to the 14-qubit IBM platform `melbourne`, using 2 swaps.

## Step 3: Installation of Standalone External Solvers

Q-synth uses external solvers to find optimal circuits and layouts.
Optimal CNOT/Clifford synthesis needs at least one external solver.
Installing extra solvers will increase the capabilities of q-synth.

### Step 3a: Stand-alone SAT solver

For SAT-based CNOT synthesis and Clifford synthesis, Q-Synth needs an external SAT solver.
The reason is that pysat doesn't support time-out values.

#### Cadical:

    git clone https://github.com/arminbiere/cadical.git cadical
    cd cadical
    ./configure && make
    cd ..
    export PATH=$PWD/cadical/build:$PATH

#### Testing with Cadical

To test CNOT-synthesis with standalone Cadical, use:

    ./q-synth.py cnot -v1 Benchmarks/ECAI-24/tpar-optimized/tof_3.qasm

To test CNOT-Optimal Clifford synthesis with standalone Cadical, use:

    ./q-synth.py clifford -v1 Benchmarks/ECAI-24/tpar-optimized/tof_3.qasm

### Step 3b: Classical Planning

Both layout-mapping and CNOT-synthesis may use planning tools,
which operate on PDDL (domain and problem) files.

#### FastDownward:

    git clone https://github.com/aibasel/downward.git downward
    cd downward
    ./build.py
    cd ..
    export PATH=$PWD/downward:$PATH

For more details on FastDownward, see https://www.fast-downward.org/

#### Madagascar:

Executables are available at: https://research.ics.aalto.fi/software/sat/madagascar/

Ensure that the location of the executable 'M' is on the $PATH

    mkdir madagascar
    cd madagascar
    wget https://research.ics.aalto.fi/software/sat/madagascar/M
    chmod +x M
    cd ..
    export PATH=$PWD/madagascar:$PATH

#### Testing with Classical Planning

To do layout-synthesis with the `lifted` encoding in PDDL and solve with FastDownward (BJOLP), use

    ./q-synth.py layout -m lifted -s fd-bjolp -v1 -p melbourne Benchmarks/ICCAD-23/or.qasm

To do layout-synthesis with the `local` encoding in PDDL and solve with Madagascar, use

    ./q-synth.py layout -m local -s madagascar -v1 -p melbourne Benchmarks/ICCAD-23/or.qasm

To do peephole optimization with CNOT synthesis using planning with FastDownward (merge-and-shrink) use

    ./q-synth.py cnot -m planning -s fd-ms -v1 Benchmarks/ECAI-24/tpar-optimized/tof_3.qasm

### Step 3c: QBF Solving and Preprocessing

Both the layout-mapping and the CNOT-synthesis problem can be encoded 
more concisely in QBF. QBF-formulas can be solved by Caqe, usually
after preprocessing with Bloqqer.

#### Caqe:

    git clone https://github.com/ltentrup/caqe.git caqe
    cd caqe
    cargo build --release
    cd ..
    export PATH=$PWD/caqe/target/release:$PATH

#### Bloqqer:

    git clone https://github.com/rebryant/bloqqer.git bloqqer
    cd bloqqer
    ./configure && make
    cd ..
    export PATH=$PWD/bloqqer:$PATH

For more details on bloqqer, see https://fmv.jku.at/bloqqer/

#### Testing with QBF solving

To test CNOT synthesis with QBF solver Caqe and preprocessor Bloqqer, use

    ./q-synth.py cnot -m qbf -v1 Benchmarks/ECAI-24/tpar-optimized/tof_3.qasm
