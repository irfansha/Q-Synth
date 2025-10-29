#!/bin/bash

Path_to_benchmarks_without_permutations="../../Benchmarks/Random-Clifford/tket_optimized_without_swaps_no_u3_gates/"

Path_to_benchmarks_with_permutations="../../Benchmarks/Random-Clifford/tket_optimized_0cost_swaps/"

declare -a Metric_combinations_without_permutaions=(
   "--search_strategy forward --minimize cx-count -g"
   "--search_strategy backward --minimize cx-count"
   "--search_strategy forward --minimize cx-depth -g -r"
   "--search_strategy backward --minimize cx-depth"
)

declare -a Metric_combinations_with_permutaions=(
   "--search_strategy forward --minimize cx-count -q -g"
   "--search_strategy backward --minimize cx-count -q"
   "--search_strategy forward --minimize cx-depth -q -g"
   "--search_strategy backward --minimize cx-depth -q"
)


Random_clifford_instances="03q_05306.qasm  03q_33936.qasm  03q_50494.qasm  03q_55125.qasm  03q_99346.qasm
                           04q_05306.qasm  04q_33936.qasm  04q_50494.qasm  04q_55125.qasm  04q_99346.qasm
                           05q_05306.qasm  05q_33936.qasm  05q_50494.qasm  05q_55125.qasm  05q_99346.qasm
                           06q_05306.qasm  06q_33936.qasm  06q_50494.qasm  06q_55125.qasm  06q_99346.qasm
                           07q_05306.qasm  07q_33936.qasm  07q_50494.qasm  07q_55125.qasm  07q_99346.qasm"

echo "Experiment 1:"
echo "Random Clifford instances without permutation"
for metric_combination in "${Metric_combinations_without_permutaions[@]}"; do
  echo -e "\n\nExperiment 1 (without permutation) - ${metric_combination}"
  echo "======================================================================================================================="
  for file in ${Random_clifford_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py clifford --solver cd ${metric_combination} -t 10800 -v 0 $Path_to_benchmarks_without_permutations$file
  done
done

echo "Random Clifford instances with permutation"
for metric_combination in "${Metric_combinations_with_permutaions[@]}"; do
  echo -e "\n\nExperiment 1 (with permutation) - ${metric_combination}"
  echo "======================================================================================================================="
  for file in ${Random_clifford_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py clifford --solver cd ${metric_combination} -t 10800 -v 0 $Path_to_benchmarks_without_permutations$file
  done
done