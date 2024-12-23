#! /usr/bin/env python3

# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023, 2024

import argparse
import datetime
import subprocess
import textwrap

if __name__ == '__main__':
  version = "Version 3.0"
  text = f"Q-Synth - Optimal Quantum Layout Synthesis ({version})"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("--version", help="show program version", action="store_true")
  sub_parsers = parser.add_subparsers(help="Available Synthesis subcommands", dest="subparser_name", required=True)
  layout_parser = sub_parsers.add_parser("layout", help="Quantum Layout Synthesis",formatter_class=argparse.RawTextHelpFormatter,
                                         epilog="(*) changing these options may result in sub-optimal results\n(**) MQT QCEC needs to be installed")
  layout_parser.add_argument("circuit_in", help="input file: logical quantum circuit (default ?/Benchmarks/ICCAD-23/or.qasm)", metavar="INPUT.qasm", nargs="?")
  layout_parser.add_argument("circuit_out", help="output file: mapped quantum circuit (default None - no output)", nargs="?", metavar="OUTPUT.qasm")
  layout_parser.add_argument("-p", "--platform", help=textwrap.dedent('''\
                               Either provider name:
                                 tenerife  = FakeTenerife/IBM QX2, 5 qubit
                                 melbourne = FakeMelbourne, 14 qubit (default)
                                 tokyo     = FakeTokyo, 20 qubit
                               Or generated platforms:
                                 rigetti-{8,12,14,16} = various subgraphs of the rigetti platform
                                 sycamore   = google sycamore platform with grid like topology - 54 qubits
                                 star-{3,7} = test with 3/7-legged star topology (need swaps before first cnot)
                                 cycle-5    = cycle of 5 qubits (good for testing use of ancillary bits)
                                 grid-{4,5,6,7,8}  = nxn grid (standard platforms for experiments)
                                 test       = test platform (can be anything for experimentation)
                               '''), default = "melbourne")
  layout_parser.add_argument("-b", "--bidirectional", type=int, help="Make coupling bidirectional [0/1/2]: 0=no, 1=yes (default), 2=use H-CNOT-H" ,default = 1)
  layout_parser.add_argument("--symmetry_breaking", type=int, help="Compute Isomorphic physical qubits (symmetry breaking to do) [0/1/2]: 0=no (default), 1=yes (on first qubit), 2=yes (on first 2 qubits)" ,default = 0)
  layout_parser.add_argument("--distance_sb", type=int, help=textwrap.dedent('''\
                                "based on physical qubit distances, some qubits are disabled (only in ancillary for now) [0/1/2]: 
                                 0=no (default),
                                 1= applies distance restrictions,
                                 2= applies distance restrictions and uses symmetry breaking for mutual qubit exclusion
                                 '''),default = 0)
  layout_parser.add_argument("-m", "--model", help=textwrap.dedent('''\
                               Model type used for the encoding:
                                 global = uses global levels to ensure dependencies (with separate initial mapping)
                                 local  = local dependencies, grounded model
                                 lifted = lifted, non-grounded local model
                                 sat = uses sat encoding instead of planning (default)'''), default = "sat")
  layout_parser.add_argument("-a", "--ancillary", type=int, help="Ancillary bits may be used [0/1]: 0=no, 1=yes (default) (*)", default = 1)
  layout_parser.add_argument("-i", "--initial", type=int, help="Initial mapping is separate [0/1]: 0=integrated (default), 1=separate", default=0)
  layout_parser.add_argument("-r", "--relaxed", type=int, help="Use relaxed dependencies [0/1]: 0=strict (default), 1=relaxed dependencies", default=0)
  layout_parser.add_argument("-c", "--cnot_cancel", type=int, help="Cancel CNOT gates [0/1]: 0=no (default), 1=cancel", default=0)
  layout_parser.add_argument("-q", "--qiskit_optimize", type=int, help="0=none (default), [1,2,3]=standard qiskit optimization levels", default=0, metavar="LEVEL")
  layout_parser.add_argument("--bridge", type=int, help="Use bridge gates [0/1]: 0=no (default), 1=with bridges", default=0)
  layout_parser.add_argument("-t", "--time", type=float, help="Solving time limit in seconds, default 1800 seconds", default = 1800)
  layout_parser.add_argument("-s", "--solver", help=textwrap.dedent('''\
                               Either a planner tool combination:
                                 fdss-sat = seq-sat-fdss-2018
                                 fdss-opt = seq-opt-fdss-1 (*)
                                 fdss-opt-2 = seq-opt-fdss-2 (*)
                                 fd-bjolp = seq-opt-bjolp (default)
                                 fd-ms = seq-opt-merge-and-shrink
                                 fd-lmcut = fast downward with LM-cut heuristic
                                 M-seq = Madagascar sequential (*)
                                 M-seq-optimal = Madagascar sequential, only optimal plans
                                 LiSAT = lifted SAT solver
                                 MpC = Madagascar C, with parallel plans (*)
                               Or a SAT solver from PySAT (with --model=sat):
                                 cd   = cadical103
                                 cd15 = cadical153 (default)
                                 gc3  = gluecard3
                                 gc4  = gluecard41
                                 g3   = glucose3
                                 g4   = glucose4
                                 lgl  = lingeling
                                 mcb  = maplechrono
                                 mcm  = maplecm
                                 mpl  = maplesat
                                 mg3  = mergesat3
                                 mc   = minicard
                                 m22  = minisat22
                                 mgh  = minisatgh'''))
  layout_parser.add_argument("--cardinality", type=int,help=textwrap.dedent('''\
                               At-Most and At-Least constraints from PySAT:
                                 0 = pairwise
                                 1 = seqcounter (default)
                                 2 = sortnetwrk
                                 3 = cardnetwrk
                                 4 = bitwise
                                 5 = ladder
                                 6 = totalizer
                                 7 = mtotalizer
                                 8 = kmtotalizer
                                 9 = native (needs more testing)'''), default = 1)
  layout_parser.add_argument("--start", type=int, help="solve sat instances, starting from this depth, default 0 (*)", default = 0)
  layout_parser.add_argument("--step", type=int, help="solve the sat instance, with depths modulo step, default 1 (*)", default = 1)
  layout_parser.add_argument("--end", type=int, help="solve sat instances until this depth (inclusive) when specified, (*)")
  layout_parser.add_argument("--twoway_sat", type=int, help="use twoway propagation of CNOT dependency information [0/1], default 1", default = 1)
  layout_parser.add_argument("--near_optimal", type=int, help="Adds bridges along with swaps, adds atmost k+1 bridges if k is optimal number of swaps [0/1], default 0", default = 0)
  layout_parser.add_argument("--parallel_swaps", type=int, help="adds parallel swaps in each time step (bounded optimal) [0/1], default 0", default = 0)
  layout_parser.add_argument("--constraints", type=int, help=textwrap.dedent('''
                               Three levels of sat encoding constraints:
                                 0 = removing any constraints will result in an incorrect encoding
                                 1 = extra clauses for pruning
                                 2 = extra binary clauses (redundant constraints), helps sat solver (default)'''), default = 2)
  layout_parser.add_argument("--lp_connections", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                                 0 = auxiliary variables for logical physical connections
                                 1 = directly clauses on logical pair variables (default)
                                 2 = clauses to indicate distance'''), default = 1)
  layout_parser.add_argument("--lp_distance", type=int, help="when set to -1, max swap distance is used otherwise restrictions are added until the number specified, default -1", default = -1)
  layout_parser.add_argument("--group_cnots", type=int, help="if two consequent cnots act on same qubits, then we group them when enabled [0/1], default 0", default = 0)
  layout_parser.add_argument("--aux_files", help="location for intermediate files (default ./intermediate_files)", default = "./intermediate_files", metavar="DIR")
  layout_parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                                 0 = only generate pddl files
                                 1 = computed mapped layout with swap gates (default)'''), default = 1)
  layout_parser.add_argument("-v", "--verbose", type=int, help="[-1/0/1/2/3], default=0, visual=1, extended=2, debug=3, silent=-1", default = 0)
  layout_parser.add_argument("--check_equivalence", type=int, help="Check equivalence using qcec or native testing (if available) [0/1]: 0=no (default), 1=yes (**)" ,default = 0)
  # CNOT synthesis with Peephole optimization:
  cnot_parser = sub_parsers.add_parser("cnot", help="CNOT synthesis via Peephole optimization",formatter_class=argparse.RawTextHelpFormatter,
                                       epilog="(*) MQT QCEC needs to be installed")
  cnot_parser.add_argument("circuit_in", help="input file: logical quantum circuit (default ?/Benchmarks/ECAI-24/tpar-optimized/barenco_tof_3.qasm)", metavar="INPUT.qasm", nargs="?")
  cnot_parser.add_argument("circuit_out", help="output file: mapped quantum circuit (default None - no output)", nargs="?", metavar="OUTPUT.qasm")
  cnot_parser.add_argument("-v", "--verbose", type=int, help="show intermediate info [0/1/2], default 0", default=0)
  cnot_parser.add_argument("--minimize", help=textwrap.dedent('''\
                               Minimization metric for CNOT synthesis:
                                 gates = minimizing number of gates (default)
                                 depth = depth minimization (only for qbf and sat solvers)'''),default="gates")
  cnot_parser.add_argument("--aux_files", help="location for intermediate files (default ./intermediate_files)", default = "./intermediate_files", metavar="DIR")
  cnot_parser.add_argument("-m", "--model", help=textwrap.dedent('''\
                               Encoding to use:
                                 planning = only for gates optimization with/without connectivity restrictions
                                 qbf = for gates and depth optimization with/without connectivity restrictions but not with qubit permutation
                                 sat = works with all combinations  (default)'''), default = "sat")
  cnot_parser.add_argument("-s", "--solver", help=textwrap.dedent('''\
                               Choose either a planner (with --model=planning):
                                 fd-ms         = seq-opt-merge-and-shrink (default)
                                 lama          = lama
                               Or a SAT solver (with --model=sat):
                                 cd            = cadical (default)
                               Or a QBF solver (with --mode=qbf):
                                 caqe          = caqe solver with bloqqer preprocessor (default)'''))
  cnot_parser.add_argument('-q',"--qubit_permute", help="Allow any permutation of qubits in CNOT subcircuits", action="store_true")
  cnot_parser.add_argument("-t", "--time", type=float, help="Solving time limit per slice in seconds, default 600 seconds", default = 600)
  cnot_parser.add_argument("-p", "--platform", help=textwrap.dedent('''\
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
                               '''), default=None)
  cnot_parser.add_argument("-b", "--bidirectional", type=int, help="Make coupling bidirectional [0/1]: 0=no, 1=yes (default)" ,default = 1)
  cnot_parser.add_argument("--check_equivalence", type=int, help="Check equivalence using qcec [0/1]: 0=no (default), 1=yes (*)" ,default = 0)
  cnot_parser.add_argument("--only_write_pddl_files", help="Only generate PDDL instance files instead of executing the planner", action="store_true")

  args = parser.parse_args()

  #print(args)

  try:
    git_label = subprocess.check_output(["git", "describe", "--always"], text=True).strip()
  except subprocess.CalledProcessError:
    git_label = "Not under git"

  if args.version:
    print("Q-Synth - Optimal Quantum Layout Synthesis and CNOT resynthesis")
    print("(c) Irfansha Shaik, Jaco van de Pol, Aarhus, 2023, 2024")
    print(version)
    print("Git commit hash: " + git_label)
    exit(0)

  if args.verbose > -1:
    print("Q-Synth - Optimal Quantum Layout Synthesis and CNOT resynthesis")
    print(f"{version}, git commit hash: " + git_label)
    print("arguments:")
    for key,val in vars(args).items():
      print(f"\t{key:26}{val}")
    print("Start time: " + str(datetime.datetime.now()))

  if (args.subparser_name == "layout"):
    from src.LayoutSynthesis.layout_synthesis import layout_synthesis
    print("Layout Synthesis")
    layout_synthesis(circuit_in=args.circuit_in, circuit_out=args.circuit_out, platform=args.platform, model=args.model, solver=args.solver, solver_time=args.time,
                     ancillary=args.ancillary, relaxed=args.relaxed, bidirectional=args.bidirectional, bridge=args.bridge, start=args.start, step=args.step, end=args.end, run=args.run,
                     symmetry_breaking=args.symmetry_breaking, verbose=args.verbose, distance_sb=args.distance_sb, initial=args.initial, cnot_cancel=args.cnot_cancel, qiskit_optimize=args.qiskit_optimize,
                     cardinality=args.cardinality, twoway_sat=args.twoway_sat, near_optimal=args.near_optimal, parallel_swaps=args.parallel_swaps, constraints=args.constraints,
                     lp_connections=args.lp_connections, lp_distance=args.lp_distance, group_cnots=args.group_cnots, aux_files=args.aux_files, check_equivalence=args.check_equivalence)
  elif (args.subparser_name == "cnot"):
    from src.peephole_cnotsynthesis import peephole_cnotsynthesis
    print("CNOT Synthesis")
    peephole_cnotsynthesis(circuit_in=args.circuit_in, circuit_out=args.circuit_out, minimize=args.minimize,
                           model=args.model, qubit_permute=args.qubit_permute,
                           solver=args.solver, time=args.time, platform=args.platform, bidirectional=args.bidirectional,
                           intermediate_files_path=args.aux_files, verbose=args.verbose, check_equivalence=args.check_equivalence,
                           only_write_pddl_files=args.only_write_pddl_files)
