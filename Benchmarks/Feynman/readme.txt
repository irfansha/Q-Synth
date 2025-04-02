Benchmarks from Feynman
URL: https://github.com/meamy/feynman
Commit : 8e7aeb70235eeaf808eaf6172dff1a19b1d49242


Installed using commands:

	cabal configure
	cabal build
	cabal install

Benchmarks used from : https://github.com/meamy/feynman/tree/master/benchmarks/qc

Chose all benchmarks with <=25 qubits and T-gate count < 5000.
Feynman can take a lot of time for harder instances for optimization.

We generated a benchmark set with statefold and phasefold for T-gate reduction i.e., with options `-statefold -phasefold`

We translate .qc files to .qasm files using `qc2qasm` script in the Feynman tool.
Unfortunately, the output files contain a high level single gate with implements the full circuit.
We remove such a gate and replace with standard gates on q register as in openqasm 2.0 format.
This transformation can be done by the following command:

	python3 standardize_qasm.py --circuit $file

The script for `standardize_qasm` is available in the current folder.

In total 28 instances are generated for each optimization setting.

For mapped benchmakrs:

We first optimized (state_phase_folded circuits) by allowing 0-cost swaps and dropped the swap resulting in some output permutation.
Then for each instance we mapped to eagle, rigetti, and sycamore using qiskit with O3 level optimization.
