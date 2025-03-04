#!/usr/bin/env sh

Path_to_benchmarks="../../Benchmarks/SAT-24/Standard/"
Root="../../"
Python_file="env/bin/python"

declare -a Platforms=(
    "tenerife"
    "melbourne"
)

declare -a Subarch=(
    0
    1
)

declare -a Instances=(
    "or.qasm"
    "adder.qasm"
    "barenco_tof_4.qasm"
)

for platform in "${Platforms[@]}"; do

  echo -e "\n\nPlatform: "${platform}
  echo "============================"
  for file in ${Instances[@]}; do

      echo -e "Circuit: "$file
      echo "========"

      for sb in "${Subarch[@]}"; do

          echo "Using subarchitectues: "$sb
          echo "======"


          echo "SAT:"
          echo "===="
          "$Root$Python_file" "$Root/q-synth.py" layout -v0 -p $platform $Path_to_benchmarks$file --metric cx-count -m sat --subarch $sb
          echo "===="
          "$Root$Python_file" "$Root/q-synth.py" layout -v0 -p $platform $Path_to_benchmarks$file --metric cx-depth -m sat --subarch $sb
          echo "===="
          "$Root$Python_file" "$Root/q-synth.py" layout -v0 -p $platform $Path_to_benchmarks$file --metric depth -m sat --subarch $sb
          echo "===="

          echo "PLANNING:"
          echo "===="
          "$Root$Python_file" "$Root/q-synth.py" layout -v0 -p $platform $Path_to_benchmarks$file --metric cx-count -m global --subarch $sb
          echo "===="
          "$Root$Python_file" "$Root/q-synth.py" layout -v0 -p $platform $Path_to_benchmarks$file --metric cx-depth -m plan_cost_opt --subarch $sb
          echo "===="
          "$Root$Python_file" "$Root/q-synth.py" layout -v0 -p $platform $Path_to_benchmarks$file --metric depth -m plan_cost_opt --subarch $sb
          echo "===="
      done

  done
done
