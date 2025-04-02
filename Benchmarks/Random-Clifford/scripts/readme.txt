For installation use :

    python3 -m venv clifford_venv
    source clifford_venv/bin/activate
    pip install -r requirements.txt


For Benchmark reproduction, use following commands in "Random-Clifford/scripts/" folder:

  For stabilizer generation:

    python3 generate_random_clifford_circuits_qiskit.py -n 5 --num_iterations 5 --out_folder ../stabilizers
    python3 generate_random_clifford_circuits_qiskit.py -n 6 --num_iterations 5 --out_folder ../stabilizers
    python3 generate_random_clifford_circuits_qiskit.py -n 7 --num_iterations 5 --out_folder ../stabilizers

  For optimized benchmarks with premutations:

    python3 generate_random_clifford_circuits_qiskit.py -n 5 --num_iterations 5 --out_folder ../tket_optimized_0cost_swaps/ --synthesize_optimize --allow_swaps
    python3 generate_random_clifford_circuits_qiskit.py -n 6 --num_iterations 5 --out_folder ../tket_optimized_0cost_swaps/ --synthesize_optimize --allow_swaps
    python3 generate_random_clifford_circuits_qiskit.py -n 7 --num_iterations 5 --out_folder ../tket_optimized_0cost_swaps/ --synthesize_optimize --allow_swaps

  For optimized benchmarks without premutations:

    python3 generate_random_clifford_circuits_qiskit.py -n 5 --num_iterations 5 --out_folder ../tket_optimized_without_swaps/ --synthesize_optimize
    python3 generate_random_clifford_circuits_qiskit.py -n 6 --num_iterations 5 --out_folder ../tket_optimized_without_swaps/ --synthesize_optimize
    python3 generate_random_clifford_circuits_qiskit.py -n 7 --num_iterations 5 --out_folder ../tket_optimized_without_swaps/ --synthesize_optimize