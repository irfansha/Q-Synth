# Quantum-Circuit Synthesis - Q-Synth v5.1

A state-of-the-art, open-source, optimal quantum circuit synthesis tool.
This tool provides three main functionalities: 
- Optimal Layout Synthesis, 
- Optimal CNOT (Re)Synthesis, and 
- Optimal Clifford (Re)Synthesis.

## Key Features
- Layout Synthesis with Classical Planning and SAT, optimizing CNOT-count/depth (v1.0, v2.0, v4.0).
- Layout aware CNOT (Re)Synthesis with Planning, SAT and QBF, optimizing CNOT-count/depth (v3.0).
- Layout aware Clifford (Re)Synthesis with SAT, optimizing CNOT-count/depth (v5.0).
- CNOT and Clifford re-synthesis can be applied to slices in a peephole synthesis (v3.0, v5.0)
- Scalable layout synthesis for large platforms via maximal subarchitectures (v4.0).
- All efficient synthesis features based on SAT are available via an API (with simple pip-installation, v5.1).
- Additional features with planning and QBF are available via the command line interface.

## Getting started

Q-Synth can be installed using pip:
> **Recommended:** Please use a fresh python virtual environment.

    pip install Q-Synth


### Layout Synthesis

For layout synthesis through the API, simply call `layout_synthesis` with your circuit (as a qiskit QuantumCircuit) and a coupling graph as input. For example:

    from qsynth import get_coupling_graph, layout_synthesis
    from qiskit import QuantumCircuit

    # An example bidirectional coupling graph
    coupling_graph = get_coupling_graph(coupling_graph=[[0,1],[1,2]], bidirectional=1)

    qc = QuantumCircuit(3)
    qc.cx(0,1)
    qc.s(0)
    qc.cx(0,2)
    qc.cx(1,2)

    mapped_result = layout_synthesis(circuit=qc, coupling_graph=coupling_graph, metric="cx-count", verbose=-1) # silent mode
    print(mapped_result.circuit)
    print(mapped_result.initial_mapping)
    print(mapped_result.final_mapping)

`mapped_result.circuit` contains the mapped circuit with provably optimal swap count,
`mapped_result.initial_mapping` contains the initial mapping,
and `mapped_result.final_mapping` stores the output qubit permutation.

### Peephole Synthesis with CNOT and Clifford (Re)Synthesis

Q-Synth can re-synthesize each CNOT/Clifford sub-circuit in a peephole manner to reduce the CNOT count or depth, while still respecting the layout constraints.  
For example, we can easily resynthesize our mapped result circuit using peephole synthesis with CNOT slicing using:

    from qsynth import peephole_synthesis
    opt_result = peephole_synthesis(circuit=mapped_result.circuit, coupling_graph=coupling_graph, slicing="cnot", metric="cx-count")

`opt_result.circuit` contains the resynthesized circuit with 5 CNOTs instead of 6 without any extra single qubit gates.

Clifford slicing allows resynthesis of even larger sub-circuits with possible further reductions. Simply use `slicing="clifford"` in `peephole_synthesis` to enables this.

    opt_result = peephole_synthesis(circuit=mapped_result.circuit, coupling_graph=coupling_graph, slicing="clifford", metric="cx-count")

`opt_result.circuit` now only has 4 CNOTs, but with some additional single qubit gates.

### Tutorial and Command-line tools

