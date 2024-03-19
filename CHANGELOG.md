# New Features in Q-Synth v2.0 (SAT based parallel plans)

- SAT Encoding: Parallel plans based SAT encoding for Optimal Layout Synthesis
- Bridges: bridge gates can be used along with SWAPs for better CNOT count (in SAT or planning)
- Relaxed Dependencies: supports gate commutation rules (in SAT or planning)
- CNOT Cancellation: Optional CNOT Cancellation before layout synthesis
- Experimental options: pre- and post-processing with circuit optimizations
- Experimental options: parallel swaps and/or bridges (near-optimal)

# Features in Q-Synth v1.0 (Classical Planning, ICCAD 2023)

- input OPENQASM 2.0 quantum circuit + Qiskit hardware platform
- output: mapped quantum circuit on platform, with optimal layout (minimum SWAPs)
- generates PDDL files, solved with e.g. Madagascar, FastDownward
- supports several PDDL encodings (global, local, lifted)
- support for ancillary qubits
