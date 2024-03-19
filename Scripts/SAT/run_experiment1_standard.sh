#!/bin/bash

Path_to_benchmarks="../../Benchmarks/SAT/Standard/"

declare -a Platforms=(
           "sycamore"
           "rigetti-80"
           "eagle"
)

Standard_instances="or.qasm adder.qasm qaoa5.qasm 4mod5-v1_22.qasm mod5mils_65.qasm 4gt13_92.qasm
                    tof_4.qasm  barenco_tof_4.qasm qft_8.qasm tof_5.qasm mod_mult_55.qasm barenco_tof_5.qasm
                    vbe_adder_3.qasm rc_adder_6.qasm ising_model_10.qasm
                    16QBT_05CYC_TFL_0.qasm 16QBT_10CYC_TFL_0.qasm 16QBT_15CYC_TFL_0.qasm
                    16QBT_20CYC_TFL_0.qasm 16QBT_30CYC_TFL_0.qasm 16QBT_35CYC_TFL_0.qasm
                    54QBT_05CYC_QSE_0.qasm 54QBT_25CYC_QSE_0.qasm"

echo "Experiment 1:"
echo "Standard instances"
for platform in "${Platforms[@]}"; do
  echo -e "\n\nExperiment 1 - Platform: "${platform}
  echo "======================================================================================================================="
  for file in ${Standard_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py -m sat -p $platform -s cd15 -v1 -t 10800 $Path_to_benchmarks$file
  done
done


