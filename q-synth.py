#! /usr/bin/env python3

# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024, 2025, 2026

import argparse
import datetime
import subprocess
import textwrap
from qiskit import QuantumCircuit, qasm2

from qsynth import layout_synthesis, get_coupling_graph
from qsynth.api import cnot_peephole_synthesis, cnot_rz_peephole_synthesis, clifford_peephole_synthesis
from qsynth.layout_config import MODELS, METRICS, SOLVERS


def configure_layout_parser(layout_parser):
    layout_parser.add_argument(
        "-p",
        "--platform",
        help=textwrap.dedent(
            """\
                               Either provider name:
                                 tenerife  = FakeTenerife/IBM QX2, 5 qubit
                                 melbourne = FakeMelbourne, 14 qubit (default)
                                 tokyo     = FakeTokyo, 20 qubit
                               Or generated platforms:
                                 rigetti-{8,12,14,16} = various subgraphs of the rigetti platform
                                 sycamore  = google sycamore platform with grid like topology - 54 qubits
                                 line-<n>  = linear platform of <n> qubits (good for testing use of ancilla qubits)
                                 cycle-<n> = cycle of <n> qubits (good for testing use of ancilla qubits)
                                 star-<n>  = center qubit + <n>-legged star (need swaps before first cnot)
                                 grid-<n>  = <n> x <n> grid (standard platforms for experiments)
                                 test      = test platform (can be anything for experimentation)
                               """
        ),
        default="melbourne",
    )
    layout_parser.add_argument(
        "-b",
        "--bidirectional",
        type=int,
        help="Make coupling bidirectional [0/1]: 0=no, 1=yes (default)",
        default=1,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "-m",
        "--model",
        help=textwrap.dedent(
            """\
                               Model type used for the encoding:
                                 sat = uses the sat encoding (default)
                                 planning = uses the default planner (depending on the metric)
                               For count-metrics, the following planning models are supported:
                                 local  = local dependencies, grounded model (default for planning/count)
                                 global = uses global levels to ensure dependencies (with separate initial mapping)
                                 lifted = lifted, non-grounded local model
                               For depth-metrics, the following planning models are supported:
                                 cost_opt = cost-based optimal planning model (default for planning/depth)
                                 cond_cost_opt = conditional cost-based optimal planning model
                                 lc_incr = local, clock-incremental planning model"""
        ),
        default="sat",
        choices=MODELS,
    )
    layout_parser.add_argument(
        "-a",
        "--ancillas",
        type=int,
        help="Max number of ancilla qubits allowed: -1 (default) unlimited; 0,1,2,...: specify max (*)",
        default=-1,
    )
    layout_parser.add_argument(
        "-r",
        "--relaxed",
        type=int,
        help="Use relaxed dependencies [0/1]: 0=strict (default), 1=relaxed dependencies",
        default=0,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "-c",
        "--cnot_cancel",
        type=int,
        help="Cancel CNOT gates [0/1]: 0=no (default), 1=cancel",
        default=0,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "--bridge",
        type=int,
        help="Use bridge gates [0/1]: 0=no (default), 1=with bridges",
        default=0,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "-s",
        "--solver",
        help=textwrap.dedent(
            """\
                               Either a planner tool combination (with --model=planning):
                                 fd-bjolp (default), fd-ms, madagascar, etc (1)
                               Or a SAT solver from PySAT (with --model=sat):
                                 cd19 = cadical195 (default), g42 = glucose42, etc. (2)
                                 """
        ),
    )
    layout_parser.add_argument(
        "--swap_upper_bound",
        type=int,
        help="Upper bound on the number of SWAP gates to map the circuit. Needs to be provided for --search_strategy=backward"
    )
    layout_parser.add_argument(
        "--parallel_swaps",
        type=int,
        help="adds parallel swaps in each time step [0/1], default 0, (*)",
        default=0,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "--metric",
        help=textwrap.dedent(
            """\
                                The primary metric to optimize for:
                                  cx-count = number of cx gates (default)
                                  cx-depth = maximal depth of cx gates
                                  depth    = maximal circuit depth"""
        ),
        default="cx-count",
        choices={"cx-count", "cx-depth", "depth"},
    )
    layout_parser.add_argument(
        "--secondary_metric",
        help=textwrap.dedent(
            """\
            If provided, a second optimization run will optimize this metric while bounding the optimal value
            of the primary metric. Note that 'depth' and 'cx-depth' cannot be combined as primary/secondary metrics.
            Options are:
                None (default)
                cx-count (number of CNOT gates)
                cx-depth (depth of CNOT gates)"""
        ),
        default=None,
        choices={"cx-count", "cx-depth"},
    )
    layout_parser.add_argument(
        "--subarch",
        type=int,
        help="Use subarchitectures (with max ancillas) [0/1]: 0=no (default), 1=yes (*)",
        default=0,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "--search_strategy",
        type=str,
        help=textwrap.dedent(
            """
            The search strategy to use, either 'forward' or 'backward'.
            """
        ),
        default="forward",
    )


