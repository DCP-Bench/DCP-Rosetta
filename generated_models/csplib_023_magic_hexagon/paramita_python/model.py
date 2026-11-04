# csplib_023_magic_hexagon: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf

# The cells of the hexagon, row by row from the top: A to S.
CELLS = list("ABCDEFGHIJKLMNOPQRS")

# The 15 lines of cells: the 5 rows, the 5 lines running down to the left
# and the 5 running down to the right.
LINES = [
    "ABC", "DEFG", "HIJKL", "MNOP", "QRS",
    "HMQ", "DINR", "AEJOS", "BFKP", "CGL",
    "ADH", "BEIM", "CFJNQ", "GKOR", "LPS",
]


def create_model(instance):
    """Place the numbers 1 to NUM_CELLS, each once, in the cells of a hexagon so that
    each of the 15 lines of cells sums to MAGIC_SUM."""
    n = instance["NUM_CELLS"]      # the numbers to place: 1 to n
    magic = instance["MAGIC_SUM"]  # the sum each line of cells has to reach
    numbers = range(1, n + 1)

    # x[c][v] is true when cell c holds the number v
    x = {c: {v: Bool(f"x_{c}_{v}") for v in numbers} for c in CELLS}

    # Each cell holds exactly one number.
    constraints = [sum(x[c].values()) == 1 for c in CELLS]

    # Each number is in exactly one cell.
    constraints += [sum(x[c][v] for c in CELLS) == 1 for v in numbers]

    # value[c] is the number in cell c
    value = {c: sum(v * x[c][v] for v in numbers) for c in CELLS}

    # Each line of cells sums to the magic sum.
    constraints += [sum(value[c] for c in line) == magic for line in LINES]

    # The numbers in the cells A to S.
    outputs = {"LD": [value[c] for c in CELLS]}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
