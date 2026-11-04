# csplib_032_max_density_still_life: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """In an n x m window of Conway's Game of Life, place as many live cells as possible so that
    the pattern does not change from one generation to the next. The board is infinite; cells
    outside the window are dead."""
    n = instance["n"]  # the number of rows of the window
    m = instance["m"]  # the number of columns of the window

    # alive[i][j] is true when the cell in row i, column j of the window is alive
    alive = [[Bool(f"alive_{i}_{j}") for j in range(m)] for i in range(n)]

    # Whether cell (i, j) lies in the window.
    def inside(i, j):
        return 0 <= i < n and 0 <= j < m

    # The number of live neighbours of cell (i, j). Cells outside the window are dead.
    def live_neighbours(i, j):
        return sum(
            alive[i + di][j + dj]
            for di in (-1, 0, 1)
            for dj in (-1, 0, 1)
            if (di, dj) != (0, 0) and inside(i + di, j + dj)
        )

    # The constraints of the model, collected as they are added.
    constraints = []

    # A live cell has 2 or 3 live neighbours, so it stays alive.
    for i in range(n):
        for j in range(m):
            n_live_neighbours = live_neighbours(i, j)
            constraints.append(If(alive[i][j], (n_live_neighbours >= 2) & (n_live_neighbours <= 3)))

    # A dead cell does not have exactly 3 live neighbours, so no cell is born. This covers the
    # window and the ring of dead cells just outside it.
    for i in range(-1, n + 1):
        for j in range(-1, m + 1):
            n_live_neighbours = live_neighbours(i, j)
            if inside(i, j):
                constraints.append(Or([alive[i][j], n_live_neighbours <= 2, n_live_neighbours >= 4]))
            else:
                constraints.append(Or([n_live_neighbours <= 2, n_live_neighbours >= 4]))

    # The number of live cells in the window, to maximise.
    density = sum(alive[i][j] for i in range(n) for j in range(m))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(density, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"grid": alive}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
