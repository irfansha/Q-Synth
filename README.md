# Quantum-Circuit Synthesis - Q-Synth v2.0

Tools for quantum circuit synthesis, compilation and optimization.

    q-synth.py      Optimal Circuit Layout Synthesis, based on Classical Planning and SAT Solving

This tool takes a quantum circuit in OPENQASM 2.0 format and the coupling graph of a physical quantum platform.
The output is an optimal mapping of the circuit onto the platform, preserving the gates and their dependencies,
respecting the coupling graph, and minimizing the number of SWAP operations (with or without using ancillary qubits).
We also support ancillary qubits, bridges instead of SWAPS, and relaxed dependencies based on gate commutation rules.
We employ two main approaches, classical planning (v1.0) and SAT-solver based parallel plans (v2.0).

## USAGE

Q-Synth works by transforming a circuit + platform to a classical planning problem (v1.0) or a SAT problem (v2.0), and solving it with an external solver. The solution is translated back to reconstruct the optimally mapped quantum layout.

### Positional argument:

    INPUT.qasm            input circuit file
    OUTPUT.qasm           output circuit file: None (d)

### Common Options:

    -p, --platform        Quantum platform: tenerife, melbourne (d), tokyo and others
    -b, --bidirectional   Make coupling map bidirectional: 0=no, 1=yes (d), 2=use H-CNOT-H
    -a, --ancillary       Use ancillary qubits when mapping: 0=no, 1=yes (d) (*)
    --bridge              (NEW) Use bridges [0/1]. For now only with -r0, -a0, -i1 and -m sat
    -r, --relaxed         (NEW) Relaxed or Strict Dependencies: 0=strict (d), 1=relaxed

    -t, --time            Solving time limit in seconds: 1800 (d)
    -v, --verbose         Verbosity [-1/0/1/2/33]: 
                            0=status (d), 1=visual, 2=extended, 3=debug, -1=silent
    -h, --help            Help with detailed description of all options
    --aux_files           location for intermediate files: ./intermediate_files (d)
    --run                 mode: 0 = encoding only, 1 = layout mapping, 2 = map + test (d)

### Classical Planning Options :

    -m, --model           Model type used for the encoding: global, local, lifted
    -i, --initial         Initial mapping: 0=integrated (d), 1=separate init_map actions
    -s, --solver          Planners without --model=sat: fd-bjolp (d), fd-ms, and others

### SAT-based Options **(NEW)** :

    -m, --model           Model type used for the encoding: sat (d)
    -s, --solver          SAT solvers with --model=sat: cd (d), cd15, g4 and others
    --cardinality         At-Most and At-Least constraints from PySAT: 
                            0 = pairwise, 1 = seqcounter (d), and others
    --constraints         Three levels of sat encoding constraints: 
                            0 = minimal 1 = +pruning 2 = +redundant binary clauses (d)
    --start               Solve the sat instances, starting from this depth, 0 (d) (*)
    --step                Solve the sat instances, at depths modulo this step, 1 (d) (*)

### Experimental Options **(NEW)** :

    -c, --cnot_cancel     Cancel CNOT gates before layout synthesis: 0=no (d), 1=yes
    -q, --qiskit_optimize Qiskit post-optimization levels: 
                            0=none (d), [1,2,3] = standard qiskit levels
    --near_optimal        Adds bridges along with swaps [0/1], default 0 (*)
                            (adds  most k+1 bridges, if k is the optimal number of swaps)
    --parallel_swaps      Adds parallel swaps in each parallel time step [0/1], default 0 (*)
                            (bounded optimal)

(*) changing these options might lead to suboptimal results

## Examples with Classical Planning (v1.0):

Map the Adder circuit on platform Tenerife (bi-directional) without using ancillary qubits.
Do this using the local model, with planner FastDownward with Merge-and-Shrink:

    ./q-synth.py -b1 -a0 -m local -p tenerife -s fd-ms -v1 Benchmarks/Planning/adder.qasm 

Now map circuit barenco_tof_4.qasm to Melbourne (uni-directed), using FastDownward with BJOLP:

    ./q-synth.py -b0 -a0 -m local -p melbourne -s fd-bjolp -v1 Benchmarks/Planning/barenco_tof_4.qasm

