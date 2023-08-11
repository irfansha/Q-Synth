# Quantum Synthesis

Tools for quantum circuit synthesis, compilation and optimization.

    q-synth.py            Optimal Circuit Layout Synthesis, based on Classical Planning and SAT Solving

This tool takes a quantum circuit in OPENQASM 2.0 format and the coupling graph of a physical quantum platform.
The output is an optimal mapping of the circuit onto the platform, preserving the gates and their dependencies,
respecting the coupling graph, and minimizing the number of SWAP operations (with or without using ancillary qubits).
It works by generating a classical planning problem, solving it with an external solver, 
and translating the plan to the mapped quantum layout.

## Positional argument:

    INPUT.qasm            input circuit file

## Options:

    -p, --platform        Quantum platform: tenerife, melbourne (d), tokyo and others
    -b, --bidirectional   Make coupling bidirectional: 0, 1 (d)
    -m, --model           Model type used for the encoding: global, local (d), lifted, local_initial, lifted_initial
    -a, --ancillary       Use ancillary qubits when mapping: 0 (d), 1
    -t, --time            Solving time limit in seconds: 1800 (d)
    -s, --solver          Planners: fd-bjolp (d), fd-ms, M-seq-optimal (Madagascar), and others
    -v, --verbose         [-1/0/1/2/3]: 0 (d)
    -h, --help            help with detailed description of all options
    --circuit_out         Output circuit file: None (d)
    --aux_files           location for intermediate files: ./intermediate_files (d)
    --run                 levels of execution: 0 = generate pddl files, 1 = map optimal layout, 2 = map + equivalence check (d)

## Examples:

Map the Adder circuit on platform Tenerife (bi-directional) without using ancillary qubits.
Do this using the local model, with planner FastDownard with Merge-and-Shrink:

    ./q-synth.py -b1 -a0 -m local -p tenerife -s fd-ms -v1 Benchmarks/adder.qasm 

Now map circuit barenco_tof_4.qasm to Melbourne (uni-directed), using FastDownward with BJOLP:

    ./q-synth.py -b0 -a0 -m local -p melbourne -s fd-bjolp -v1 Benchmarks/barenco_tof_4.qasm

This used 7 swaps. Let's now use ancillary bits and write the output to bar4_melbourne.qasm.

    ./q-synth.py -b0 -a1 -m local -p melbourne -s fd-bjolp -v1 Benchmarks/barenco_tof_4.qasm --circuit_out bar4_melbourne.qasm

This uses only 6 swaps.

## Dependencies:

- Qiskit : https://qiskit.org/
- FastDownward : https://www.fast-downward.org/
- Madagascar : https://research.ics.aalto.fi/software/sat/madagascar/

## Installation:

Qiskit :

    pip install qiskit

FastDownward :

    git clone https://github.com/aibasel/downward.git downward
    cd downward
    ./build.py

    Ensure that the location of the generated script fast-downward.py is on the $PATH

Madagascar : 

    Executables are available at : https://research.ics.aalto.fi/software/sat/madagascar/

    Ensure that the location of the executables 'M' and 'MpC' are on the $PATH

## Run Experiments:

Use the following bash scripts for running some experiments:

    cd Scripts
    bash run_experiment1_tenerife.sh
    bash run_experiment2_melbourne.sh
    bash run_experiment3_noancillary.sh

## Limitations

The input should only contain unary gates and binary CNOT gates.

The script is tested on Linux.

## Copyright and Publication

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

Please refer to this publication:

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
