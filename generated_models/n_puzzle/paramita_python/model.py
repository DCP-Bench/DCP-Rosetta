# n_puzzle: a Paramita (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python n_puzzle.py n_puzzle.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """N-puzzle: on an n x n grid with the tiles 1 to n*n-1 and one empty square (tile 0),
    trace the steps from the start picture to the end picture. Each step slides one tile
    into the empty square, and the picture changes at every step."""
    start = instance["puzzle_start"]  # start[r][c]: the tile in row r, column c at the start
    end = instance["puzzle_end"]      # end[r][c]: the tile in row r, column c at the end
    n_steps = instance["N_STEPS"]     # number of pictures, counting the start and the end
    n = len(start)                    # the grid is n x n
    n_values = n * n                  # tiles 0 (the empty square) to n*n-1
    cells = [(r, c) for r in range(n) for c in range(n)]

    # holds[s][r][c][v] is true when cell (r, c) holds tile v in picture s
    holds = [[[[Bool(f"p_{s}_{r}_{c}_{v}") for v in range(n_values)]
               for c in range(n)]
              for r in range(n)]
             for s in range(n_steps)]

    def at(s, q, v):
        # the Bool that cell q holds tile v in picture s
        return holds[s][q[0]][q[1]][v]

    # Cells q and q2 are neighbours when they share an edge.
    def adjacent(q, q2):
        return abs(q[0] - q2[0]) + abs(q[1] - q2[1]) == 1

    constraints = []

    # Every cell of every picture holds exactly one tile.
    for s in range(n_steps):
        for q in cells:
            constraints.append(sum(at(s, q, v) for v in range(n_values)) == 1)

    # Every picture holds each tile in exactly one cell.
    for s in range(n_steps):
        for v in range(n_values):
            constraints.append(sum(at(s, q, v) for q in cells) == 1)

    # The first picture is the start picture.
    for r in range(n):
        for c in range(n):
            constraints.append(at(0, (r, c), start[r][c]))

    # The last picture is the end picture.
    for r in range(n):
        for c in range(n):
            constraints.append(at(n_steps - 1, (r, c), end[r][c]))

    # A step slides one tile into the empty square: a tile moves to a neighbouring cell
    # and the empty square moves into the cell the tile left.
    for s in range(n_steps - 1):
        for q in cells:
            for q2 in cells:
                if q == q2:
                    continue
                if not adjacent(q, q2):
                    # a tile cannot jump to a cell that is not next to it
                    for v in range(n_values):
                        constraints.append(~(at(s, q, v) & at(s + 1, q2, v)))
                    continue
                for v in range(1, n_values):
                    constraints.append(If(at(s, q, v) & at(s + 1, q2, v),
                                          at(s, q2, 0) & at(s + 1, q, 0)))

    # The empty square is in a different cell in every two consecutive pictures.
    for s in range(n_steps - 1):
        for q in cells:
            constraints.append(~(at(s, q, 0) & at(s + 1, q, 0)))

    # steps[s][r][c]: the tile in row r, column c of picture s, 0 for the empty square
    steps = [[[sum(v * at(s, (r, c), v) for v in range(n_values))
               for c in range(n)]
              for r in range(n)]
             for s in range(n_steps)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"steps": steps}


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
