#!/usr/bin/env python3

import csv
import sys
import re

args = sys.argv[1:]
file = args[0]
out = args[1]


def parse_output(txt):
    # Time limits are not enforced

    # Patterns to use for matching
    circuit_p = r"circuit_in\s+(\S+)"
    platform_p = r"platform\s+(\S+)"
    ancillas_p = r"ancillas\s+(\S+)"

    enc_solve_p = r"Encoding\+Solving time: (\d+\.\d+)"
    swaps_p = r"Number of additional swaps: (\d+)"
    extraction_p = r"Extraction time: (\d+\.\d+)"
    no_sol_p = r"No solution"

    using_subarch_p = r"Using subarchitectures"
    subarch_count_p = r"Selected (\d+) maximal subarchitectures from (\d+) candidates"
    # subarch_comp_p = r"Subarchitecture computation done in (\d+\.\d+)s"
    subarch_total_p = r"(\d+\.\d+)s elapsed\."
    subarch_best_p = r"Best solution has (\d+) swaps and \d+ cx-depth\."
    subarch_no_mapping_p = r"Mapping could not be found\."

    # Try matching patterns
    circuit_match = re.search(circuit_p, txt)
    platform_match = re.search(platform_p, txt)
    ancillas_match = re.search(ancillas_p, txt)

    enc_solve_match = re.search(enc_solve_p, txt)
    swaps_match = re.search(swaps_p, txt)
    extraction_match = re.search(extraction_p, txt)
    no_solution_match = re.search(no_sol_p, txt)

    using_subarchitectures_match = re.search(using_subarch_p, txt)
    subarch_count_match = re.search(subarch_count_p, txt)
    subarch_total_match = re.search(subarch_total_p, txt)
    subarch_best_match = re.search(subarch_best_p, txt)
    subarch_no_mapping_match = re.search(subarch_no_mapping_p, txt)

    row = ["ERROR"] * 7  # circuit, platform, ancillas, subarch, subarchs, time, swaps
    if circuit_match:
        row[0] = circuit_match.group(1)  # circuit

    if platform_match:
        row[1] = platform_match.group(1)  # platform

    if ancillas_match:
        if ancillas_match.group(1) == "-1":
            row[2] = "INF"
        else:
            row[2] = ancillas_match.group(1)

    if using_subarchitectures_match:
        # Using subarchitectures
        row[3] = True

        if subarch_count_match:
            row[4] = subarch_count_match.group(1)

        if subarch_total_match:
            row[5] = subarch_total_match.group(1)

        if subarch_best_match:
            row[6] = subarch_best_match.group(1)

        if subarch_no_mapping_match or no_solution_match:
            row[5] = "N/A"
            row[6] = "N/A"
    else:
        # Not using subarchitectures
        row[3] = False
        row[4] = "N/A"

        if enc_solve_match and extraction_match:
            time = 0.0
            time += float(enc_solve_match.group(1))
            time += float(extraction_match.group(1))
            row[5] = time

        if swaps_match:
            row[6] = swaps_match.group(1)

        if no_solution_match:
            row[5] = "N/A"
            row[6] = "N/A"

    return row


# Optional header
header = [
    "Circuit",
    "Platform",
    "Ancillaries",
    "Allow Subarchitectures",
    "Maximal Subarchitectures",
    "Time (s)",
    "Swaps",
]

# Parse data rows from file
rows = []
with open(file, "r") as f:
    lines = "\n".join(f.readlines())
    rows.append(parse_output(lines))


# Write rows
with open(out, "a", newline="") as csvfile:
    writer = csv.writer(
        csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    # writer.writerow(header)
    writer.writerows(rows)
