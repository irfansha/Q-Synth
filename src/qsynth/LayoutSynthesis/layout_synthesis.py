# (C) CC-BY Irfansha Shaik, Jaco van de Pol, Aarhus University, 2023

import datetime
import time
import os
from pathlib import Path

from typing import Optional

from qsynth.LayoutSynthesis.generate_global_pddl import GenerateGlobalPDDL as glob
from qsynth.LayoutSynthesis.generate_lifted import GenerateLifted as glip
from qsynth.LayoutSynthesis.generate_local import GenerateLocal as gloc
from qsynth.LayoutSynthesis.sat_encoding_twoway import SatEncodingTwoway as setw
from qsynth.LayoutSynthesis.sat_encoding_bridges import SatEncodingBridges as seb
from qsynth.LayoutSynthesis.run_planner import RunPlanner as rp
from qsynth.LayoutSynthesis.circuit_extraction_global import (
    CircuitExtractionGlobal as ceg,
)
from qsynth.LayoutSynthesis.circuit_extraction_local import (
    CircuitExtractionLocal as cel,
)
from qsynth.LayoutSynthesis.circuit_extraction_lifted import CircuitExtractionLifted
from qsynth.LayoutSynthesis.circuit_extraction_sat import (
    CircuitExtractionSAT as ces,
)
from qsynth.LayoutSynthesis.testing_mapped_circuit import (
    TestingMappedCircuit as TMC,
)
from qsynth.CnotSynthesis.options import Options as op
from qiskit import QuantumCircuit, qasm2
from qsynth.Utilities.result import MappingResult