def configure_cnot_parser(cnot_parser):
    cnot_parser.add_argument(
        "--minimize",
        help=textwrap.dedent(
            """\
                               Minimization metric for CNOT synthesis:
                                 cx-count = minimizing number of CNOT gates (default)
                                 cx-depth = minimizing depth of CNOT gates (only for qbf and sat solvers)"""
        ),
        default="cx-count",
        choices=("cx-count", "cx-depth"),
    )
    cnot_parser.add_argument(
        "--bound",
        help=textwrap.dedent(
            """\
                               Bound metric for CNOT synthesis. If provided, the synthesis will not increase this metric.
                               Defaults to None (no bound). Other options are:
                                 cx-count = bounding number of CNOT gates
                                 cx-depth = bounding depth of CNOT gates"""
        ),
        default=None,
        choices=("cx-count", "cx-depth"),
    )
    cnot_parser.add_argument(
        "-m",
        "--model",
        help=textwrap.dedent(
            """\
                               Encoding to use:
                                 planning = only for cx-count optimization with/without connectivity restrictions
                                 qbf = for count and depth optimization with/without connectivity restrictions but not with qubit permutation
                                 sat = works with all combinations (default)"""
        ),
        default="sat",
        choices=("planning", "qbf", "sat"),
    )
    cnot_parser.add_argument(
        "-s",
        "--solver",
        help=textwrap.dedent(
            """\
                               Choose either a planner (with --model=planning):
                                 fd-ms         = seq-opt-merge-and-shrink (default)
                                 lama          = lama
                                 madagascar    = Madagascar (M) (sequential, optimal)
                               Or a SAT solver (with --model=sat):
                                 cd            = cadical (needs to installed seperately)
                                 pysat-cd      = pysat with cadical backend (default)
                                 pysat-[sat solver name] = pysat with any available backend solver
                               Or a QBF solver (with --model=qbf):
                                 caqe          = caqe solver with bloqqer preprocessor (default)"""
        ),
    )
    cnot_parser.add_argument(
        "-q",
        "--qubit_permute",
        help="Allow any permutation of qubits in CNOT subcircuits",
        action="store_true",
    )
    cnot_parser.add_argument(
        "--search_strategy",
        help=textwrap.dedent(
            """\
                               search direction to use, only of sat models:
                                 forward           = forward up to the given bound (default)
                                 unbounded-forward = unbounded forward, until some solution found
                                 backward          = backward search from a given bound"""
        ),
        default="forward",
    )

    cnot_parser.add_argument(
        "-d",
        "--disable_unused",
        help="allow gates only on used qubits in the original circuit(*)",
        action="store_true",
    )


def configure_cnot_rz_parser(cnot_rz_parser):
    cnot_rz_parser.add_argument(
        "--minimize",
        help=textwrap.dedent(
            """\
                               Minimization metric for CNOT+Rz synthesis:
                                 cx-count = minimizing number of CNOT gates (default)
                                 cx-depth = minimizing depth of CNOT gates
            """
        ),
        default="cx-count",
        choices=("cx-count", "cx-depth"),
    )
    cnot_rz_parser.add_argument(
        "--bound",
        help=textwrap.dedent(
            """\
                               Bound metric for CNOT+Rz synthesis. If provided, the synthesis will not increase this metric.
                               Defaults to None. Options are:
                                 cx-count = bounding number of CNOT gates
                                 cx-depth = bounding depth of CNOT gates"""
        ),
        default=None,
        choices=("cx-count", "cx-depth"),
    )
    cnot_rz_parser.add_argument(
        "-q",
        "--qubit_permute",
        help="Allow any permutation of qubits in CNOT subcircuits",
        action="store_true",
    )
    cnot_rz_parser.add_argument(
        "--search_strategy",
        help=textwrap.dedent(
            """\
                               search strategy to use:
                                 forward           = forward search up to the given bound (default)
                                 backward          = backward search from a given bound
                                 binary            = binary search below a given bound
                                 maxsat            = using a MaxSAT solver from PySAT
            """
        ),
        default="forward",
    )
    cnot_rz_parser.add_argument(
        "-d",
        "--disable_unused",
        help="allow gates only on used qubits in the original circuit(*)",
        action="store_true",
    )


