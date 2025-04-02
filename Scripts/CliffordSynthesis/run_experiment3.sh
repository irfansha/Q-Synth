#!/bin/bash

declare -a Metric_combinations=(
   "--minimize gates -g -d"
   "--minimize depth -g -r -d"
)

declare -a Platform_name_and_option=(
   "/sycamore-54 sycamore"
   "/rigetti-80 rigetti-80"
   "/eagle-127 eagle"
)

VQE_mapped_instances="pennylane_8q_50o_0.qasm  pennylane_8q_50o_1.qasm  pennylane_16q_100o_0.qasm  pennylane_16q_100o_1.qasm
                        simple_8q_50o_0.qasm  simple_8q_50o_1.qasm  simple_16q_100o_0.qasm  simple_16q_100o_1.qasm
                        yardanov_8q_50o_0.qasm  yardanov_8q_50o_1.qasm  yardanov_16q_100o_0.qasm  yardanov_16q_100o_1.qasm"

echo "Experiment 3: VQE mapped instances"
for platform_name_and_option in "${Platform_name_and_option[@]}"; do
  read -a platformop <<< "$platform_name_and_option"
  echo "Platform name and relevant option: ${platformop}"
  echo "======================================================================================================================="
  for metric_combination in "${Metric_combinations[@]}"; do
    echo -e "Metric combination - ${metric_combination}"
    for file in ${VQE_mapped_instances}; do
      echo -e "\nCircuit: "$file
      ../../q-synth.py clifford ${metric_combination} -t 600 -v 0 ../../Benchmarks/VQE/mapped${platformop[0]}/$file -p ${platformop[1]}
    done
  done
done

Feynman_mapped_instances="barenco_tof_3.qasm tof_3.qasm qft_4.qasm mod5_4.qasm hwb6.qasm barenco_tof_4.qasm tof_4.qasm
                          barenco_tof_5.qasm mod_mult_55.qasm tof_5.qasm grover_5.qasm vbe_adder_3.qasm fprenorm.qasm
                          mod_red_21.qasm gf2^4_mult.qasm rc_adder_6.qasm csla_mux_3.qasm gf2^5_mult.qasm
                          ham15-med.qasm ham15-low.qasm gf2^6_mult.qasm barenco_tof_10.qasm tof_10.qasm ham15-high.qasm
                          gf2^7_mult.qasm qcla_com_7.qasm adder_8.qasm gf2^8_mult.qasm"

echo "Experiment 3: Feynman mapped instances"
for platform_name_and_option in "${Platform_name_and_option[@]}"; do
  read -a platformop <<< "$platform_name_and_option"
  echo "Platform name and relevant option: ${platformop}"
  echo "======================================================================================================================="
  for metric_combination in "${Metric_combinations[@]}"; do
    echo -e "Metric combination - ${metric_combination}"
    for file in ${Feynman_mapped_instances}; do
      echo -e "\nCircuit: "$file
      ../../q-synth.py clifford ${metric_combination} -t 600 -v 0 ../../Benchmarks/Feynman/mapped${platformop[0]}/$file -p ${platformop[1]}
    done
  done
done