#! /usr/bin/env python3

# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024

import argparse
import datetime
import subprocess
import textwrap

from src.layout_config import MODELS, METRICS, SOLVERS

if __name__ == "__main__":
    version = "Version 5.0"
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
    layout_parser = sub_parsers.add_parser(
        "layout",
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
    layout_parser.add_argument(
        "circuit_in",
        help="input file: logical quantum circuit",
        metavar="INPUT.qasm",
        nargs="?",
    )
    layout_parser.add_argument(
        "circuit_out",
        help="output file: mapped quantum circuit (default None - no output)",
        nargs="?",
        metavar="OUTPUT.qasm",
    )
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
                                 line-<n>  = linear platofrm of <n> qubits (good for testing use of ancilla qubits)
                                 cycle-<n> = cycle of <n> qubits (good for testing use of ancilla qubits)
                                 star-<n>  = center qubit + <n>-legged star (need swaps before first cnot)
                                 grid-<n>  = nxn grid (standard platforms for experiments)
                                 test      = test platform (can be anything for experimentation)
                               """
        ),
        default="melbourne",
    )
    layout_parser.add_argument(
        "-b",
        "--bidirectional",
        type=int,
        help="Make coupling bidirectional [0/1/2]: 0=no, 1=yes (default), 2=use H-CNOT-H",
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
        help="Max number of ancilla bits allowed: -1 (d) unlimited; 0,1,2,...: specify max (*)",
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
        "-t",
        "--time",
        type=float,
        help="Solving time limit in seconds, default 1800 seconds",
        default=1800,
    )
    layout_parser.add_argument(
        "-s",
        "--solver",
        help=textwrap.dedent(
            """\
                               Either a planner tool combination:
                                 fd-bjolp (default), fd-ms, madagascar, etc (1)
                               Or a SAT solver from PySAT (with --model=sat):
                                 cd19 = cadical195 (default), g42  = glucose42, etc. (2)
                                 """
        ),
    )
    layout_parser.add_argument(
        "--cardinality",
        type=int,
        help=textwrap.dedent(
            """\
                               At-Most/At-Least constraints from PySAT cardinality:
                                 0 = pairwise, 1 = seqcounter (default), 2 = sortnetwrk, etc. (3)
                                 """
        ),
        default=1,
    )
    layout_parser.add_argument(
        "--start",
        type=int,
        help="solve sat instances, starting from this depth, default 0 (*)",
        default=0,
    )
    layout_parser.add_argument(
        "--step",
        type=int,
        help="solve the sat instance, with depths modulo step, default 1 (*)",
        default=1,
    )
    layout_parser.add_argument(
        "--end",
        type=int,
        help="solve sat instances until this depth (inclusive) when specified, (*)",
    )
    layout_parser.add_argument(
        "--parallel_swaps",
        type=int,
        help="adds parallel swaps in each time step [0/1], default 0, (*)",
        default=0,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "--aux_files",
        help="location for intermediate files (default ./intermediate_files)",
        default="./intermediate_files",
        metavar="DIR",
    )
    layout_parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        help="[-1/0/1/2/3], default=0, visual=1, extended=2, debug=3, silent=-1",
        default=0,
        choices=(-1, 0, 1, 2, 3),
    )
    layout_parser.add_argument(
        "--check",
        type=int,
        help="Check correctness (equivalence and platform restrictions) [0/1]: 0=no (default), 1=yes",
        default=0,
        choices=(0, 1),
    )
    layout_parser.add_argument(
        "--metric",
        help=textwrap.dedent(
            """\
                                The metric to optimise for:
                                cx-count = number of cx gates
                                cx-depth = maximal depth of cx gates
                                depth    = maximal circuit depth
                                depth-cx-count = depth first, then number of cx-gates
                                cx-depth-cx-count = cx-depth first, then number of cx-gates"""
        ),
        default="cx-count",
        choices=METRICS,
    )
    layout_parser.add_argument(
        "--subarch",
        type=int,
        help="Use subarchitectures (with max ancillas) [0/1]: 0=no (default), 1=yes (*)",
        default=0,
        choices=(0, 1),
    )

    # CNOT synthesis with Peephole optimization:
    cnot_parser = sub_parsers.add_parser(
        "cnot",
        help="CNOT synthesis via Peephole optimization",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="(*) changing these options may result in sub-optimal results",
    )
    cnot_parser.add_argument(
        "circuit_in",
        help="input file: logical quantum circuit (default ?/Benchmarks/ECAI-24/tpar-optimized/barenco_tof_3.qasm)",
        metavar="INPUT.qasm",
        nargs="?",
    )
    cnot_parser.add_argument(
        "circuit_out",
        help="output file: mapped quantum circuit (default None - no output)",
        nargs="?",
        metavar="OUTPUT.qasm",
    )
    cnot_parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        help="show intermediate info [0/1/2], default 0",
        default=0,
        choices=(0, 1, 2),
    )
    cnot_parser.add_argument(
        "--minimize",
        help=textwrap.dedent(
            """\
                               Minimization metric for CNOT synthesis:
                                 gates = minimizing number of gates (default)
                                 depth = depth minimization (only for qbf and sat solvers)"""
        ),
        default="gates",
        choices=("gates", "depth"),
    )
    cnot_parser.add_argument(
        "--aux_files",
        help="location for intermediate files (default ./intermediate_files)",
        default="./intermediate_files",
        metavar="DIR",
    )
    cnot_parser.add_argument(
        "-m",
        "--model",
        help=textwrap.dedent(
            """\
                               Encoding to use:
                                 planning = only for gates optimization with/without connectivity restrictions
                                 qbf = for gates and depth optimization with/without connectivity restrictions but not with qubit permutation
                                 sat = works with all combinations  (default)"""
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
                                 cd            = cadical (default)
                               Or a QBF solver (with --mode=qbf):
                                 caqe          = caqe solver with bloqqer preprocessor (default)"""
        ),
        choices=("fd-ms", "lama", "madagascar", "cd", "caqe"),
    )
    cnot_parser.add_argument(
        "-q",
        "--qubit_permute",
        help="Allow any permutation of qubits in CNOT subcircuits",
        action="store_true",
    )
    cnot_parser.add_argument(
        "--optimal_search",
        help=textwrap.dedent(
            """\
                               search direction to use, only of sat models:
                                 f  = forward up to the given bound (default)
                                 uf = unbounded forward, until some solution found
                                 b  = backward search from a given bound"""
        ),
        default="f",
    )
    cnot_parser.add_argument(
        "-d",
        "--disable_unused",
        help="allow gates only on used qubits in the original circuit(*)",
        action="store_true",
    )
    cnot_parser.add_argument(
        "-t",
        "--time",
        type=float,
        help="Solving time limit in seconds, adds 1s per slice as buffer for io, default 600 seconds",
        default=600,
    )
    cnot_parser.add_argument(
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
    cnot_parser.add_argument(
        "-b",
        "--bidirectional",
        type=int,
        help="Make coupling bidirectional [0/1]: 0=no, 1=yes (default)",
        default=1,
        choices=(0, 1),
    )
    cnot_parser.add_argument(
        "--check",
        type=int,
        help="Check correctness (equivalence, connectivity) [0/1]: 0=no (default), 1=yes",
        default=0,
        choices=(0, 1),
    )
    # Clifford synthesis:
    clifford_parser = sub_parsers.add_parser(
        "clifford",
        help="Clifford synthesis",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="(*) changing these options may result in sub-optimal results",
    )
    clifford_parser.add_argument(
        "circuit_in",
        help="input file: logical quantum circuit (default ?/Benchmarks/ECAI-24/tpar-optimized/barenco_tof_3.qasm)",
        metavar="INPUT.qasm",
        nargs="?",
    )
    clifford_parser.add_argument(
        "circuit_out",
        help="output file: mapped quantum circuit (default None - no output)",
        nargs="?",
        metavar="OUTPUT.qasm",
    )
    clifford_parser.add_argument(
        "-v",
        "--verbose",
        type=int,
        help="show intermediate info [0/1/2], default 0",
        default=0,
    )
    clifford_parser.add_argument(
        "--minimize",
        help=textwrap.dedent(
            """\
                               Minimization metric for Clifford synthesis:
                                 gates = minimizing number of gates (default)
                                 depth = depth minimization (only for qbf and sat solvers)"""
        ),
        default="gates",
    )
    clifford_parser.add_argument(
        "--aux_files",
        help="location for intermediate files (default ./intermediate_files)",
        default="./intermediate_files",
        metavar="DIR",
    )
    clifford_parser.add_argument(
        "-m",
        "--model",
        help=textwrap.dedent(
            """\
                               technique to use:
                                 planning = only for gates optimization
                                 sat = works with all combinations (default)"""
        ),
        default="sat",
    )
    clifford_parser.add_argument(
        "-e",
        "--encoding",
        help=textwrap.dedent(
            """\
                               encoding to use,
                               for sat models:
                                simpleaux = basic encoding with auxiliary variables (default)
                               for planning models:
                                gate_optimal = optimizes number of gates
                                cnot_optimal = optimizes number of CNOT gates"""
        ),
        default="simpleaux",
    )
    clifford_parser.add_argument(
        "--optimal_search",
        help=textwrap.dedent(
            """\
                               search direction to use, only of sat models:
                                 f  = forward up to the given bound (default)
                                 uf = unbounded forward, until some solution found
                                 b  = backward search from a given bound"""
        ),
        default="f",
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
                                 cd            = cadical (default)
                                 gimsatul      = gimsatul, a parallel sat solver"""
        ),
    )
    clifford_parser.add_argument(
        "--nthreads",
        type=int,
        help="number of threads for parallel sat solvers, default 4",
        default=4,
    )
    clifford_parser.add_argument(
        "-q",
        "--qubit_permute",
        help="Allow any permutation of qubits",
        action="store_true",
    )
    clifford_parser.add_argument(
        "-t",
        "--time",
        type=float,
        help="Solving time limit in seconds, adds 1s per slice as buffer for io, default 600 seconds",
        default=600,
    )
    clifford_parser.add_argument(
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
                                 cycle-5    = cycle of 5 qubits (good for testing use of ancillary bits)
                                 grid-{4,5,6,7,8}  = nxn grid (standard platforms for experiments)
                                 test       = test platform (can be anything for experimentation)
                               If none provided, we do not map (default = None)
                               """
        ),
        default=None,
    )
    clifford_parser.add_argument(
        "-b",
        "--bidirectional",
        type=int,
        help="Make coupling bidirectional [0/1]: 0=no, 1=yes (default)",
        default=1,
    )
    clifford_parser.add_argument(
        "--check",
        type=int,
        help="Check equivalence [0/1]: 0=no (default), 1=yes",
        default=0,
    )

    args = parser.parse_args()

    #  print(args)

    try:
        git_label = subprocess.check_output(
            ["git", "describe", "--always"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        git_label = "Not under git"

    if args.version:
        print("Q-Synth - Optimal Quantum Layout Synthesis, CNOT resynthesis, and Clifford resynthesis")
        print("(c) Irfansha Shaik, Jaco van de Pol, Aarhus, 2023, 2024, 2025")
        print(version)
        print("Git commit hash: " + git_label)
        exit(0)

    if args.verbose > -1:
        print("Q-Synth - Optimal Quantum Layout Synthesis and CNOT resynthesis, and Clifford resynthesis")
        print(f"{version}, git commit hash: " + git_label)
        print("arguments:")
        for key, val in vars(args).items():
            print(f"\t{key:26}{val}")
        print("Start time: " + str(datetime.datetime.now()))

    # Make sure that input circuit is specified
    if not args.circuit_in:
        print("Error: Input file not specified.")
        exit(1)

    if args.subparser_name == "layout":
        print("Layout Synthesis")

        # Import layout synthesis wrapper
        from src.layout_synthesis_wrapper import layout_synthesis

        if not args.subarch and args.ancillas > 0:
            print("Ancillas >0: Turning on subarchitectures (--subarch)")
            args.subarch = 1

        if args.subarch:
            print("Using subarchitectures")

            # Call subarchitecture mapping with injected layout synthesis
            from src.Subarchitectures.subarchitectures import subarchitecture_mapping

            subarchitecture_mapping(
                circuit_in=args.circuit_in,
                circuit_out=args.circuit_out,
                platform=args.platform,
                model=args.model,
                solver=args.solver,
                solver_time=args.time,
                num_ancillary_qubits=args.ancillas,  # can still be negative
                relaxed=args.relaxed,
                bidirectional=args.bidirectional,
                bridge=args.bridge,
                start=args.start,
                step=args.step,
                end=args.end,
                verbose=args.verbose,
                cnot_cancel=args.cnot_cancel,
                cardinality=args.cardinality,
                parallel_swaps=args.parallel_swaps,
                aux_files=args.aux_files,
                check=args.check,
                metric=args.metric,
                layout_synthesis_method=layout_synthesis,
            )
        else:  # no subarchitectures

            # Making a call to layout synthesis wrapper instead
            layout_synthesis(
                circuit_in=args.circuit_in,
                circuit_out=args.circuit_out,
                platform=args.platform,
                model=args.model,
                solver=args.solver,
                solver_time=args.time,
                allow_ancillas=(
                    args.ancillas < 0
                ),  # negative means: any number allowed
                relaxed=args.relaxed,
                bidirectional=args.bidirectional,
                bridge=args.bridge,
                start=args.start,
                step=args.step,
                end=args.end,
                verbose=args.verbose,
                cnot_cancel=args.cnot_cancel,
                cardinality=args.cardinality,
                parallel_swaps=args.parallel_swaps,
                aux_files=args.aux_files,
                check=args.check,
                metric=args.metric,
                coupling_graph=None,
            )

    elif args.subparser_name == "cnot":
        from src.peephole_synthesis import peephole_synthesis

        print("CNOT Synthesis")
        peephole_synthesis(
            circuit_in=args.circuit_in,
            circuit_out=args.circuit_out,
            slicing="cnot",
            minimize=args.minimize,
            model=args.model,
            qubit_permute=args.qubit_permute,
            optimal_search=args.optimal_search,
            disable_unused=args.disable_unused,
            solver=args.solver,
            time=args.time,
            platform=args.platform,
            bidirectional=args.bidirectional,
            intermediate_files_path=args.aux_files,
            verbose=args.verbose,
            check=args.check,
        )
    elif args.subparser_name == "clifford":
        from src.peephole_synthesis import peephole_synthesis

        print("Clifford Synthesis")
        peephole_synthesis(
            circuit_in=args.circuit_in,
            circuit_out=args.circuit_out,
            encoding=args.encoding,
            slicing="clifford",
            minimize=args.minimize,
            model=args.model,
            qubit_permute=args.qubit_permute,
            optimal_search=args.optimal_search,
            gate_ordering=args.gate_ordering,
            simple_path_restrictions=args.simple_path_restrictions,
            cycle_bound=args.cycle_bound,
            disable_unused=args.disable_unused,
            solver=args.solver,
            nthreads=args.nthreads,
            time=args.time,
            platform=args.platform,
            bidirectional=args.bidirectional,
            intermediate_files_path=args.aux_files,
            verbose=args.verbose,
            check=args.check,
        )
