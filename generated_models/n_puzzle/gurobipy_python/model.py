# n_puzzle: a Gurobi (Python) model from DCP Rosetta.
# Download the `n_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python n_puzzle.py n_puzzle.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Slide the numbered tiles of a square sliding puzzle, one tile at a time into the empty
    square, so that the puzzle goes from its start state to its end state in exactly N_STEPS
    states, each different from the one before."""
    n_steps = instance["N_STEPS"]          # the number of states, the start and the end state included
    start = instance["puzzle_start"]       # start[i][j]: the tile in row i, column j at the start; 0 is the empty square
    end = instance["puzzle_end"]           # end[i][j]: the tile in row i, column j at the end; 0 is the empty square
    dim = len(start)                       # the board is dim by dim
    n = dim * dim - 1                      # the tiles are numbered 1..n, plus the empty square 0 (from the statement)
    cells = [(i, j) for i in range(dim) for j in range(dim)]
    steps = range(n_steps)                 # the states, numbered from 0

    def neighbours(i, j):
        # The cells the empty tile can slide to from (i, j): left, right, up, down.
        for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            if 0 <= i + di < dim and 0 <= j + dj < dim:
                yield i + di, j + dj

    model = gp.Model("n_puzzle")

    # x[t, i, j] is the tile (0 for the empty square) on cell (i, j) in state t. The first state is
    # the start state and the last state the end state, fixed through the variable bounds.
    x = {}
    # blank[t, i, j] is 1 when the empty square is on cell (i, j) in state t; 0 otherwise.
    blank = {}
    for t in steps:
        for (i, j) in cells:
            fixed = start[i][j] if t == 0 else end[i][j] if t == n_steps - 1 else None
            lo, hi = (fixed, fixed) if fixed is not None else (0, n)
            x[t, i, j] = model.addVar(lb=lo, ub=hi, vtype=GRB.INTEGER, name=f"x[{t},{i},{j}]")
            if fixed is not None:
                b = 1 if fixed == 0 else 0
                blank[t, i, j] = model.addVar(lb=b, ub=b, vtype=GRB.BINARY, name=f"blank[{t},{i},{j}]")
            else:
                blank[t, i, j] = model.addVar(vtype=GRB.BINARY, name=f"blank[{t},{i},{j}]")

    # The sum of the tile values is the same in every state (the tiles are 0..n in each), and in
    # the start state it is total.
    total = sum(start[i][j] for (i, j) in cells)

    # Each state has exactly one empty square.
    model.addConstrs((gp.quicksum(blank[t, i, j] for (i, j) in cells) == 1 for t in steps), name="one_blank")

    # Middle states only (the start and end states are fixed already): a cell holds 0 exactly when
    # the empty square is on it.
    middle = range(1, n_steps - 1)
    model.addConstrs((x[t, i, j] <= n * (1 - blank[t, i, j]) for t in middle for (i, j) in cells), name="zero")
    model.addConstrs((x[t, i, j] >= 1 - blank[t, i, j] for t in middle for (i, j) in cells), name="tile")
    # Every middle state holds the same tiles as the start state. Together with the constraints
    # below this keeps the tiles all different: the only cells that change are the old and the new
    # place of the empty square, and the new place becomes 0, so the old place must take the tile
    # that slid out of the new place.
    model.addConstrs((gp.quicksum(x[t, i, j] for (i, j) in cells) == total for t in middle), name="same_tiles")

    # Each step is one slide: from state t-1 to state t, the state must change (a tile slides into the
    # empty square) and only the cells where the empty square was or is now may change.
    steps_after_start = range(1, n_steps)
    # The empty square reaches (i, j) only from a neighbouring cell. Staying in place is excluded:
    # then no cell could change, and the state must change every step.
    model.addConstrs((blank[t, i, j] <= gp.quicksum(blank[t - 1, r, c] for (r, c) in neighbours(i, j))
                      for t in steps_after_start for (i, j) in cells), name="slide")
    # A cell outside the old and new places of the empty square keeps its tile. The change of a
    # tile is bounded by n, which is the largest tile value.
    moved = {(t, i, j): blank[t - 1, i, j] + blank[t, i, j] for t in steps_after_start for (i, j) in cells}
    model.addConstrs((x[t, i, j] - x[t - 1, i, j] <= n * moved[t, i, j]
                      for t in steps_after_start for (i, j) in cells), name="keep_up")
    model.addConstrs((x[t - 1, i, j] - x[t, i, j] <= n * moved[t, i, j]
                      for t in steps_after_start for (i, j) in cells), name="keep_down")

    # No objective: any sequence of slides that meets the constraints answers the puzzle.

    # The states, one 2-dimensional matrix per state (rows of tiles), from the start state to the end state.
    return model, {"steps": [[[x[t, i, j] for j in range(dim)] for i in range(dim)] for t in steps]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
