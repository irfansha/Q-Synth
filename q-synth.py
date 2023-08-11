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
from generate_local_initial import GenerateLocalInitial as gloi
from generate_local_strict import GenerateLocalStrict as glos
from run_planner import RunPlanner as rp
from circuit_extraction_global import CircuitExtractionGlobal as ceg
from circuit_extraction_local_initial import CircuitExtractionLocalOld as celi
from circuit_extraction_local import CircuitExtractionLocal as cel
from circuit_extraction_lifted import CircuitExtractionLifted
from testing_mapped_circuit import TestingMappedCircuit as TMC
from testing_mapped_circuit_new import TestingMappedCircuitNew as TMCnew
from subprocess import CalledProcessError
import circuit_utils

if __name__ == '__main__':
  version = "Version 1.0 - ICCAD 2023"
  text = f"Q-Synth - Optimal Quantum Layout Synthesis ({version})"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("circuit_in", help="input file: quantum circuit", metavar="INPUT.qasm", nargs="?")
  parser.add_argument("--circuit_out", help="output file: mapped quantum circuit (default None)", metavar="OUTPUT", default = None)
  parser.add_argument("-p", "--platform", help=textwrap.dedent('''\
                               Either provider name:
                                 tenerife  = FakeTenerife/IBM QX2, 5 qubit
                                 melbourne = FakeMelbourne, 14 qubit (default)
                                 tokyo     = FakeTokyo, 20 qubit
                               Or generated platforms:
                                 rigetti-{12,14} = various subgraphs of the rigetti platform
                                 star-{3,7}      = test with 3/7-legged star topology (need swaps before first cnot)
                                 cycle-5         = cycle of 5 qubits (good for testing use of ancillary bits)
                                 test            = test platform (can be anything for experimentation)
                               '''), default = "melbourne")
  parser.add_argument("-b", "--bidirectional", type=int, help="[0/1] make coupling bidirectional, default 1" ,default = 1)
  parser.add_argument("-m", "--model", help=textwrap.dedent('''\
                               Model type used for the encoding:
                                 global = uses global levels to ensure dependencies (with separate initial mapping)
                                 local  = local dependencies, grounded model with initial map integrated (default)
                                 lifted = non-grounded local model with integrated initial mapping
                                 local_initial  = local dependencies, grounded model with separate initial mapping
                                 lifted_initial = non-grounded local model with separate initial mapping'''), default = "local")
  parser.add_argument("-a", "--ancillary", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("-t", "--time", type=float, help="Solving time limit in seconds, default 1800 seconds", default = 1800)
  parser.add_argument("-s", "--solver", help=textwrap.dedent('''\
                               A planner tool combination:
                                 fdss-sat = seq-sat-fdss-2018
                                 fdss-opt = seq-opt-fdss-1
                                 fdss-opt-2 = seq-opt-fdss-2
                                 fd-bjolp = seq-opt-bjolp (default)
                                 fd-ms = seq-opt-merge-and-shrink
                                 fd-lmcut = fast downward with LM-cut heuristic
                                 M-seq = Madagascar sequential
                                 M-seq-optimal = Madagascar sequential, only optimal plans
                                 MpC = Madagascar C, with parallel plans'''), default="fd-bjolp")
  parser.add_argument("--aux_files", help="location for intermediate files (default ./intermediate_files)", default = "./intermediate_files", metavar="DIR")
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                                 0 = only generate pddl files
                                 1 = computed mapped layout with swap gates
                                 2 = check resulting circuit for equivalence (default)'''), default = 2)
  parser.add_argument("-v", "--verbose", type=int, help="[-1/0/1/2/3], default 0", default = 0)
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

  # find Benchmarks and Domains
  source_location = os.path.dirname(circuit_utils.__file__)
  args.benchmarks = os.path.join(source_location,"Benchmarks")
  args.domains    = os.path.join(source_location,"Domains")
  if args.circuit_in == None:
    args.circuit_in = os.path.join(args.benchmarks,"or.qasm")

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
    instance = glos(args)
  elif args.model == "local_initial":
    if (args.ancillary == 1):
      print("Error: --ancillary=1 is not implemented with local_initial")
      exit(-1)
    instance = gloi(args)
  elif args.model in ("lifted", "lifted_initial"):
    instance = glip(args)
  else:
    print(f"Error: model '{args.model}' not recognized")
    exit(-1)
  encoding_time = time.perf_counter() - start_encoding_time
  if args.verbose > -1:
    print("Encoding time: " + str(encoding_time))
  # ----------------------------------------------------------------------------------------------------

  if args.run >= 1:
    # --------------------------------------- Timing the solver run ----------------------------------------
    start_run_time = time.perf_counter()

    # run fastdownward on pddl problems:
    run_instance = rp(args,instance)

    solving_time = time.perf_counter() - start_run_time
    if args.verbose > -1:
      print("Solving time: " + str(solving_time))
    # ------------------------------------------------------------------------------------------------------

  if args.run >= 1:
    # --------------------------------------- Timing the extraction ----------------------------------------
    start_extract_time = time.perf_counter()

    if args.model == "global":
      map_extract = ceg(args,instance,run_instance.plan)
    elif args.model == "local":
      map_extract = cel(args,instance,run_instance.plan)
    elif "lifted" in args.model:
      map_extract = CircuitExtractionLifted(args,instance,run_instance.plan)
    elif args.model == "local_initial":
      map_extract = celi(args,instance,run_instance.plan)
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
      if "lifted" in args.model or args.model == "local":
        TMCnew(instance, map_extract.map_unmap)
      else:
        TMC(instance,map_extract.mapped_circuit, map_extract)
      extraction_time = time.perf_counter() - start_test_time
      if args.verbose > -1:
        print("Testing time: " + str(extraction_time))

  # ------------------------------------------------------------------------------------------------------

  if args.verbose > -1:
    print("Finish time: " + str(datetime.datetime.now()))
