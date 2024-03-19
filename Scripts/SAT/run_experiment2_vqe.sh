#!/bin/bash

Path_to_benchmarks="../../Benchmarks/SAT/VQE/"

declare -a Platforms=(
           "sycamore"
           "rigetti-80"
           "eagle"
)

VQE_instances="vqe_8_1_5_100.qasm vqe_8_4_5_100.qasm vqe_8_3_5_100.qasm vqe_8_1_10_100.qasm vqe_8_2_5_100.qasm
               vqe_8_0_5_100.qasm vqe_8_0_10_100.qasm vqe_8_4_10_100.qasm vqe_8_3_10_100.qasm vqe_8_2_10_100.qasm"

echo "Experiment 2:"
echo "VQE instances"
for platform in "${Platforms[@]}"; do
  echo -e "\n\nExperiment 2 - Platform: "${platform}
  echo "======================================================================================================================="
  for file in ${VQE_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py -m sat -p $platform -s cd15 -v1 -t 10800 $Path_to_benchmarks$file
  done
done