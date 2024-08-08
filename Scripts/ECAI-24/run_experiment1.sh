#!/bin/bash

Path_to_benchmarks="../../Benchmarks/ECAI-24/tpar-optimized/"

declare -a Model_Solver_metric_combinations=(
   "planning fd-ms gates"
   "qbf caqe gates"
   "qbf caqe depth"
   "sat cd gates"
   "sat cd depth"
)

Tpar_instances="barenco_tof_3.qasm  barenco_tof_4.qasm  barenco_tof_5.qasm  mod5_4.qasm mod_mult_55.qasm
                    qft_4.qasm  rc_adder_6.qasm tof_3.qasm  tof_4.qasm  tof_5.qasm  vbe_adder_3.qasm"

echo "Experiment 1:"
echo "Tpar optimized instances"
for model_solver_metric_combination in "${Model_Solver_metric_combinations[@]}"; do
  read -a mscomb <<< "$model_solver_metric_combination"
  echo -e "\n\nExperiment 1 - Model: "${mscomb[0]} "Solver: "${mscomb[1]} "Minimize: "${mscomb[2]}
  echo "======================================================================================================================="
  for file in ${Tpar_instances}; do
    echo -e "\nCircuit: "$file
    ../../q-synth.py cnot -m ${mscomb[0]} -s ${mscomb[1]} --minimize ${mscomb[2]} -t 600 -v 0 $Path_to_benchmarks$file
  done
done

read -a mscomb <<< "sat cd gates -q"
echo -e "\n\nExperiment 1 - Model: sat Solver: cd Minimize: gates with qubit permute"
echo "======================================================================================================================="
for file in ${Tpar_instances}; do
  echo -e "\nCircuit: "$file
  ../../q-synth.py cnot -q -m sat -s cd --minimize gates -t 600 -v 0 $Path_to_benchmarks$file
done

read -a mscomb <<< "sat cd depth -q"
echo -e "\n\nExperiment 1 - Model: sat Solver: cd Minimize: depth with qubit permute"
echo "======================================================================================================================="
for file in ${Tpar_instances}; do
  echo -e "\nCircuit: "$file
  ../../q-synth.py cnot -q -m sat -s cd --minimize depth -t 600 -v 0 $Path_to_benchmarks$file
done
