#!/bin/bash

Path_to_benchmarks="../../Benchmarks/ECAI-24/tpar-optimized/"

Tpar_instances="barenco_tof_3.qasm  barenco_tof_4.qasm  barenco_tof_5.qasm  mod5_4.qasm mod_mult_55.qasm
                    qft_4.qasm  rc_adder_6.qasm tof_3.qasm  tof_4.qasm  tof_5.qasm  vbe_adder_3.qasm"

echo "Experiment 1:"
echo "Tpar optimized instances"
for file in ${Tpar_instances}; do
  echo -e "\nCircuit: "$file
  ../../q-synth.py cnot -m planning -s fd-ms --minimize gates -t 600 -v 0 --only_write_pddl_files $Path_to_benchmarks$file
done
