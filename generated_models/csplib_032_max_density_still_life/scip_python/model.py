# csplib_032_max_density_still_life: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_032_max_density_still_life.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_032_max_density_still_life.py csplib_032_max_density_still_life.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Maximum density still life: choose which cells of an n x m active grid are alive
    so that the pattern is a still life and as many cells as possible are alive.

    A still life does not change from one generation to the next in Conway's Game of
    Life. A live cell has 2 or 3 live neighbours. A dead cell must not have exactly 3
    live neighbours, otherwise it would become alive. The board is infinite, and cells
    outside the active grid are dead, so the rule for dead cells applies to them too.
    """
    n = instance["n"]  # the number of rows of the active grid
    m = instance["m"]  # the number of columns of the active grid

    model = Model("max_density_still_life")

    # live[i, j] is 1 when cell (i, j) of the active grid is alive, and 0 when dead.
    # Each cell is a yes/no choice, so the variables are binary.
    live = model.addMatrixVar((n, m), vtype="B", name="live")

    def neighbours(i, j):
        # The live cells among the 8 cells around (i, j). Cells outside the grid are
        # dead, so they are left out of the sum.
        return quicksum(
            live[a, b]
            for a in range(i - 1, i + 2)
            for b in range(j - 1, j + 2)
            if (a, b) != (i, j) and 0 <= a < n and 0 <= b < m
        )

    # below[i, j] and above[i, j] are the two sides of the rule for a dead cell (i, j):
    # below = 1 allows the cell to have at most 2 live neighbours, and above = 1 allows
    # it to have at least 4. They are witnesses, not exact flags: a live cell may leave
    # both at 0. Both are binary because each side is a yes/no choice.
    below = model.addMatrixVar((n, m), vtype="B", name="below")
    above = model.addMatrixVar((n, m), vtype="B", name="above")

    for i in range(n):
        for j in range(m):
            # A live cell has 2 or 3 live neighbours. addConsIndicator takes only <= or
            # >=, not an equality, so the two bounds are two indicators on live[i, j].
            model.addConsIndicator(neighbours(i, j) >= 2, binvar=live[i, j])
            model.addConsIndicator(neighbours(i, j) <= 3, binvar=live[i, j])

            # A dead cell must not have exactly 3 live neighbours, so it has at most 2
            # or at least 4. The "not equal to 3" is written as this either-or, since
            # addCons has no !=. The last line makes a dead cell pick one side; a live
            # cell can pick none.
            model.addConsIndicator(neighbours(i, j) <= 2, binvar=below[i, j])
            model.addConsIndicator(neighbours(i, j) >= 4, binvar=above[i, j])
            model.addCons(live[i, j] + below[i, j] + above[i, j] >= 1)

    # The cells just outside the grid are dead, and must not have exactly 3 live
    # neighbours. A cell beside the middle of a side has 3 neighbours in the grid, so it
    # must not have all 3 alive: at most 2. A cell at the end of a side has only 2
    # neighbours in the grid, and a corner outside the grid has only 1, so neither can
    # have 3 and they need no rule.
    for j in range(1, m - 1):
        model.addCons(neighbours(-1, j) <= 2)
        model.addCons(neighbours(n, j) <= 2)
    for i in range(1, n - 1):
        model.addCons(neighbours(i, -1) <= 2)
        model.addCons(neighbours(i, m) <= 2)

    # Maximise the number of live cells in the active grid (the density of the pattern).
    model.setObjective(quicksum(live[i, j] for i in range(n) for j in range(m)), "maximize")

    return model, {"grid": live}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
