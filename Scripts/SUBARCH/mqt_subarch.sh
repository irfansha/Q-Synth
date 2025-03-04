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
TMP="tmp_mqt_sub.out"

# Create file to store parsed output
OUTPUT="data_mqt_circuits_subarch.csv"
touch "$OUTPUT"

# Write header to output file
echo "Circuit,Platform,Ancillaries,Allow Subarchitectures,Maximal Subarchitectures, Time(s), Swaps" >> "$OUTPUT"

# Run with 0 ancillaries
echo "Running MQT circuits with 0 ancillaries"
for platform in ${PLATFORMS[@]}; do

    for circuit in $(ls "$mqt_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        # Run with subarchitectures and 0 ancillaries
        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 1 -a0 --platform $platform "$mqt_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$mqt_circuits/$circuit,$platform,0,True,TO,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.sub0.out"
            python util/parse.py "raw/$circuit.$platform.sub0.out" "$OUTPUT"
        fi

    done

done

# Run with 1 ancillaries
echo "Running MQT circuits with 1 ancillary"
for platform in ${PLATFORMS[@]}; do

    for circuit in $(ls "$mqt_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 1 -a1 --platform $platform "$mqt_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$mqt_circuits/$circuit,$platform,1,True,TO,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.sub1.out"
            python util/parse.py "raw/$circuit.$platform.sub1.out" "$OUTPUT"
        fi

    done

done
