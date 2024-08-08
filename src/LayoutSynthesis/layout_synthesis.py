# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

import datetime
import time
import os
from pathlib import Path

from src.LayoutSynthesis.generate_global_pddl import GenerateGlobalPDDL as glob
from src.LayoutSynthesis.generate_lifted import GenerateLifted as glip
from src.LayoutSynthesis.generate_local import GenerateLocal as gloc
from src.LayoutSynthesis.sat_encoding import SatEncoding as se
from src.LayoutSynthesis.sat_encoding_twoway import SatEncodingTwoway as setw
from src.LayoutSynthesis.sat_encoding_bridges import SatEncodingBridges as seb
from src.LayoutSynthesis.run_planner import RunPlanner as rp
from src.LayoutSynthesis.circuit_extraction_global import CircuitExtractionGlobal as ceg
from src.LayoutSynthesis.circuit_extraction_local import CircuitExtractionLocal as cel
from src.LayoutSynthesis.circuit_extraction_lifted import CircuitExtractionLifted
from src.LayoutSynthesis.circuit_extraction_sat import CircuitExtractionSAT as ces
from src.LayoutSynthesis.testing_mapped_circuit import TestingMappedCircuit as TMC
from src.LayoutSynthesis.qiskit_optimization import qiskit_optimization
from src.CnotSynthesis.options import Options as op
from qiskit import QuantumCircuit

def layout_synthesis(circuit_in=None, circuit_out=None, platform="melbourne", model="sat", solver=None, solver_time=1800,
                     ancillary=1, relaxed=0, bidirectional=1, bridge=0, start=0, step=1, end=None, run=1, check_equivalence=0,
                     symmetry_breaking=0, verbose=0, distance_sb=0, initial=0, cnot_cancel=0, qiskit_optimize=0,
                     cardinality=1, twoway_sat=1, near_optimal=0, parallel_swaps=0, constraints=2,
                     lp_connections=1, lp_distance=-1, group_cnots=0, aux_files="./intermediate_files"):
  # TODO: add descriptions of arguments:
  # --------------------------------------- Creating args separately ---------------------------------------
  args = op()
  args.circuit_in = circuit_in
  args.circuit_out = circuit_out
  args.platform = platform
  args.bidirectional = bidirectional
  args.symmetry_breaking = symmetry_breaking
  args.distance_sb = distance_sb
  args.model = model
  args.ancillary = ancillary
  args.initial = initial
  args.relaxed = relaxed
  args.cnot_cancel = cnot_cancel
  args.qiskit_optimize = qiskit_optimize
  args.bridge = bridge
  args.time = solver_time
  args.solver = solver
  args.cardinality = cardinality
  args.start = start
  args.step = step
  args.end = end
  args.twoway_sat = twoway_sat
  args.near_optimal = near_optimal
  args.parallel_swaps = parallel_swaps
  args.constraints = constraints
  args.lp_connections = lp_connections
  args.lp_distance = lp_distance
  args.group_cnots = group_cnots
  args.aux_files = aux_files
  args.run = run
  args.check_equivalence = check_equivalence
  args.verbose = verbose
  # ----------------------------------------------------------------------------------------------------

  layout_synthesis_path = os.path.abspath(__file__)
  QSynth_path = Path(layout_synthesis_path).parent.parent.parent
  # find Benchmarks and Domains, 
  args.benchmarks = os.path.join(QSynth_path,"Benchmarks")
  args.domains    = os.path.join(QSynth_path,"src","LayoutSynthesis","Domains")
  if args.circuit_in == None:
    args.circuit_in = os.path.join(args.benchmarks,"ICCAD-23","or.qasm")

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
  if args.verbose > -1 and args.model != "sat":
    print("Encoding time: " + str(encoding_time))
  else:
    print("Encoding+Solving time: " + str(encoding_time))
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
  elif args.run >= 1 and args.model == "sat":
     # if a solution is not found, either due to timeout or end of the horizon,
     # we return withour extraction or optimization:
     if (instance.status == False) :
       print("Mapping not found")
       exit(-1)

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
    # testing mapped circuit, if equivalence check enabled:
    # ------------------------------------------------------------------------------------------------------
    if args.check_equivalence == 1:

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
