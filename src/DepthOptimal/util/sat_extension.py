import argparse
from pysat.formula import CNF
from pysat.solvers import (
    Cadical153,
    Glucose42,
    MapleChrono,
    MapleCM,
    Maplesat,
    Mergesat3,
    Minicard,
    MinisatGH,
)

# TODO:
# Convert these into q-synth notation

solvers: dict = {
    "cadical": Cadical153(),
    "glucose": Glucose42(),
    "maple_chrono": MapleChrono(),
    "maple_cm": MapleCM(),
    "maplesat": Maplesat(),
    "mergesat": Mergesat3(),
    "minicard": Minicard(),
    "minisat": MinisatGH(),
}

parser = argparse.ArgumentParser(
    description="This is a wrapper for the pysat library",
    prog="python src/sat_extension.py",
)

parser.add_argument(
    "-s",
    "--solver",
    type=str,
    help=f"the underlying solver: {', '.join(solvers.keys())}",
    default="glucose",
)

parser.add_argument(
    "input",
    type=str,
    help="the path to the input (cnf) file",
)

args = parser.parse_args()

formula = CNF(from_file=args.input)
solver = solvers[args.solver]
solver.append_formula(formula.clauses)
if solver.solve():
    solution = solver.get_model()
    print(f"SAT: {solution}")
    exit(0)
else:
    exit(1)
