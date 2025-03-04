# Features in Q-Synth v4.0 (Sub-architecture based layout synthesis and Depth-Optimal layout synthesis)

- Layout synthesis using sub-architectures
- Depth-optimal layout synthesis for optimizing for depth, cx-depth as well as cx-depth-cx-count and depth-cx-count

# Features in Q-Synth v3.0 (Layout aware CNOT synthesis with permutation using Planning, SAT, and QBF, ECAI 2024)

- Four CNOT Synthesis variations with layout restrictions and qubit permutation: S, W, S+R, and W+R
- Selected variant encodings in Planning, SAT and QBF
- Minimization of either CNOT count or CNOT depth
- Peephole optimization for arbitrary (Non-CNOT) circuits via slicing for S, W, and S+R variants

# Features in Q-Synth v2.0 (Layout synthesis with SAT based parallel plans with incremental solving, SAT 2024)

- SAT Encoding: Parallel plans based SAT encoding for Optimal Layout Synthesis
- Bridges: bridge gates can be used along with SWAPs for better CNOT count (in SAT or planning)
- Relaxed Dependencies: supports gate commutation rules (in SAT or planning)
- CNOT Cancellation: Optional CNOT Cancellation before layout synthesis
- Experimental options: pre- and post-processing with circuit optimizations
- Experimental options: parallel swaps and/or bridges (near-optimal)

# Features in Q-Synth v1.0 (Layout synthesis based on Classical Planning, ICCAD 2023)

- input OPENQASM 2.0 quantum circuit + Qiskit hardware platform
- output: mapped quantum circuit on platform, with optimal layout (minimum SWAPs)
- generates PDDL files, solved with e.g. Madagascar, FastDownward
- supports several PDDL encodings (global, local, lifted)
- support for ancillary qubits