This used 7 swaps. Let's now use ancillary bits and write the output to bar4_melbourne.qasm.

    ./q-synth.py -b0 -a1 -m local -p melbourne -s fd-bjolp -v1 Benchmarks/Planning/barenco_tof_4.qasm bar4_melbourne.qasm

This uses only 6 swaps.

## Examples with SAT-based Parallel Plans:

Map the 10-qubit vbe-adder circuit on platform 14-qubit Melbourne (bi-directional).
Do this using sat encoding, with sat solver Cadical:

    ./q-synth.py -b1 -a1 -m sat -p melbourne -s cd15 -v1 Benchmarks/SAT/Standard/vbe_adder_3.qasm

This used 8 swaps. Using above planning based approaches timeout after 3 hours.
We can now solve the same instance within 5 seconds.

Now map circuit 6-qubit mod5mils_65.qasm to 54-qubit Sycamore platform with swaps+bridges:

    ./q-synth.py -b1 -a1 -m sat -p sycamore -s cd15 -v1 Benchmarks/SAT/Standard/mod5mils_65.qasm  --bridge 1

This uses 1 swap and 3 bridges. Let's use relaxed dependencies instead of additional bridges:

    ./q-synth.py -b1 -a1 -m sat -p sycamore -s cd15 -v1 Benchmarks/SAT/Standard/mod5mils_65.qasm  -r1

This uses only 4 swaps.


## Dependencies:

- Qiskit : https://qiskit.org/
- QCEC : https://github.com/cda-tum/mqt-qcec

For Planning:

- FastDownward : https://www.fast-downward.org/
- Madagascar : https://research.ics.aalto.fi/software/sat/madagascar/

For SAT-based:

- pysat : https://pysathq.github.io/
- rustworkx : https://github.com/Qiskit/rustworkx



## Installation:

Qiskit :

    pip install qiskit==0.45.1

QCEC :

    pip install mqt.qcec==2.2.3

Pysat :

    pip install python-sat==0.1.8.dev2

rustworkx :

    pip install rustworkx==0.13.1

FastDownward :

    git clone https://github.com/aibasel/downward.git downward
    cd downward
    ./build.py

    Ensure that the location of the generated script fast-downward.py is on the $PATH

Madagascar : 

    Executables are available at : https://research.ics.aalto.fi/software/sat/madagascar/

    Ensure that the location of the executable 'M' is on the $PATH


## Run Experiments:

Use the following bash scripts for running the ICCAD 2023 experiments with Classical Planning:

    cd Scripts/Planning
    bash run_experiment1_tenerife.sh
    bash run_experiment2_melbourne.sh
    bash run_experiment3_noancillary.sh

Use the following bash scripts for running the experiments with SAT-based Parallel Plans:

    cd Scripts/SAT
    bash run_experiment1_standard.sh
    bash run_experiment2_vqe.sh
    bash run_experiment3_additional_options.sh

## Publication

Please refer to this publication for classical-planning based synthesis:

I. Shaik, J. van de Pol, _Optimal Layout Synthesis for Quantum Circuits as Classical Planning_. 
In: Proc. IEEE/ACM IC on Computer-Aided Design, (ICCAD'23), San Francisco, California, USA, 2023.

    @inproceedings{ShaikvdP2023,
      author       = {Irfansha Shaik and Jaco van de Pol},
      title        = {Optimal Layout Synthesis for Quantum Circuits as Classical Planning},
      booktitle    = {{ICCAD'23}},
      address      = {{San Diego, California, USA}},
      organization = {{IEEE/ACM}},
      year         = {2023}
    }

Please refer to this publication for SAT based synthesis:

I. Shaik, J. van de Pol, _Optimal layout synthesis for deep quantum circuits on NISQ processors with 100+ qubits_.
In: CoRR, abs/2403.11598, 2024. arXiv:2403.11598.

    @article{shaik2024optimal,
      author       = {Irfansha Shaik and Jaco van de Pol},
      title        = {Optimal Layout Synthesis for Deep Quantum Circuits on {NISQ} Processors with 100+ Qubits}, 
      journal      = {CoRR},
      volume       = {abs/2403.11598},
      eprinttype   = {arXiv},
      eprint       = {2403.11598},
      archivePrefix= {arXiv},
      primaryClass = {quant-ph},
      year         = {2024}
    }


## Limitations

The input should only contain unary gates and binary CNOT gates.

The script is tested on Linux.

## Copyright

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024
