#!/bin/bash

declare -a Metric_combinations=(
   "--minimize cx-count -g -d"
   "--minimize cx-depth -g -r -d"
)

declare -a VQE_benchmark_path_and_enabling_permutation=(
   "../../Benchmarks/VQE/original/"
   "-q ../../Benchmarks/VQE/original/"
   "../../Benchmarks/VQE/tket_optimized_without_swaps/"
   "-q ../../Benchmarks/VQE/tket_optimized_0cost_swaps/"
)

VQE_unmapped_instances="pennylane_8q_50o_0.qasm  pennylane_8q_50o_1.qasm  pennylane_16q_100o_0.qasm  pennylane_16q_100o_1.qasm
                        simple_8q_50o_0.qasm  simple_8q_50o_1.qasm  simple_16q_100o_0.qasm  simple_16q_100o_1.qasm
                        yardanov_8q_50o_0.qasm  yardanov_8q_50o_1.qasm  yardanov_16q_100o_0.qasm  yardanov_16q_100o_1.qasm"

echo "Experiment 2: VQE unmapped instances"
for benchmark_and_permutation in "${VQE_benchmark_path_and_enabling_permutation[@]}"; do
  echo "Benchmark path and permutation option: ${benchmark_and_permutation}"
  echo "======================================================================================================================="
  for metric_combination in "${Metric_combinations[@]}"; do
    echo -e "Metric combination - ${metric_combination}"
    for file in ${VQE_unmapped_instances}; do
      echo -e "\nCircuit: "$file
      ../../q-synth.py clifford --solver cd ${metric_combination} -t 600 -v 0 $benchmark_and_permutation$file
    done
  done
done

declare -a Feynman_benchmark_path_and_enabling_permutation=(
   "../../Benchmarks/Feynman/state_phase_folded/"
   "-q ../../Benchmarks/Feynman/state_phase_folded/"
   "../../Benchmarks/Feynman/tket_optimized_without_swaps/"
   "-q ../../Benchmarks/Feynman/tket_optimized_0cost_swaps/"
)

Feynman_unmapped_instances="tof_3.qasm barenco_tof_3.qasm mod5_4.qasm qft_4.qasm tof_4.qasm barenco_tof_4.qasm hwb6.qasm
                            mod_mult_55.qasm tof_5.qasm barenco_tof_5.qasm grover_5.qasm vbe_adder_3.qasm fprenorm.qasm
                            mod_red_21.qasm gf2^4_mult.qasm rc_adder_6.qasm csla_mux_3.qasm gf2^5_mult.qasm
                            ham15-low.qasm ham15-med.qasm gf2^6_mult.qasm tof_10.qasm barenco_tof_10.qasm ham15-high.qasm
                            gf2^7_mult.qasm qcla_com_7.qasm adder_8.qasm gf2^8_mult.qasm"

echo "Experiment 2: Feynman unmapped instances"
for benchmark_and_permutation in "${Feynman_benchmark_path_and_enabling_permutation[@]}"; do
  echo "Benchmark path and permutation option: ${benchmark_and_permutation}"
  echo "======================================================================================================================="
  for metric_combination in "${Metric_combinations[@]}"; do
    echo -e "Metric combination - ${metric_combination}"
    for file in ${Feynman_unmapped_instances}; do
      echo -e "\nCircuit: "$file
      ../../q-synth.py clifford --solver cd ${metric_combination} -t 600 -v 0 $benchmark_and_permutation$file
    done
  done
done
