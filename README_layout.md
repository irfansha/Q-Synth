# Layout Synthesis

For choosing Layout Synthesis use the subcommand 'layout'.
For help, use the following command:

    ./q-synth.py layout --help

For Layout Synthesis, this tool takes a quantum circuit in OPENQASM 2.0 format and the coupling graph of a physical quantum platform.
The output is an optimal mapping of the circuit onto the platform, preserving the gates and their dependencies,
respecting the coupling graph, and minimizing the number of SWAP operations (with or without using ancillary qubits).
We also support ancillary qubits, bridges instead of SWAPS, and relaxed dependencies based on gate commutation rules.
We employ two main approaches, classical planning (v1.0) and SAT-solver based parallel plans (v2.0).

## Installation:

For detailed instructions on installation, see the [Installation Instructions](INSTALL.md).

## Usage

Q-Synth works by transforming a circuit + platform to a classical planning problem (v1.0) or a SAT problem (v2.0), and solving it with an external solver. The solution is translated back to reconstruct the optimally mapped quantum layout.

### Positional argument:

    INPUT.qasm            input circuit file
    OUTPUT.qasm           output circuit file: None (d), our output file

### Common Options:

    -p, --platform        Quantum platform: tenerife, melbourne (d), tokyo and others
    -b, --bidirectional   Make coupling map bidirectional: 0=no, 1=yes (d), 2=use H-CNOT-H
    -a, --ancillas        Max nr of ancilla qubits: -1=unlimited (d), 0=none, 1,2,... specify max (*)
    -r, --relaxed         Relaxed or Strict Dependencies: 0=strict (d), 1=relaxed
    --bridge              Use bridges [0/1]. For now only supported with -r0, -a0 and -m sat
    --metric              Optimization metric: one of
                            cx-depth, cx-count, depth, cx-depth-cx-count, depth-cx-count
    --subarch             Use "subarchitectures" with exact number of ancillas: 0=no (d), 1=yes

    -t, --time            Solving time limit in seconds: 1800 (d)
    -v, --verbose         Verbosity [-1/0/1/2/3]: 
                            0=status (d), 1=visual, 2=extended, 3=debug, -1=silent
    -h, --help            Help with detailed description of all options
    --aux_files           location for intermediate files: ./intermediate_files (d)

### Classical Planning Options :

    -m, --model           Model type used for the encoding: -m planning
                          Chooses a default planner, depending on metrics
                            count-metric: -m global (d), local, or lifted
                            depth-metric: -m cond_cost_opt (d), cost_opt, or lc_incr
    -s, --solver          Planner solvers: fd-bjolp (d), fd-ms, madagascar, and others

### SAT-based Options :

    -m, --model           Model type used for the encoding: -m sat (d)
    -s, --solver          SAT solvers with --model=sat: cd19 (d), g42, cms, etc (1)
    --cardinality         At-Most and At-Least constraints from PySAT: 
                            0 = pairwise, 1 = seqcounter (d), 3 = sortnetwrk, etc (2)
    --start               Solve the sat instances, starting from this depth, 0 (d) (*)
    --step                Solve the sat instances, at depths modulo this step, 1 (d) (*)
    --end                 Solve sat instances until this depth (inclusive) when specified, None (d) (*)

### Experimental Options :

    -c, --cnot_cancel     Cancel CNOT gates before layout synthesis: 0=no (d), 1=yes
    --parallel_swaps      Adds parallel swaps in each time step [0/1], default 0 (*)

