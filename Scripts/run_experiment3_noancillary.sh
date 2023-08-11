#!/bin/bash

Path_to_benchmarks="../Benchmarks/"

declare -a Model_Solver_combinations=(
           "local fd-bjolp"
           "local fd-ms"
           "local M-seq-optimal"
           "global fd-bjolp"
)
Melbourne_instances="or.qasm adder.qasm qaoa5.qasm 4mod5-v1_22.qasm mod5mils_65.qasm 4gt13_92.qasm tof_4.qasm barenco_tof_4.qasm tof_5.qasm mod_mult_55.qasm barenco_tof_5.qasm vbe_adder_3.qasm rc_adder_6.qasm"

echo -e "\nExperiment 3:"
echo "Without ancillary, local model, solver fd-bjolp"
echo "======================================================================================================================="
ancillary="0"
for file in ${Melbourne_instances}; do
  echo -e "\nCircuit: "$file
  ../q-synth.py -a$ancillary -b1 -p melbourne -m local -s fd-bjolp --run 2 -t 1800 -v1 $Path_to_benchmarks$file
done