def layout_synthesis(
    circuit_in=None,
    circuit_out=None,
    platform="melbourne",
    model="sat",
    solver=None,
    solver_time=1800,
    allow_ancillas=True,
    relaxed=0,
    bidirectional=1,
    bridge=0,
    start=None,
    step=1,
    end=None,
    check=0,
    verbose=0,
    cnot_cancel=0,
    cardinality=1,
    parallel_swaps=0,
    aux_files="./intermediate_files",
    coupling_graph=None,
    initial_mapping: Optional[dict[int, int]] = None,
    search_strategy: str = "forward",
) -> Optional[tuple[QuantumCircuit, int]]:
    # TODO: add descriptions of arguments:
    # --------------------------------------- Creating args separately ---------------------------------------
    args = op()
    args.circuit_in = circuit_in
    args.circuit_out = circuit_out
    args.platform = platform
    args.bidirectional = bidirectional
    args.model = model
    args.allow_ancillas = allow_ancillas
    args.relaxed = relaxed
    args.cnot_cancel = cnot_cancel
    args.bridge = bridge
    args.time = solver_time
    args.solver = solver
    args.cardinality = cardinality
    args.start = start
    args.step = step
    args.end = end
    args.parallel_swaps = parallel_swaps
    args.aux_files = aux_files
    args.check = check
    args.verbose = verbose
    args.coupling_graph = coupling_graph
    args.initial_mapping = initial_mapping
    args.search_strategy = search_strategy
    # ----------------------------------------------------------------------------------------------------

    layout_synthesis_path = os.path.abspath(__file__)
    QSynth_path = Path(layout_synthesis_path).parent.parent.parent.parent
    args.domains = os.path.join(
        QSynth_path, "src", "qsynth", "LayoutSynthesis", "Domains"
    )

    # If initial mapping is specified, Only use SAT encoding (without bridges and ancillas):
    if args.initial_mapping is not None:
        if args.model != "sat":
            print(
                "Warning: Initial mapping is specified, but model is not sat. Switching to -m sat (without bridges)"
            )
        args.model = "sat"
        args.bridge = 0
    # If search strategy is backwards, we disable bridges and set model to set encoding:
    if search_strategy == "backward":
        if args.model != "sat":
            print(
                "Warning: Search strategy is backward, but model is not sat. Switching to -m sat (without bridges)"
            )
        args.model = "sat"
        args.bridge = 0
        assert args.start != None, "Upper bound for backward search must be specified"
    else:
        assert (
            search_strategy == "forward"
        ), "Search strategy must be either 'forward' or 'backward'"
        # If search strategy is forward, we set start to zero If not specified:
        if args.start is None:
            args.start = 0

    if args.bridge == 1 and args.model != "sat":
        args.model = "lifted"
        args.allow_ancillas = False
        args.relaxed = 0
        print("Experimental feature --bridge: switching to -m lifted, -a0, -r0")

    # choose default planner or sat-solver
    if args.solver == None:
        if args.model == "sat":
            args.solver = "cd19"
        if args.model != "sat":
            args.solver = "fd-bjolp"

    # we use intermediate directory for intermediate files:
    os.makedirs(args.aux_files, exist_ok=True)
    args.pddl_domain_out = os.path.join(args.aux_files, "domain.pddl")
    args.pddl_problem_out = os.path.join(args.aux_files, "problem.pddl")
    args.log_out = os.path.join(args.aux_files, "log_out")
    args.SAS_file = os.path.join(args.aux_files, "out.sas")
    args.plan_file = os.path.join(args.aux_files, "plan")

    # --------------------------------------- Timing the encoding ----------------------------------------
    args.start_encoding_time = time.perf_counter()

    if args.model == "global":
        instance = glob(args)
    elif args.model == "local":
        instance = gloc(args)
    elif args.model == "lifted":
        instance = glip(args)
    elif args.model == "sat":
        if args.bidirectional == 0:
            print("Error: sat encoding assumes bidirectional coupling graph")
            exit(-1)
        if args.bridge == 0:
            instance = setw(args)
        else:
            instance = seb(args)
    else:
        print(f"Error: model '{args.model}' not recognized")
        return None
    encoding_time = time.perf_counter() - args.start_encoding_time
    if args.verbose > 0:
        if args.model != "sat":
            print("Encoding time: " + str(encoding_time))
        else:
            print("Encoding+Solving time: " + str(encoding_time))
    # ----------------------------------------------------------------------------------------------------

    if args.model != "sat":
        # --------------------------------------- Timing the solver run ----------------------------------------
        start_run_time = time.perf_counter()

        # run external planner on pddl problems:
        run_instance = rp(args, instance)

        solving_time = time.perf_counter() - start_run_time
        if args.verbose > 0:
            print("Solving time: " + str(solving_time))

        if run_instance.plan == None:
            if args.verbose > -1:
                print("Mapping not found")
            return None

        # ------------------------------------------------------------------------------------------------------
    elif args.model == "sat":
        # if a solution is not found, either due to timeout or end of the horizon,
        # we return without extraction or optimization:
        if instance.status == False:
            if args.verbose > -1:
                print("Mapping not found")
            return None

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
    if args.verbose > 0:
        print("Extraction time: " + str(extraction_time))

    # extracted mapped circuit (without measurements):
    mapped_circuit = map_extract.map_unmap.get_mapped_circuit()
    # ------------------------------------------------------------------------------------------------------
    # testing mapped circuit, if equivalence check enabled:
    # ------------------------------------------------------------------------------------------------------
    if args.check == 1:

        start_test_time = time.perf_counter()
        TMC(instance, map_extract.map_unmap)
        extraction_time = time.perf_counter() - start_test_time
        if args.verbose > 0:
            print("Testing time: " + str(extraction_time))

    # ------------------------------------------------------------------------------------------------------

    # Finally, we write the circuit to output, if required:
    if args.circuit_out != None:
        qasm2.dump(mapped_circuit, args.circuit_out)
        print(f"Output is written to {args.circuit_out}")

    # ------------------------------------------------------------------------------------------------------

    if args.verbose > 0:
        print("Finish time: " + str(datetime.datetime.now()))

    # Get swap count
    swap_count = 0
    ops = mapped_circuit.count_ops()
    if "swap" in ops.keys():
        swap_count = ops["swap"]

    mapped_result = MappingResult(
        circuit=mapped_circuit,
        initial_mapping=map_extract.map_unmap.initial_mapping,
        final_mapping=map_extract.map_unmap.logical_physical_map,
        opt_val=swap_count,
    )

    # Return mapped result
    return mapped_result
