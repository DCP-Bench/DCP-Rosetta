# flow_free_game: a PySAT (Python) model from DCP Rosetta.
# Download the `flow_free_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python flow_free_game.py flow_free_game.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

N_COLORS = 10  # the colours are numbered 1 to 10


def create_model(instance):
    """Flow Free: fill every cell of a board with a colour so that each colour forms one pipe.
    A given cell is an end of its pipe and touches exactly one cell of its colour. An empty
    cell lies in the middle of a pipe and touches exactly two cells of its colour."""
    board = instance["board"]  # board[i][j]: the colour of the cell, or 0 if it is empty
    n_rows = len(board)
    n_cols = len(board[0])

    pool = IDPool()

    # B[i][j] is the colour of the cell in row i and column j.
    B = [[Integer(f"B{i}_{j}", 1, N_COLORS, vpool=pool) for j in range(n_cols)]
         for i in range(n_rows)]
    engine = IntegerEngine(vars=[cell for row in B for cell in row], vpool=pool)
    cnf = engine.clausify()

    cells = [(i, j) for i in range(n_rows) for j in range(n_cols)]

    def neighbours(i, j):
        # The cells directly above, below, left and right of (i, j).
        return [(k, l) for (k, l) in cells if abs(k - i) + abs(l - j) == 1]

    # same[(p, q)] is true exactly when the side-by-side cells p and q have the same colour.
    # One such variable serves both cells.
    same = {}

    def same_colour(p, q):
        key = (min(p, q), max(p, q))
        if key not in same:
            literal = pool.id(("same", key))
            x, y = B[key[0][0]][key[0][1]], B[key[1][0]][key[1][1]]
            for color in range(1, N_COLORS + 1):
                cnf.append([-x.equals(color), -y.equals(color), literal])
                for other in range(1, N_COLORS + 1):
                    if other != color:
                        cnf.append([-literal, -x.equals(color), -y.equals(other)])
            same[key] = literal
        return same[key]

    for i, j in cells:
        # Which neighbours of the cell share its colour.
        touching = [same_colour((i, j), q) for q in neighbours(i, j)]
        if board[i][j] != 0:
            # A given cell keeps its colour and touches exactly one cell of that colour,
            # the next cell of its pipe.
            cnf.append([B[i][j].equals(board[i][j])])
            cnf.extend(CardEnc.equals(lits=touching, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
        else:
            # An empty cell touches exactly two cells of its colour, the previous and the
            # next cell of its pipe.
            cnf.extend(CardEnc.equals(lits=touching, bound=2, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    return cnf, {"B": B}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