def configure_clifford_parser(clifford_parser):
    clifford_parser.add_argument(
        "--minimize",
        help=textwrap.dedent(
            """\
                               Minimization metric for Clifford synthesis:
                                 cx-count           = minimizing number of CNOT gates (default)
                                 cx-depth           = CNOT depth minimization (only for sat solvers)
                                 cx-count_1q-count  = minimizing 1-qubit gates and CNOT gates (only for planning)
                                 """
        ),
        default="cx-count",
    )
    clifford_parser.add_argument(
        "--bound",
        help=textwrap.dedent(
            """\
                               Bound metric for Clifford synthesis. If provided, the synthesis will not increase this metric.
                               Specifying a bound is only available with SAT. Defaults to None. Options are:
                                 cx-count = bounding number of CNOT gates
                                 cx-depth = bounding depth of CNOT gates"""
        ),
        default=None,
        choices=("cx-count", "cx-depth"),
    )
    clifford_parser.add_argument(
        "-m",
        "--model",
        help=textwrap.dedent(
            """\
                               technique to use:
                                 planning = only for cx-count optimization with/without connectivity restrictions
                                 sat = works with all combinations (default)"""
        ),
        default="sat",
    )
    clifford_parser.add_argument(
        "--search_strategy",
        help=textwrap.dedent(
            """\
                               search direction to use, only of sat models:
                                 forward           = forward up to the given bound (default)
                                 unbounded-forward = unbounded forward, until some solution found
                                 backward          = backward search from a given bound"""
        ),
        default="forward",
    )
    clifford_parser.add_argument(
        "--postprocess_1q_gates",
        help="post-processing mode for 1-qubit gates: greedy (default), rigid, or none",
        choices=["greedy", "rigid", "none"],
        default="greedy",
    )
    clifford_parser.add_argument(
        "-g", "--gate_ordering", help="fix parallel gate ordering", action="store_true"
    )
    clifford_parser.add_argument(
        "-r",
        "--simple_path_restrictions",
        help="allow only simple paths across layers",
        action="store_true",
    )
    clifford_parser.add_argument(
        "--cycle_bound",
        type=int,
        help="number of layers to break cycles with simple path restrictions, default=3; -1 breaks all cycles",
        default=3,
    )
    clifford_parser.add_argument(
        "-d",
        "--disable_unused",
        help="allow gates only on used qubits in the original circuit(*)",
        action="store_true",
    )
    clifford_parser.add_argument(
        "-s",
        "--solver",
        help=textwrap.dedent(
            """\
                               Choose either a planner (with --model=planning):
                                 fd-ms         = seq-opt-merge-and-shrink (default)
                                 lama          = lama
                               Or a SAT solver (with --model=sat):
                                 cd            = cadical
                                 pysat-cd      = pysat with cadical backend (default)
                                 pysat-[sat solver name] = pysat with any available backend solver
                                 gimsatul      = gimsatul, a parallel sat solver
                                 mallob      = mallob, a parallel sat solver"""
        ),
    )
    # clifford_parser.add_argument(
    #    "--nthreads",
    #    type=int,
    #    help="number of threads for parallel sat solvers, default 4",
    #    default=4,
    # )
    # clifford_parser.add_argument(
    #    "--mallob_solver_string",
    #    help="solver sequence for mallob, default 'k+(ck)*'",
    #    default="k+(ck)*",
    # )
    clifford_parser.add_argument(
        "-q",
        "--qubit_permute",
        help="Allow any permutation of qubits",
        action="store_true",
    )


