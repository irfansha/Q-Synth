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
TMP="tmp_qsynth_full.out"

# Create file to store parsed output
OUTPUT="data_qsynth_circuits_full.csv"
touch "$OUTPUT"

# Write header to output file
echo "Circuit,Platform,Ancillaries,Allow Subarchitectures,Maximal Subarchitectures, Time(s), Swaps" >> "$OUTPUT"

# For each platform:
echo "Running Q-Synth circuits with 0 ancillaries"
for platform in ${PLATFORMS[@]}; do

    for circuit in $(ls "$qsynth_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 0 -a0 --platform $platform "$qsynth_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$qsynth_circuits/$circuit,$platform,INF,False,N/A,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.0.out"
            python util/parse.py "raw/$circuit.$platform.0.out" "$OUTPUT"
        fi

    done

done

echo "Running Q-Synth circuits with infinite ancillaries"
for platform in ${PLATFORMS[@]}; do

    for circuit in $(ls "$qsynth_circuits/"); do

        echo "Running configurations for $circuit on $platform"

        timeout "${TIMEOUT}s" python "$QSROOT/q-synth.py" layout --time $TIMEOUT -m sat --subarch 0 -a-1 --platform $platform "$qsynth_circuits/$circuit" &> "$TMP"
        exit_status=$?
        if [[ $exit_status -eq 124 ]]; then
            echo "Timeout of $TIMEOUT seconds elapsed"
            echo "$qsynth_circuits/$circuit,$platform,INF,False,N/A,TO,TO" >> "$OUTPUT"
        else
            mv "$TMP" "raw/$circuit.$platform.0.out"
            python util/parse.py "raw/$circuit.$platform.0.out" "$OUTPUT"
        fi

    done

done
