#!/bin/bash

Path_to_standard_benchmarks="../../Benchmarks/SAT/Standard/"
Path_to_vqe_benchmarks="../../Benchmarks/SAT/VQE/"

declare -a Bridge_Relaxed_configurations=(
           "0 0 S" # standard swaps (S), no bridges and no relaxed dependencies
           "1 0 SB" # Swaps + Bridges (SB), no relaxed dependencies
           "0 1 SR" # Swaps + relaxed dependencies (SR), no Bridges
           "1 1 SBR" # Swaps + Bridges + relaxed dependencies (SBR)
)

Standard_instances="or.qasm adder.qasm qaoa5.qasm 4mod5-v1_22.qasm mod5mils_65.qasm 4gt13_92.qasm
                    tof_4.qasm  barenco_tof_4.qasm tof_5.qasm mod_mult_55.qasm barenco_tof_5.qasm
                    vbe_adder_3.qasm rc_adder_6.qasm"
VQE_instances="vqe_8_1_5_100.qasm vqe_8_4_5_100.qasm vqe_8_3_5_100.qasm vqe_8_1_10_100.qasm vqe_8_2_5_100.qasm
               vqe_8_0_5_100.qasm vqe_8_0_10_100.qasm vqe_8_4_10_100.qasm vqe_8_3_10_100.qasm vqe_8_2_10_100.qasm"

echo "Experiment 3:"
echo "Standard instances"
for bridge_relaxed_configuration in "${Bridge_Relaxed_configurations[@]}"; do
  read -a brconf <<< "$bridge_relaxed_configuration"
  echo -e "\n\nExperiment 3 - Configuration "${brconf[2]}
  echo "======================================================================================================================="
  for file in ${Standard_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py --bridge ${brconf[1]} -r ${brconf[0]} -m sat -p melbourne -s cd15 -v1 -t 600 $Path_to_standard_benchmarks$file
  done
done
echo "VQE instances"
for bridge_relaxed_configuration in "${Bridge_Relaxed_configurations[@]}"; do
  read -a brconf <<< "$bridge_relaxed_configuration"
  echo -e "\n\nExperiment 3 - Configuration "${brconf[2]}
  echo "======================================================================================================================="
  for file in ${VQE_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py --bridge ${brconf[1]} -r ${brconf[0]} -m sat -p melbourne -s cd15 -v1 -t 600 $Path_to_vqe_benchmarks$file
  done
done