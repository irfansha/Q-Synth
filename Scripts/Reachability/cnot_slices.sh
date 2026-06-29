#!/bin/bash

path_to_benchmarks="../../Benchmarks/CNOT-slices/"

strategies="forward backward k-step inc going-down from-middle atmost binary maxsat"

tpar_instances="barenco_tof_3 barenco_tof_4  barenco_tof_5  mod5_4 mod_mult_55
                    qft_4  rc_adder_6 tof_3  tof_4  tof_5  vbe_adder_3"

echo "CNOT synthesis on slices from standard tpar optimized benchmarks:"
for strategy in ${strategies}; do
  echo -e "\n\nStrategy: "${strategy} "\nMetric: cx-count"
  echo "======================================================================================================================="
  for benchmark in ${tpar_instances}; do
    echo -e "\nCircuit: "$benchmark""
    echo -e "========================================\n\n"
    for slice in "$path_to_benchmarks$benchmark"/*; do
      ../../q-synth.py cnot --search_strategy $strategy --minimize cx-count -d -t 600 -v 0 $slice
      echo -e "\n"
    done
  done
done
