#!/bin/bash

Path_to_benchmarks="../../Benchmarks/Planning/"

declare -a Model_Solver_combinations=(
           "local fd-bjolp"
           "local fd-ms"
           "local M-seq-optimal"
           "global fd-bjolp"
)
Tenerife_instances="or.qasm adder.qasm qaoa5.qasm 4mod5-v1_22.qasm mod5mils_65.qasm 4gt13_92.qasm"

echo "Experiment 1:"
echo "Tenerife instances"
ancillary="1"
for model_solver_combination in "${Model_Solver_combinations[@]}"; do
  read -a mscomb <<< "$model_solver_combination"
  echo -e "\n\nExperiment 1 - Model: "${mscomb[0]} "Solver: "${mscomb[1]}
  echo "======================================================================================================================="
  for file in ${Tenerife_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py -a$ancillary -b1 -p tenerife -m ${mscomb[0]} -s ${mscomb[1]} --run 2 -t 1800 -v1 $Path_to_benchmarks$file
  done
done
