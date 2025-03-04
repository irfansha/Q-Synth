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
qsynth_circuits="circuits/qsynth"

# Create directory to hold temporary results
RES="raw/"
mkdir "$RES"

# File to hold temporary output
TMP="tmp_qsynth_sub.out"

# Create file to store parsed output
OUTPUT="data_qsynth_circuits_subarch.csv"
touch "$OUTPUT"

# Write header to output file
echo "Circuit,Platform,Ancillaries,Allow Subarchitectures,Maximal Subarchitectures, Time(s), Swaps" >> "$OUTPUT"

echo "Running Q-Synth circuits with 0 ancillaries"
for platform in ${PLATFORMS[@]}; do

    for circuit in $(ls "$qsynth_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 1 -a0 --platform $platform "$qsynth_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$qsynth_circuits/$circuit,$platform,0,True,TO,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.sub0.out"
            python util/parse.py "raw/$circuit.$platform.sub0.out" "$OUTPUT"
        fi

    done

done

echo "Running Q-Synth circuits with 1 ancillaries"
for platform in ${PLATFORMS[@]}; do
    for circuit in $(ls "$qsynth_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 1 -a1 --platform $platform "$qsynth_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$qsynth_circuits/$circuit,$platform,1,True,TO,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.sub1.out"
            python util/parse.py "raw/$circuit.$platform.sub1.out" "$OUTPUT"
        fi

    done

done


echo "Running Q-Synth circuits with 2 ancillaries"
for platform in ${PLATFORMS[@]}; do
    for circuit in $(ls "$qsynth_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 1 -a2 --platform $platform "$qsynth_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$qsynth_circuits/$circuit,$platform,2,True,TO,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.sub2.out"
            python util/parse.py "raw/$circuit.$platform.sub2.out" "$OUTPUT"
        fi

    done

done
