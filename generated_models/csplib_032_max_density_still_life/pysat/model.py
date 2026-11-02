# csplib_032_max_density_still_life: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from itertools import product

from pysat.formula import IDPool, WCNF


def create_model(instance):
    """In an n x m window of Conway's Game of Life, place as many live cells as possible so that
    the pattern does not change from one generation to the next. The board is infinite; cells
    outside the window are dead."""
    n = instance["n"]  # the number of rows of the window
    m = instance["m"]  # the number of columns of the window

    pool = IDPool()
    formula = WCNF()

    # grid[i][j] is true when the cell in row i, column j of the window is alive
    grid = [[pool.id(("grid", i, j)) for j in range(m)] for i in range(n)]

    # A live cell has 2 or 3 live neighbours and survives. A dead cell does not have exactly
    # 3 live neighbours, or it would come alive. Each combination of a cell and its neighbours
    # that breaks this rule is ruled out.
    for i in range(n):
        for j in range(m):
            neighbours = [grid[a][b]
                          for a in range(i - 1, i + 2) for b in range(j - 1, j + 2)
                          if (a, b) != (i, j) and 0 <= a < n and 0 <= b < m]
            for alive in (True, False):
                for values in product((True, False), repeat=len(neighbours)):
                    count = sum(values)
                    ok = count in (2, 3) if alive else count != 3
                    if not ok:
                        clause = [-grid[i][j] if alive else grid[i][j]]
                        clause += [-lit if v else lit for lit, v in zip(neighbours, values)]
                        formula.append(clause)

    # Cells just outside the window must not come alive either. A dead cell beside an edge
    # sees the (up to three) window cells next to it along that edge, and must not see
    # exactly three live ones. Cells diagonal to a corner see at most one window cell.
    border = []  # the window cells that one outside cell sees along an edge
    for j in range(m):
        cols = range(max(0, j - 1), min(m, j + 2))
        border.append([grid[0][b] for b in cols])
        border.append([grid[n - 1][b] for b in cols])
    for i in range(n):
        rows = range(max(0, i - 1), min(n, i + 2))
        border.append([grid[a][0] for a in rows])
        border.append([grid[a][m - 1] for a in rows])
    for cells in border:
        if len(cells) == 3:
            formula.append([-lit for lit in cells])

    # Each dead cell in the window costs 1, so the cheapest pattern has the most live cells.
    for row in grid:
        for lit in row:
            formula.append([lit], weight=1)

    return formula, {"grid": grid}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