(d) default option  
(*) changing these options might lead to suboptimal results  
(1) See for all supported SAT solvers: [PySat solvers](https://pysathq.github.io/docs/html/api/solvers.html#pysat.solvers.SolverNames)  
(2) See for all cardinality constraints: [PySat cardinality](https://pysathq.github.io/docs/html/api/card.html#pysat.card.EncType)

### Debug option

    --check   Check correctness (equivalence, layout restrictions) [0/1]: 0=no (default), 1=yes

## Examples with Classical Planning (v1.0):

Map the Adder circuit on platform Tenerife (bi-directional) with 0 ancillary qubits.
Do this using the local model, with planner FastDownward with Merge-and-Shrink:

    ./q-synth.py layout -b1 -a0 -m local -p tenerife -s fd-ms -v1 Benchmarks/ICCAD-23/adder.qasm

Now map circuit barenco_tof_4.qasm to Melbourne (uni-directed), using FastDownward with BJOLP:

    ./q-synth.py layout -b0 -a0 -m local -p melbourne -s fd-bjolp -v1 Benchmarks/ICCAD-23/barenco_tof_4.qasm

This used 7 swaps. Let's now use unlimited ancillary bits and write the output to bar4_melbourne.qasm.

    ./q-synth.py layout -b0 -a-1 -m local -p melbourne -s fd-bjolp -v1 Benchmarks/ICCAD-23/barenco_tof_4.qasm bar4_melbourne.qasm

This uses only 6 swaps.

## Examples with SAT-based Parallel Plans (v2.0):

Map the 10-qubit vbe-adder circuit on platform 14-qubit Melbourne (bi-directional).
Do this using sat encoding, with sat solver Cadical:

    ./q-synth.py layout -b1 -a-1 -m sat -p melbourne -s cd15 -v1 Benchmarks/SAT-24/Standard/vbe_adder_3.qasm

This used 8 swaps. Using above planning based approaches timeout after 3 hours.
We can now solve the same instance within 5 seconds.

Now map circuit 6-qubit mod5mils_65.qasm to 54-qubit Sycamore platform with swaps+bridges:

    ./q-synth.py layout -b1 -a-1 -m sat -p sycamore -s cd15 -v1 Benchmarks/SAT-24/Standard/mod5mils_65.qasm  --bridge 1

This uses 1 swap and 3 bridges. Let's use relaxed dependencies instead of additional bridges:

    ./q-synth.py layout -b1 -a-1 -m sat -p sycamore -s cd15 -v1 Benchmarks/SAT-24/Standard/mod5mils_65.qasm  -r1

This uses only 4 swaps.


## Examples with Sub-architectures (v4.0):

Map the 5-qubit 4gt13_92 circuit on platform 53-qubit Sycamore (bi-directional) optimizing for cx-count.
Do this using sub-architectures allowing 2 ancillary qubits:

    ./q-synth.py layout -b1 -a 2 -m sat -p sycamore --subarch 1 -s cd19 -v1 Benchmarks/SAT-24/Standard/4gt13_92.qasm --metric cx-count

This uses 10 swaps.

Map the 8-qubit vqe circuit on platform 127-qubit IBM Eagle (bi-directional) optimizing for cx-count.
Do this using sub-architectures allowing 0 ancillary qubits:

    ./q-synth.py layout -b1 -a 0 -m sat -p eagle --subarch 1 -s cd19 -v1 Benchmarks/SAT-24/VQE/vqe_8_1_5_100.qasm --metric cx-count
    
This uses 3 swaps.

## Examples with Depth-Optimal Synthesis (v4.0):


Map the 4-qubit adder circuit on platform 5-qubits Tenerife optimizing for depth.

    ./q-synth.py layout -m sat -p tenerife -s cd19 -v1 Benchmarks/SAT-24/Standard/adder.qasm --metric depth

This gives a circuit with depth 15.

Now let's map this using optimization metric `cx-depth`:

    ./q-synth.py layout -m sat -p tenerife -s cd19 -v1 Benchmarks/SAT-24/Standard/adder.qasm --metric cx-depth

This yields a circuit with cx-depth 10.

One can also optimize for `depth` first, and then `cx-count`:

    ./q-synth.py layout -m sat -p tenerife -s cd19 -v1 Benchmarks/SAT-24/Standard/adder.qasm --metric depth-cx-count
    
Which results in a mapped circuit with depth 15 and 1 swap.

It is also possible to combine depth-optimal synthesis with sub-architectures :

    ./q-synth.py layout -m sat -p sycamore -s cd19 -v1 Benchmarks/SAT-24/Standard/4gt13_92.qasm --metric depth-cx-count --subarch 1 -a 2

This will compute the optimal mapping of 5-qubit circuit `4gt13_92` with respect to `depth-cx-count` metric on _7-qubit sub-architectures_ of the 53-qubit sycamore architecture.

## Run Experiments:

Use the following bash scripts for running the ICCAD 2023 experiments with Classical Planning:

    cd Scripts/ICCAD-23
    bash run_experiment1_tenerife.sh
    bash run_experiment2_melbourne.sh
    bash run_experiment3_noancillary.sh

Use the following bash scripts for running the SAT-2024 experiments with SAT-based Parallel Plans:

    cd Scripts/SAT-24
    bash run_experiment1_standard.sh
    bash run_experiment2_vqe.sh
    bash run_experiment3_additional_options.sh

## Copyright

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024, 2025