def make_common_parsers():
    io_parser = argparse.ArgumentParser(add_help=False)
    io_parser.add_argument(
        "circuit_in",
        help="input file: logical quantum circuit (default ?/Benchmarks/ECAI-24/tpar-optimized/barenco_tof_3.qasm)",
        metavar="INPUT.qasm",
        nargs="?",
    )
    io_parser.add_argument(
        "circuit_out",
        help="output file: mapped quantum circuit (default None - no output)",
        nargs="?",
        metavar="OUTPUT.qasm",
    )

    platform_parser = argparse.ArgumentParser(add_help=False)
    platform_parser.add_argument(
        "-p",
        "--platform",
        help=textwrap.dedent(
            """\
                               Either provider name:
                                 tenerife  = FakeTenerife/IBM QX2, 5 qubit
                                 melbourne = FakeMelbourne, 14 qubit
                                 tokyo     = FakeTokyo, 20 qubit
                               Or generated platforms:
                                 rigetti-{8,12,14,16} = various subgraphs of the rigetti platform
                                 sycamore   = google sycamore platform with grid like topology - 54 qubits
                                 star-{3,7} = test with 3/7-legged star topology (need swaps before first cnot)
                                 cycle-5    = cycle of 5 qubits (good for testing use of ancilla qubits)
                                 grid-{4,5,6,7,8}  = nxn grid (standard platforms for experiments)
                                 test       = test platform (can be anything for experimentation)
                               If none provided, we do not map (default = None)
                               """
        ),
        default=None,
    )
    platform_parser.add_argument(
        "-b",
        "--bidirectional",
        type=int,
        help="Make coupling bidirectional [0/1]: 0=no, 1=yes (default)",
        default=1,
        choices=(0, 1),
    )

    run_parser = argparse.ArgumentParser(add_help=False)
    run_parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        help="[-1/0/1/2/3], default=0, visual=1, extended=2, debug=3, silent=-1",
        default=0,
        choices=(-1, 0, 1, 2, 3),
    )
    run_parser.add_argument(
        "-t",
        "--time",
        type=int,
        help=textwrap.dedent(
            """
            Solving time limit in seconds, adds 1s per slice as buffer for io when doing peephole synthesis.
            Defaults to 600 seconds.
            """
        ),
        default=600,
    )
    run_parser.add_argument(
        "--aux_files",
        help="location for intermediate files (default ./intermediate_files)",
        default="./intermediate_files",
        metavar="DIR",
    )
    run_parser.add_argument(
        "--check",
        type=int,
        help="Check correctness (equivalence, connectivity) [0/1]: 0=no (default), 1=yes",
        default=0,
        choices=(0, 1),
    )

    return io_parser, platform_parser, run_parser


