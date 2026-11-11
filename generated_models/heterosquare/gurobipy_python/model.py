# heterosquare: a Gurobi (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python heterosquare.py heterosquare.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Place the numbers 1 to n*n in an n-by-n square, each number exactly once, so that
    the n row sums, the n column sums and the two diagonal sums are all different."""
    n = instance["n"]  # the order of the square: n rows and n columns

    # The cells are numbered row by row: cell k is in row k // n and column k % n.
    cells = range(n * n)
    # The numbers to place: each of 1 to n*n is used exactly once.
    numbers = range(1, n * n + 1)

    # Each line of the square, listed by its cell numbers: the rows, then the columns,
    # then the main diagonal and the anti-diagonal.
    rows = [[r * n + c for c in range(n)] for r in range(n)]
    cols = [[r * n + c for r in range(n)] for c in range(n)]
    diagonals = [[i * n + i for i in range(n)], [i * n + (n - 1 - i) for i in range(n)]]
    lines = rows + cols + diagonals

    # Least and most a line of n distinct numbers from 1 to n*n can add to. These follow
    # from the numbers being distinct and in range; the statement does not give them.
    least = n * (n + 1) // 2
    most = n * n * n - n * (n - 1) // 2

    model = gp.Model("heterosquare")

    # place[k, v] is 1 when cell k holds the number v, and 0 when not
    place = model.addVars(cells, numbers, vtype=GRB.BINARY, name="place")
    # Each cell holds exactly one number.
    model.addConstrs((gp.quicksum(place[k, v] for v in numbers) == 1 for k in cells),
                     name="one_number_per_cell")
    # Each number is placed in exactly one cell, so the numbers are all distinct.
    model.addConstrs((gp.quicksum(place[k, v] for k in cells) == 1 for v in numbers),
                     name="each_number_once")

    # x[k] is the number in cell k, an integer from 1 to n*n, read off place
    x = [model.addVar(lb=1, ub=n * n, vtype=GRB.INTEGER, name=f"x_{k}") for k in cells]
    model.addConstrs((x[k] == gp.quicksum(v * place[k, v] for v in numbers) for k in cells),
                     name="number_in_cell")

    # total[j] is the sum of the numbers on line j (rows, columns, then the two diagonals)
    total = [model.addVar(lb=least, ub=most, vtype=GRB.INTEGER, name=f"sum_{j}")
             for j in range(len(lines))]
    model.addConstrs((total[j] == gp.quicksum(x[k] for k in lines[j])
                      for j in range(len(lines))), name="line_sums")

    # Every two line sums differ. below is 1 when total[i] is smaller than total[j], and 0
    # when it is larger; the two indicator constraints together say the sums differ.
    # (A loop, not one addConstrs: each pair needs its own switch variable.)
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            below = model.addVar(vtype=GRB.BINARY, name=f"below_{i}_{j}")
            model.addConstr((below == 1) >> (total[i] <= total[j] - 1), name=f"differ_{i}_{j}_a")
            model.addConstr((below == 0) >> (total[i] >= total[j] + 1), name=f"differ_{i}_{j}_b")

    # The square: square[r][c] is the number in row r, column c
    square = [[x[r * n + c] for c in range(n)] for r in range(n)]

    return model, {"x": square}


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
