#! /usr/bin/env python3

# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

import argparse
import datetime
import subprocess
import textwrap
import time
import os

from generate_global_pddl import GenerateGlobalPDDL as glob
from generate_lifted import GenerateLifted as glip
from generate_local import GenerateLocal as gloc
from sat_encoding import SatEncoding as se
from sat_encoding_twoway import SatEncodingTwoway as setw
from sat_encoding_bridges import SatEncodingBridges as seb
from run_planner import RunPlanner as rp
from circuit_extraction_global import CircuitExtractionGlobal as ceg
from circuit_extraction_local import CircuitExtractionLocal as cel
from circuit_extraction_lifted import CircuitExtractionLifted
from circuit_extraction_sat import CircuitExtractionSAT as ces
from testing_mapped_circuit import TestingMappedCircuit as TMC
from subprocess import CalledProcessError
from qiskit_optimization import qiskit_optimization
import circuit_utils
from qiskit import QuantumCircuit

if __name__ == '__main__':
  version = "Version 0.2.0"
  text = f"Q-Synth - Optimal Quantum Layout Synthesis ({version})"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter,
                                   epilog="(*) changing these options may result in sub-optimal results")
  parser.add_argument("circuit_in", help="input file: logical quantum circuit (default ?/Benchmarks/or.qasm)", metavar="INPUT.qasm", nargs="?")
  parser.add_argument("circuit_out", help="output file: mapped quantum circuit (default None - no output)", nargs="?", metavar="OUTPUT.qasm")
  parser.add_argument("-p", "--platform", help=textwrap.dedent('''\
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
  parser.add_argument("-b", "--bidirectional", type=int, help="Make coupling bidirectional [0/1/2]: 0=no, 1=yes (default), 2=use H-CNOT-H" ,default = 1)
  parser.add_argument("--symmetry_breaking", type=int, help="Compute Isomorphic physical qubits (symmetry breaking to do) [0/1/2]: 0=no (default), 1=yes (on first qubit), 2=yes (on first 2 qubits)" ,default = 0)
  parser.add_argument("--distance_sb", type=int, help=textwrap.dedent('''\
                                "based on physical qubit distances, some qubits are disabled (only in ancillary for now) [0/1/2]: 
                                 0=no (default),
                                 1= applies distance restrictions,
                                 2= applies distance restrictions and uses symmetry breaking for mutual qubit exclusion
                                 '''),default = 0)
  parser.add_argument("-m", "--model", help=textwrap.dedent('''\
                               Model type used for the encoding:
                                 global = uses global levels to ensure dependencies (with separate initial mapping)
                                 local  = local dependencies, grounded model
                                 lifted = lifted, non-grounded local model
                                 sat = uses sat encoding instead of planning (default)'''), default = "sat")
  parser.add_argument("-a", "--ancillary", type=int, help="Ancillary bits may be used [0/1]: 0=no, 1=yes (default) (*)", default = 1)
  parser.add_argument("-i", "--initial", type=int, help="Initial mapping is separate [0/1]: 0=integrated (default), 1=separate", default=0)
  parser.add_argument("-r", "--relaxed", type=int, help="Use relaxed dependencies [0/1]: 0=strict (default), 1=relaxed dependencies", default=0)
  parser.add_argument("-c", "--cnot_cancel", type=int, help="Cancel CNOT gates [0/1]: 0=no (default), 1=cancel", default=0)
  parser.add_argument("-q", "--qiskit_optimize", type=int, help="0=none (default), [1,2,3]=standard qiskit optimization levels", default=0, metavar="LEVEL")
  parser.add_argument("--bridge", type=int, help="Use bridge gates (EXPERIMENTAL) [0/1]: 0=no (default), 1=with bridges (*)", default=0)
  parser.add_argument("-t", "--time", type=float, help="Solving time limit in seconds, default 1800 seconds", default = 1800)
  parser.add_argument("-s", "--solver", help=textwrap.dedent('''\
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
  parser.add_argument("--cardinality", type=int,help=textwrap.dedent('''\
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
  parser.add_argument("--start", type=int, help="solve sat instances, starting from this depth, default 0 (*)", default = 0)
  parser.add_argument("--step", type=int, help="solve the sat instance, with depths modulo step, default 1 (*)", default = 1)
  parser.add_argument("--twoway_sat", type=int, help="we use predecessor and sucessor cnot array to give global information locally (without bridges) [0/1], default 1", default = 1)
  parser.add_argument("--near_optimal", type=int, help="Adds bridges along with swaps, adds atmost k+1 bridges if k is optimal number of swaps [0/1], default 0", default = 0)
  parser.add_argument("--parallel_swaps", type=int, help="adds parallel swaps in each time step (bounded optimal) [0/1], default 0", default = 0)
  parser.add_argument("--constraints", type=int, help=textwrap.dedent('''
                               Three levels of sat encoding constraints:
                                 0 = removing any constraints will result in an incorrect encoding
                                 1 = extra clauses for pruning
                                 2 = extra binary clauses (redundant constraints), helps sat solver (default)'''), default = 2)
  parser.add_argument("--lp_connections", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                                 0 = auxiliary variables for logical physical connections
                                 1 = directly clauses on logical pair variables (default)
                                 2 = clauses to indicate distance'''), default = 1)
  parser.add_argument("--lp_distance", type=int, help="when set to -1, max swap distance is used otherwise restrictions are added until the number specified, default -1", default = -1)
  parser.add_argument("--group_cnots", type=int, help="if two consequent cnots act on same qubits, then we group them when enabled [0/1], default 0", default = 0)
  #parser.add_argument("--lower_bound", type=int, help="compute lower bound based on subgraphs: can result in near optimal solutions, default 0", default = 0, metavar="BOUND")
  parser.add_argument("--aux_files", help="location for intermediate files (default ./intermediate_files)", default = "./intermediate_files", metavar="DIR")
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                                 0 = only generate pddl files
                                 1 = computed mapped layout with swap gates
                                 2 = check resulting circuit for equivalence (default)'''), default = 2)
  parser.add_argument("-v", "--verbose", type=int, help="[-1/0/1/2/3], default=0, visual=1, extended=2, debug=3, silent=-1", default = 0)
  parser.add_argument("--version", help="show program version", action="store_true")
  args = parser.parse_args()

  try:
    git_label = subprocess.check_output(["git", "describe", "--always"], text=True).strip()
  except CalledProcessError:
    git_label = "Not under git"

  if args.version:
    print("Q-Synth - Optimal Quantum Layout Synthesis")
    print("(c) Irfansha Shaik, Jaco van de Pol, Aarhus, 2023")
    print(version)
    print("Git commit hash: " + git_label)
    exit(0)

  # find Benchmarks and Domains, 
  source_location = os.path.dirname(circuit_utils.__file__)
  args.benchmarks = os.path.join(source_location,"Benchmarks")
  args.domains    = os.path.join(source_location,"Domains")
  if args.circuit_in == None:
    args.circuit_in = os.path.join(args.benchmarks,"or.qasm")

  if (args.bridge == 1 and args.model != "sat"):
    args.model = "lifted"
    args.ancillary = 0
    args.relaxed = 0
    print("Experimental feature --bridge: switching to -m lifted, -a0, -r0")

  # choose default planner or sat-solver
  if args.model == "sat" and args.solver == None:
    args.solver = "cd15"
  if args.model != "sat" and args.solver == None:
    args.solver = "fd-bjolp"

  # we use intermediate directory for intermediate files:
  os.makedirs(args.aux_files, exist_ok=True)
  args.pddl_domain_out = os.path.join(args.aux_files, "domain.pddl")
  args.pddl_problem_out = os.path.join(args.aux_files, "problem.pddl")
  args.log_out = os.path.join(args.aux_files, "log_out")
  args.SAS_file = os.path.join(args.aux_files, "out.sas")
  args.plan_file = os.path.join(args.aux_files, "plan")

  if args.verbose > -1:
    print("Q-Synth - Optimal Quantum Layout Synthesis")
    print(f"{version}, git commit hash: " + git_label)
    print("arguments:")
    for key,val in vars(args).items():
      print(f"\t{key:26}{val}")
    print("Start time: " + str(datetime.datetime.now()))
  
  # --------------------------------------- Timing the encoding ----------------------------------------
  start_encoding_time = time.perf_counter()
 
  if args.model == "global":
    instance = glob(args)
  elif args.model == "local":
    instance = gloc(args)
  elif args.model == "lifted":
    instance = glip(args)
  elif args.model == "sat":
    if (args.bidirectional == 0):
      print("Error: sat encoding assumes bidirectional coupling graph")
      exit(-1)
    if (args.bridge == 0 and args.twoway_sat == 0):
      instance = se(args)
    elif (args.bridge == 0 and args.twoway_sat == 1):
      instance = setw(args)
    else:
      instance = seb(args)
  else:
    print(f"Error: model '{args.model}' not recognized")
    exit(-1)
  encoding_time = time.perf_counter() - start_encoding_time
  if args.verbose > -1:
    print("Encoding time: " + str(encoding_time))
  # ----------------------------------------------------------------------------------------------------

  if args.run >= 1 and args.model != "sat":
    # --------------------------------------- Timing the solver run ----------------------------------------
    start_run_time = time.perf_counter()

    # run external planner on pddl problems:
    run_instance = rp(args, instance)

    solving_time = time.perf_counter() - start_run_time
    if args.verbose > -1:
      print("Solving time: " + str(solving_time))
    # ------------------------------------------------------------------------------------------------------

  if args.run >= 1:
    # --------------------------------------- Timing the extraction ----------------------------------------
    start_extract_time = time.perf_counter()

    if args.model == "global":
      map_extract = ceg(args, instance, run_instance.plan)
    elif args.model == "local":
      map_extract = cel(args, instance, run_instance.plan)
    elif args.model == "lifted":
      map_extract = CircuitExtractionLifted(args, instance, run_instance.plan)
    elif args.model == "sat":
      map_extract = ces(args, instance)
    else:
      print(f"Error: cannot extract circuit with model {args.model}")

    extraction_time = time.perf_counter() - start_extract_time
    if args.verbose > -1:
      print("Extraction time: " + str(extraction_time))

    # ------------------------------------------------------------------------------------------------------
    # testing mapped circuit, if debugging is enabled (run>=2):
    # ------------------------------------------------------------------------------------------------------
    if args.run >= 2:

      start_test_time = time.perf_counter()
      TMC(instance, map_extract.map_unmap)
      extraction_time = time.perf_counter() - start_test_time
      if args.verbose > -1:
        print("Testing time: " + str(extraction_time))

  # ------------------------------------------------------------------------------------------------------    
  # we also do qiskit optimization when enabled:
  # TODO: this should be done BEFORE testing, but currently we cannot test the result...

    if args.qiskit_optimize > 0 or args.circuit_out != None:
      mapped_circuit = map_extract.map_unmap.get_measured_circuit()

    if args.qiskit_optimize > 0:
      start_opt_time = time.perf_counter()
      if args.bidirectional == 1:
        coupling_map = instance.bi_coupling_map
      else:
        coupling_map = instance.coupling_map

      initial_map = list(range(0, mapped_circuit.num_qubits)) # to keep the mapping as determined by Q-Synth

      mapped_circuit = qiskit_optimization(instance.input_circuit, mapped_circuit, coupling_map, initial_map,
                                                   args.qiskit_optimize, args.verbose)
      optimization_time = time.perf_counter() - start_opt_time
      print("Qiskit Optimization time: " + str(extraction_time))

  # ------------------------------------------------------------------------------------------------------

    # Finally, we write the circuit to output, if required:
    if (args.circuit_out != None):
      QuantumCircuit.qasm(mapped_circuit, filename=args.circuit_out)
      print(f"Output is written to {args.circuit_out}")

  # ------------------------------------------------------------------------------------------------------

  if args.verbose > -1:
    print("Finish time: " + str(datetime.datetime.now()))