if __name__ == "__main__":
    version = "Version 6.0.beta"
    text = f"Q-Synth - Optimal Quantum-Circuit Synthesis ({version})"
    parser = argparse.ArgumentParser(
        description=text,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent(
            """\
                                Use 'q-synth.py layout -h'    for detailed help on Quantum Layout Synthesis
                                Use 'q-synth.py cnot -h'      for detailed help on CNOT Synthesis and Peephole Optimization
            """
        ),
    )
    parser.add_argument("--version", help="show program version", action="store_true")
    sub_parsers = parser.add_subparsers(
        help="Available Synthesis subcommands", dest="subparser_name", required=True
    )

    common_io_parser, common_platform_parser, common_run_parser = make_common_parsers()

    layout_subparser = sub_parsers.add_parser(
        "layout",
        parents=[common_io_parser, common_run_parser],
        help="Quantum Layout Synthesis",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent(
            """\
                                (*) changing these options may result in sub-optimal results
                                (1) Other supported planners: fd-lmcut, fdss-sat (*), fdss-opt-1 (*), fdds-opt-2 (*) 
                                (2) See for PySat solvers: https://pysathq.github.io/docs/html/api/solvers.html#pysat.solvers.SolverNames
                                (3) See for PySat cardinality: https://pysathq.github.io/docs/html/api/card.html#pysat.card.EncType
            """
        ),
    )
    configure_layout_parser(layout_subparser)

    # CNOT synthesis with Peephole optimization:
    cnot_subparser = sub_parsers.add_parser(
        "cnot",
        parents=[common_io_parser, common_platform_parser, common_run_parser],
        help="CNOT synthesis via Peephole optimization",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="(*) changing these options may result in sub-optimal results",
    )
    configure_cnot_parser(cnot_subparser)

    # CNOT+Rz synthesis with Peephole optimization:
    cnot_rz_subparser = sub_parsers.add_parser(
        "cnot_rz",
        parents=[common_io_parser, common_platform_parser, common_run_parser],
        help="CNOT+Rz synthesis via Peephole optimization",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="(*) changing these options may result in sub-optimal results",
    )
    configure_cnot_rz_parser(cnot_rz_subparser)

    # Clifford synthesis:
    clifford_subparser = sub_parsers.add_parser(
        "clifford",
        parents=[common_io_parser, common_platform_parser, common_run_parser],
        help="Clifford synthesis via Peephole optimization",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="(*) changing these options may result in sub-optimal results",
    )
    configure_clifford_parser(clifford_subparser)

    args = parser.parse_args()

    #  print(args)

    try:
        git_label = subprocess.check_output(
            ["git", "describe", "--always"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        git_label = "Not under git"

    if args.version:
        print(
            "Q-Synth - Optimal Quantum Layout Synthesis, CNOT resynthesis, and Clifford resynthesis"
        )
        print("(c) Irfansha Shaik, Jaco van de Pol, Aarhus, 2023, 2024, 2025, 2026")
        print(version)
        print("Git commit hash: " + git_label)
        exit(0)

    if args.verbose > -1:
        print(
            "Q-Synth - Optimal Quantum Layout Synthesis and CNOT resynthesis, and Clifford resynthesis"
        )
        print(f"{version}, git commit hash: " + git_label)
        print("arguments:")
        for key, val in vars(args).items():
            print(f"\t{key:26}{val}")
        print("Start time: " + str(datetime.datetime.now()))

    # Make sure that input circuit is specified
    if not args.circuit_in:
        print("Error: Input file not specified.")
        exit(1)

    try:
        # Read the input file and convert it into a quantum circuit using Qiskit
        circuit_in = QuantumCircuit.from_qasm_file(args.circuit_in)

        coupling_graph = None
        if args.platform:
            coupling_graph = get_coupling_graph(platform=args.platform, bidirectional=args.bidirectional)

        if args.subparser_name == "layout":
            print("Layout Synthesis")

            if args.subarch:
                print("Using subarchitectures")

            result = layout_synthesis(circuit=circuit_in, coupling_graph=coupling_graph, metric=args.metric,
                                      secondary_metric=args.secondary_metric, parallel_swaps=args.parallel_swaps,
                                      subarchitecture=args.subarch, num_ancillary_qubits=args.ancillas,
                                      search_strategy=args.search_strategy, swap_upper_bound=args.swap_upper_bound,
                                      relaxed_dependencies=args.relaxed, cancel_cnots=args.cnot_cancel,
                                      allow_bridges=args.bridge, model=args.model, solver=args.solver, check=args.check,
                                      intermediate_files_path=args.aux_files, timeout=args.time, verbose=args.verbose)

        elif args.subparser_name == "cnot":
            print("CNOT Synthesis")
            result = cnot_peephole_synthesis(circuit=circuit_in, metric=args.minimize, bound_metric=args.bound,
                                             coupling_graph=coupling_graph, output_qubit_permute=args.qubit_permute,
                                             search_strategy=args.search_strategy,
                                             disable_unused_qubits=args.disable_unused, model=args.model,
                                             solver=args.solver, check=args.check,
                                             intermediate_files_path=args.aux_files, timeout=args.time,
                                             verbose=args.verbose)

        elif args.subparser_name == "cnot_rz":
            print("CNOT+Rz Synthesis")
            result = cnot_rz_peephole_synthesis(circuit=circuit_in, metric=args.minimize, bound_metric=args.bound,
                                                coupling_graph=coupling_graph, output_qubit_permute=args.qubit_permute,
                                                search_strategy=args.search_strategy,
                                                disable_unused_qubits=args.disable_unused, check=args.check,
                                                intermediate_files_path=args.aux_files, timeout=args.time,
                                                verbose=args.verbose)
        else:
            assert args.subparser_name == "clifford"
            print("Clifford Synthesis")
            result = clifford_peephole_synthesis(circuit=circuit_in, metric=args.minimize, bound_metric=args.bound,
                                                 coupling_graph=coupling_graph, output_qubit_permute=args.qubit_permute,
                                                 postprocess_1q_gates=None if args.postprocess_1q_gates == "none" else args.postprocess_1q_gates,
                                                 disable_unused_qubits=args.disable_unused,
                                                 gate_ordering=args.gate_ordering,
                                                 simple_path_restrictions=args.simple_path_restrictions,
                                                 cycle_bound=args.cycle_bound, search_strategy=args.search_strategy,
                                                 model=args.model, solver=args.solver, check=args.check,
                                                 intermediate_files_path=args.aux_files, timeout=args.time,
                                                 verbose=args.verbose)

        if args.circuit_out:
            qasm2.dump(result.circuit, args.circuit_out)

    except Exception as e:
        print(f"Q-Synth exited with error:")
        print(e)
        exit(1)
