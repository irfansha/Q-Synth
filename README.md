# Quantum-Circuit Synthesis - Q-Synth v4.0

Tools for quantum circuit synthesis, compilation and optimization.

    q-synth.py      Optimal Circuit Layout Synthesis and CNOT (Re)Synthesis, based on Classical Planning, SAT, and QBF Solving

This tool provides two synthesis options Layout Synthesis and CNOT (Re)Synthesis.

## Installation

For detailed instructions on installation, see the [Installation Instructions](INSTALL.md).

## Layout Synthesis

For choosing Layout Synthesis use the subcommand 'layout'.
For help use the following command:

    ./q-synth.py layout --help

For Layout Synthesis, this tool takes a quantum circuit in OPENQASM 2.0 format and the coupling graph of a physical quantum platform.
The output is an optimal mapping of the circuit onto the platform, preserving the gates and their dependencies,
respecting the coupling graph, and minimizing the number of SWAP operations (with or without using ancillary qubits).
We employ two main approaches, classical planning (v1.0) and SAT-solver based parallel plans (v2.0).

### Sample USAGE

Q-Synth works by transforming a circuit + platform to a classical planning problem (v1.0) or a SAT problem (v2.0), and solving it with an external solver. The solution is translated back to reconstruct the optimally mapped quantum layout.

For example, the following command maps an input_circuit to platform and returns mapped output_circuit:

    ./q-synth.py layout -p [platform] [input_circuit] [output_circuit]

For a detailed description of the available solvers and optimization criteria, see [README_layout.md](README_layout.md).

## CNOT (Re)Synthesis

For choosing CNOT Synthesis use the subcommand 'cnot'.
For help use the following command:

    ./q-synth.py cnot --help

For CNOT Synthesis, this tool takes a quantum circuit in OPENQASM 2.0 format and an optional coupling graph of a physical quantum platform.
The output is a resynthesized circuit in which all CNOT slices are replaced by optimal equivalent sub-circuits.

### Sample USAGE

Q-Synth works by encoding each CNOT sub-circuit to a classical planning problem, a SAT problem, or a QBF problem, and solving it with an external solver. The solution is translated back to reconstruct the optimal sub-circuit.

For example, the following command resynthesizes an input_circuit for a platform 
(taking the layout restrictions into account) and returns the optimized output_circuit:

    ./q-synth.py cnot -p [platform] [input_circuit] [output_circuit]

For a detailed description of the different synthesis combinations and solvers, see the [CNOT synthesis readme](README_cnot.md) page.

## Publications

Please refer to this publication for Layout-Synthesis based on classical-planning:

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

Please refer to this publication for Layout-Synthesis based on SAT encoding:

I. Shaik, J. van de Pol, _Optimal layout synthesis for deep quantum circuits on NISQ processors with 100+ qubits_.

    @article{shaikvdP2024layoutsynthesis,
      author       = {Irfansha Shaik and Jaco van de Pol},
      title        = {Optimal Layout Synthesis for Deep Quantum Circuits on {NISQ} Processors with 100+ Qubits}, 
      booktitle    = {27th International Conference on Theory and Applications of Satisfiability
                      Testing, {SAT} 2024, August 21-24, 2024, Pune, India},
      series       = {LIPIcs},
      publisher    = {Schloss Dagstuhl - Leibniz-Zentrum f{\"{u}}r Informatik},
      year         = {2024}
    }

Please refer to this publication for CNOT synthesis (based on Planning, SAT and QBF):

I. Shaik, J. van de Pol, _Optimal Layout-Aware CNOT Circuit Synthesis with Qubit Permutation_.
In: Proc. 27th European Conference on Artificial Intelligence, (ECAI'24), Santiago de Compostela, Spain, 2024.

    @inproceedings{ShaikvdP2024cnotsynthesis,
      author       = {Irfansha Shaik and Jaco van de Pol},
      title        = {Optimal Layout-Aware CNOT Circuit Synthesis with Qubit Permutation},
      booktitle    = {{ECAI'24}},
      address      = {{Santiago de Compostela, Spain}},
      publisher    = {IOS Press},
      year         = {2024}
    }


Please refer to this Bachelor's Thesis for Sub-Architectures:
K. Milkevych, J. van de Pol, _Maximal Sub-architectures for Quantum Mapping_.
    
    @mastersthesis{Milkevych2024
      title        = {Maximal Sub-architectures for Quantum Mapping},
      school       = {Aarhus University},
      author       = {Kostiantyn V. Milkevych and Jaco van de Pol},
      year         = {2024},
      type         = {Bachelor's Thesis},
      
    }

Please refer to this Master's Thesis for Depth-Optimal Synthesis:
A. B. Clausen, A. B. Jakobsen, _Depth-Optimal Quantum Layout Synthesis through Satisfiability_.

    @mastersthesis{Anders2024
      title        = {Depth-Optimal Quantum Layout Synthesis through Satisfiability},
      school       = {Aarhus University},
      author       = {Anders Benjamin Clausen and Anna Blume Jakobsen},
      year         = {2024},
    }

and the following [GitHub repository](https://github.com/anbclausen/quills).

## Limitations

The input should only contain unary gates and binary CNOT gates.

The script are tested on Linux and macOS.

## Copyright

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024

## Contributors

- Irfansha Shaik (Aarhus University, Kvantify)
- Jaco van de Pol (Aarhus University)
- Anna Blume Jakobsen (depth-optimal layout mapping)
- Anders B. Clausen (depth-optimal layout mapping)
- Kostiantyn Milkevych (subarchitectures, testing)
