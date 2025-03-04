#!/usr/bin/env sh
# set -x

trap 'exit 130' INT

PLATFORMS=(
    guadalupe
    rigetti-16
    tokyo
    sycamore
    rigetti-80
    eagle
)

TIMEOUT=10800

# Location of Q-Synth executables
QSROOT="../.."

# Location of circuit files
mqt_circuits="circuits/mqt"

# Create directory to hold temporary results
RES="raw/"
mkdir "$RES"

# File to hold temporary output
TMP="tmp_mqt_full.out"

# Create file to store parsed output
OUTPUT="data_mqt_circuits_full.csv"
touch "$OUTPUT"

# Write header to output file
echo "Circuit,Platform,Ancillaries,Allow Subarchitectures,Maximal Subarchitectures, Time(s), Swaps" >> "$OUTPUT"

echo "Running MQT circuits with 0 ancillaries"
for platform in ${PLATFORMS[@]}; do

    for circuit in $(ls "$mqt_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 0 -a0 --platform $platform "$mqt_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$mqt_circuits/$circuit,$platform,0,False,N/A,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.0.out"
            python util/parse.py "raw/$circuit.$platform.0.out" "$OUTPUT"
        fi

    done

done

echo "Running MQT circuits with infinite ancillaries"
for platform in ${PLATFORMS[@]}; do

    for circuit in $(ls "$mqt_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 0 -a-1 --platform $platform "$mqt_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$mqt_circuits/$circuit,$platform,INF,False,N/A,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.inf.out"
            python util/parse.py "raw/$circuit.$platform.inf.out" "$OUTPUT"
        fi


    done


done
