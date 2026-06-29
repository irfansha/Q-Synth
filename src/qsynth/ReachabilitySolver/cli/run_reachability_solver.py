import argparse
import json
import os
import sys

from qsynth.ReachabilitySolver.encodings.cnot_rz_synthesis.cnot_rz_reachability_encoding import \
    CnotRzReachabilityEncoding
from qsynth.ReachabilitySolver.encodings.cnot_synthesis.cnot_reachability_encoding import CnotReachabilityEncoding
from qsynth.ReachabilitySolver.encodings.layout_synthesis.layout_reachability_encoding import \
    LayoutSynthesisReachabilityEncoding
from qsynth.ReachabilitySolver.api.encoding_spec import EncodingSpec
from qsynth.ReachabilitySolver.solvers.solver_extraction import get_solver_for_strategy


EXIT_NO_SOLUTION = 10


def get_encoding_from_path(encoding_path):
    with open(encoding_path) as f:
        encoding_spec = EncodingSpec(**json.load(f))

    encoding_type = encoding_spec.encoding_type
    payload = encoding_spec.payload

    if encoding_type == "cnot":
        encoding = CnotReachabilityEncoding.from_encoding_spec(payload)
    elif encoding_type == "cnot_rz":
        encoding = CnotRzReachabilityEncoding.from_encoding_spec(payload)
    elif encoding_type == "layout":
        encoding = LayoutSynthesisReachabilityEncoding.from_encoding_spec(payload)
    else:
        raise ValueError(f"Unknown encoding type: {encoding_spec.encoding_type}")

    return encoding


if __name__ == "__main__":
    text = "A wrapper for Reachability solvers"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--encoding_path", help="EncodingSpec input path")
    parser.add_argument("--result_path", help="MappingResult output path")
    parser.add_argument(
        "--strategy",
        help="solving strategy to use",
    )
    parser.add_argument("--minimize", help="Minimization target, either 'time_steps' or 'action_vars'")
    args = parser.parse_args()

    encoding = get_encoding_from_path(args.encoding_path)

    solver = get_solver_for_strategy(args.strategy, minimize=args.minimize, intermediate_solution_path=args.result_path)
    solution = solver.solve(encoding)
    if solution is None:
        sys.exit(EXIT_NO_SOLUTION)
    mapping_result = encoding.decode_reachability_solution(solution)

    # Make write atomic to avoid corrupted JSON on timeouts
    temporary_result_path = f"{args.result_path}.tmp"
    with open(temporary_result_path, "w") as f:
        f.write(mapping_result.to_json())
    os.replace(temporary_result_path, args.result_path)
