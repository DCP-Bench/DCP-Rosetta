# csplib_076_costas_arrays: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Costas array: place n marks on an n-by-n grid, one mark in each row and each column, so that the vectors between every pair of marks are all different."""
    n = instance["n"]  # the size of the grid, and the number of marks
    positions = range(n)  # the columns, numbered 0 to n-1 here
    values = range(1, n + 1)  # the rows, numbered 1 to n
    # The difference of two rows lies between -(n-1) and n-1; the difference triangle of the
    # statement takes its values from this range (a bound the model needs; not stated in the statement).
    diffs = range(-(n - 1), n)

    model = gp.Model("costas_arrays")

    # mark[i, v] is 1 when the mark in column i is in row v.
    mark = model.addVars(positions, values, vtype=GRB.BINARY, name="mark")
    # One mark in each column.
    model.addConstrs((mark.sum(i, "*") == 1 for i in positions), name="column")
    # One mark in each row: the rows are a permutation of 1..n.
    model.addConstrs((mark.sum("*", v) == 1 for v in values), name="row")
    # costas[i] is the row of the mark in column i, so costas lists the marks in column order.
    costas = [gp.quicksum(v * mark[i, v] for v in values) for i in positions]

    # The difference triangle: for each distance l, the difference costas[i + l] - costas[i]
    # between the marks l columns apart, for every start i. (The statement writes the
    # difference the other way round, X_i - X_{i+l}; the sign does not change which rows are equal.)
    # gap[l, i, d] is 1 when that difference equals d; exactly one d holds for each entry.
    gap = model.addVars(
        [(l, i, d) for l in range(1, n) for i in range(n - l) for d in diffs],
        vtype=GRB.BINARY, name="gap",
    )
    for l in range(1, n):
        for i in range(n - l):
            model.addConstr(gp.quicksum(gap[l, i, d] for d in diffs) == 1, name=f"one_gap[{l},{i}]")
            model.addConstr(
                costas[i + l] - costas[i] == gp.quicksum(d * gap[l, i, d] for d in diffs),
                name=f"gap_value[{l},{i}]",
            )

    # Costas condition: in each row of the difference triangle (the entries for one distance l)
    # no difference value occurs twice, so no two pairs of marks have the same vector.
    # The row for distance n - 1 has a single entry and needs no constraint.
    model.addConstrs((gp.quicksum(gap[l, i, d] for i in range(n - l)) <= 1
                      for l in range(1, n - 1) for d in diffs), name="distinct")

    # No objective: any arrangement that meets the rules is a solution.
    return model, {"costas": costas}


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