Q-Synth also supports several other features such as optimizing for CNOT depth, using subarchitectures, qubit permutations, and more.
Please refer to tutorials in [Jupyter Notebook](https://github.com/irfansha/Q-Synth/blob/main/Tutorials/qsynth.ipynb) for more examples.

More features are available via the command line interface, for instance those based on classical planning and QBF solvers.
Please see the Installation Instructions in [INSTALL_CLI.md](https://github.com/irfansha/Q-Synth/blob/main/Tutorials/INSTALL_CLI.md).  
Detailed descriptions of the command-line tools are available in [README_CLI_layout.md](https://github.com/irfansha/Q-Synth/blob/main/Tutorials/README_CLI_layout.md) and
[README_CLI_cnot.md](https://github.com/irfansha/Q-Synth/blob/main/Tutorials/README_CLI_cnot.md) and
[README_CLI_clifford.md](https://github.com/irfansha/Q-Synth/blob/main/Tutorials/README_CLI_clifford.md).

## Publications

Please refer to this publication for Layout-Synthesis based on classical-planning (v1.0):

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

Please refer to this publication for Layout-Synthesis based on SAT encoding (v2.0):

I. Shaik, J. van de Pol, _Optimal layout synthesis for deep quantum circuits on NISQ processors with 100+ qubits_.  
In: Proc. 27th IC on Theory and Applications of Satisfiability Testing (SAT'24), Pune, India, 2024.

    @article{shaikvdP2024layoutsynthesis,
      author       = {Irfansha Shaik and Jaco van de Pol},
      title        = {Optimal Layout Synthesis for Deep Quantum Circuits on {NISQ} Processors with 100+ Qubits}, 
      booktitle    = {27th IC on Theory and Applications of Satisfiability
                      Testing, {SAT} 2024, August 21-24, 2024, Pune, India},
      series       = {LIPIcs},
      publisher    = {Schloss Dagstuhl - Leibniz-Zentrum f{\"{u}}r Informatik},
      year         = {2024}
    }

Please refer to this publication for CNOT synthesis (based on Planning, SAT and QBF) (v3.0):

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


Please refer to this publication for Depth-Optimal Synthesis (v4.0):

A. B. Clausen, A. B. Jakobsen, J. van de Pol, I. Shaik, _Depth-Optimal Quantum Layout Synthesis as SAT_.  
In: Proc. 28th IC on Theory and Applications of Satisfiability Testing (SAT'25), Glasgow, Scotland, UK, 2025.

    @article{Jakobsen2025depthoptimal,
      author       = {Anna Blume Jakobsen, Anders Benjamin Clausen, Jaco van de Pol and Irfansha Shaik},
      title        = {Depth-Optimal Quantum Layout Synthesis as SAT},
      booktitle    = {28th IC on Theory and Applications of Satisfiability
                      Testing, {SAT} 2025, August 12-15, 2025, Glasgow, Scotland},
      series       = {LIPIcs},
      publisher    = {Schloss Dagstuhl - Leibniz-Zentrum f{\"{u}}r Informatik},
      year         = {2025}
    }

Depth-Optimal Synthesis was ported from [GitHub repository QuilLS](https://github.com/anbclausen/quills).

Please refer to this publication for Sub-Architectures (v4.0):

K. Milkevych, J. van de Pol, I. Shaik, _Practical Subarchitectures for Optimal Quantum Layout Synthesis_.  
In: arXiv [quant-ph] 2507.12976, 2025.
    
    @techreport{Kostyantin2025,
      title         = {Practical Subarchitectures for Optimal Quantum Layout Synthesis},
      author        = {Kostiantyn V. Milkevych and Jaco van de Pol and Irfansha Shaik},
      eprint        = {2507.12976},
      archivePrefix = {arXiv},
      primaryClass  = {quant-ph},
      year          = {2025}
    }


Please refer to this publication for CNOT-Optimal Clifford synthesis (v5.0):

I. Shaik, J. van de Pol, _CNOT-Optimal Clifford Synthesis as SAT_.
In: Proc. 28th IC on Theory and Applications of Satisfiability Testing (SAT'25), Glasgow, Scotland, UK, 2025.

    @article{shaikvdP2025cliffordsynthesis,
      author       = {Irfansha Shaik and Jaco van de Pol},
      title        = {CNOT-Optimal Clifford Synthesis as SAT},
      booktitle    = {28th IC on Theory and Applications of Satisfiability
                      Testing, {SAT} 2025, August 12-15, 2025, Glasgow, Scotland},
      series       = {LIPIcs},
      publisher    = {Schloss Dagstuhl - Leibniz-Zentrum f{\"{u}}r Informatik},
      year         = {2025}
    }

## Limitations

Q-Synth has some assumptions about the input circuits:

- The input should only contain unary gates and binary CNOT gates.
- We currently do not handle multiple quantum registers in the input circuit.

The scripts are tested on Linux and macOS.


## Copyright

(C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024, 2025

## Contributors

- Irfansha Shaik (Aarhus University, Kvantify)
- Jaco van de Pol (Aarhus University)
- Anna Blume Jakobsen (depth-optimal layout mapping)
- Anders B. Clausen (depth-optimal layout mapping)
- Kostiantyn Milkevych (subarchitectures, testing)
