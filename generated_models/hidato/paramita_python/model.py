# hidato: a Paramita (Python) model from DCP Rosetta.
# Download the `hidato.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python hidato.py hidato.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Or, add_to_container, to_cnf


def create_model(instance):
    """Fill a square grid with the numbers 1 to side*side, each once, so that every
    number touches the next one horizontally, vertically or diagonally. Some numbers
    are given in their cells."""
    puzzle = instance["puzzle"]  # puzzle[i][j] is the number given in cell (i, j), or 0 if the cell is empty
    side = len(puzzle)
    n_cells = side * side
    numbers = range(1, n_cells + 1)
    cells = [(i, j) for i in range(side) for j in range(side)]

    # x[(i, j)][v] is true when cell (i, j) holds the number v
    x = {(i, j): {v: Bool(f"x_{i}_{j}_{v}") for v in numbers} for i, j in cells}

    # the rules of the puzzle, collected below
    constraints = []

    # Each cell holds exactly one number.
    for c in cells:
        constraints.append(sum(x[c][v] for v in numbers) == 1)

    # Each number is placed in exactly one cell.
    for v in numbers:
        constraints.append(sum(x[c][v] for c in cells) == 1)

    # The given numbers stay in their cells.
    for i, j in cells:
        if puzzle[i][j] != 0:
            constraints.append(x[(i, j)][puzzle[i][j]])

    # Each number touches the next one: if k is in a cell, then k + 1 is in one of
    # the cells next to it, horizontally, vertically or diagonally.
    for i, j in cells:
        # the cells next to (i, j)
        neighbours = [
            (i + di, j + dj)
            for di in (-1, 0, 1)
            for dj in (-1, 0, 1)
            if (di, dj) != (0, 0) and 0 <= i + di < side and 0 <= j + dj < side
        ]
        for k in range(1, n_cells):
            constraints.append(~x[(i, j)][k] | Or([x[d][k + 1] for d in neighbours]))

    # the number in each cell of the solved grid
    grid = [[sum(v * x[(i, j)][v] for v in numbers) for j in range(side)] for i in range(side)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"x": grid}


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
