# csplib_012_nonogram: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Shade squares in a grid so that, in every row and every column, the blocks of consecutive
    shaded squares have the lengths given by its clue, in order, with at least one unshaded
    square between consecutive blocks."""
    row_rules = instance["row_rules"]  # row_rules[r]: the block lengths of row r, in order, padded with zeros
    col_rules = instance["col_rules"]  # col_rules[c]: the block lengths of column c, in order, padded with zeros
    n_rows = instance["rows"]  # the number of rows in the grid
    n_cols = instance["cols"]  # the number of columns in the grid

    model = gp.Model("csplib_012_nonogram")

    def add_line(cells, clue):
        """Make a line of squares show the blocks in clue, in order, with at least one unshaded
        square between consecutive blocks. cells[p] is 1 when square p of the line is shaded."""
        n = len(cells)  # the number of squares in the line
        blocks = [length for length in clue if length > 0]  # the block lengths; zeros in a clue are padding

        # start[k, p] is 1 when block k starts at square p of the line. A block must fit inside
        # the line, so p stops at n - length: a bound implied by the line length, not in the statement.
        keys = [(k, p) for k in range(len(blocks)) for p in range(n - blocks[k] + 1)]
        start = model.addVars(keys, vtype=GRB.BINARY, name="start")

        # The line shades exactly as many squares as its blocks total (implied by the clue).
        model.addConstr(gp.quicksum(cells) == sum(blocks), name="count")

        # Each block starts at exactly one square.
        model.addConstrs((gp.quicksum(start[k, p] for p in range(n - length + 1)) == 1
                          for k, length in enumerate(blocks)), name="one_start")

        # Square p is shaded exactly when some block covers it. A block starting at square q
        # covers squares q to q + length - 1.
        model.addConstrs((cells[p] == gp.quicksum(start[k, q]
                                                  for k, length in enumerate(blocks)
                                                  for q in range(max(0, p - length + 1),
                                                                 min(p, n - length) + 1))
                          for p in range(n)), name="covers")

        # Blocks come in order with a gap of at least one unshaded square: block k + 1 starts at
        # least length_k + 1 squares after block k starts.
        where = [gp.quicksum(q * start[k, q] for q in range(n - length + 1))
                 for k, length in enumerate(blocks)]  # where[k]: the square where block k starts
        model.addConstrs((where[k] + blocks[k] + 1 <= where[k + 1]
                          for k in range(len(blocks) - 1)), name="order")

    # shade[r, c] is 1 when the square in row r and column c is shaded, and 0 when it is not
    shade = model.addVars(n_rows, n_cols, vtype=GRB.BINARY, name="shade")

    # Each row shows the blocks its clue lists, in order.
    for r in range(n_rows):
        add_line([shade[r, c] for c in range(n_cols)], row_rules[r])

    # Each column shows the blocks its clue lists, in order.
    for c in range(n_cols):
        add_line([shade[r, c] for r in range(n_rows)], col_rules[c])

    # Satisfaction problem: any shading that meets every clue will do, so there is no objective.
    board = [[shade[r, c] for c in range(n_cols)] for r in range(n_rows)]  # board[r][c] is shade[r, c]

    return model, {"board": board}


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
