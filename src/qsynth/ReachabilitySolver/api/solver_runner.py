import json
import os
import subprocess
import sys
import traceback
from dataclasses import asdict
from pathlib import Path

from qiskit import QuantumCircuit

from qsynth.ReachabilitySolver.api.encoding_spec import EncodingSpec
from qsynth.ReachabilitySolver.cli.run_reachability_solver import EXIT_NO_SOLUTION
from qsynth.Utilities.result import MappingResult


def run_reachability_solver_with_timeout(
        circuit: QuantumCircuit,
        encoding_spec: EncodingSpec,
        strategy: str,
        timeout: float,
        intermediate_files_path: str | Path,
        minimize: str = "time_steps",
):
    encoding_path = f"{intermediate_files_path}/encoding.json"

    with open(encoding_path, "w") as f:
        json.dump(asdict(encoding_spec), f)

    this_file_path = os.path.abspath(__file__)
    run_reachability_solver_path = Path(this_file_path).parent.parent / "cli" / "run_reachability_solver.py"
    result_path = f"{intermediate_files_path}/result.json"
    # Remove any preexisting file on result file path
    if os.path.exists(result_path):
        os.remove(result_path)

    # Run the reachability solver using the same Python interpreter to avoid mismatches
    cmd_args = [sys.executable, str(run_reachability_solver_path),
                "--encoding_path", encoding_path,
                "--result_path", result_path,
                "--strategy", strategy,
                "--minimize", minimize]

    try:
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        # Print solver output
        if result.stdout:
            print(result.stdout)
        if result.returncode == EXIT_NO_SOLUTION:
            # No solution is found
            return MappingResult(circuit=circuit, no_plan_found=True)
        elif result.returncode != 0:
            print(f"Reachability solver exited with non-zero return code: {result.returncode}")
            print(result.stderr)
    except subprocess.TimeoutExpired as e:
        if e.stdout:
            print(e.stdout.decode())
        # If any intermediate solution exists, return it
        if os.path.exists(result_path):
            with open(result_path, "r") as f:
                circuit = MappingResult.from_json(f.read()).circuit
        return MappingResult(circuit=circuit, timed_out=True)
    except Exception as e:
        # Catch other exceptions from subprocess.run
        print(f"Error while running reachability solver: {e}")
        traceback.print_exc()

    # Only attempt to read the solution if the solver completed and actually created the file
    mapping_result = None
    if not os.path.exists(result_path):
        raise FileNotFoundError(f"{result_path} does not exist")
    with open(result_path, "r") as f:
        mapping_result = MappingResult.from_json(f.read())

    return mapping_result
