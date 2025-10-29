import argparse, textwrap

from pysat.formula import CNF
from pysat.solvers import Solver

if __name__ == "__main__":
    text = "A wrapper for Pysat solvers"
    parser = argparse.ArgumentParser(
        description=text, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--cnf", help="input cnf path")
    parser.add_argument(
        "--solver",
        help="pysat solver to use",
        default="cd19",
    )
    args = parser.parse_args()
    input_cnf = CNF(from_file=args.cnf)

    with Solver(use_timer=True, name=args.solver) as s:
        s.append_formula(input_cnf)
        if s.solve():
            print(" ".join(map(str, s.get_model())))
            # exit with code 10:
            exit(10)
        else:
            print("UNSAT")
            # exit with code 20:
            exit(20)
