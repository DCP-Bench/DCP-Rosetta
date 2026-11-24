# csplib_007_all_interval: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """All-interval series: order the pitch classes 0 to n-1 so that the n-1 steps between neighbours have sizes 1 to n-1, each used once."""
    n = instance["n"]  # the number of pitch classes, which is also the length of the series
    places = range(n)  # the positions 0 to n-1 of the series
    gaps = range(n - 1)  # the n-1 neighbouring pairs of positions
    pitches = range(n)  # the pitch classes 0 to n-1
    intervals = range(1, n)  # the intervals 1 to n-1 semitones

    model = gp.Model("all_interval")

    # note[i, v] is 1 when position i holds pitch class v: the series is a
    # permutation of 0..n-1.
    note = model.addVars(places, pitches, vtype=GRB.BINARY, name="note")
    # Each position holds exactly one pitch class.
    model.addConstrs((note.sum(i, "*") == 1 for i in places), name="place")
    # Each pitch class is used at exactly one position.
    model.addConstrs((note.sum("*", v) == 1 for v in pitches), name="pitch")
    # x[i] is the pitch class at position i.
    x = [gp.quicksum(v * note[i, v] for v in pitches) for i in places]

    # interval[i, d] is 1 when the i-th neighbouring pair is d apart: the intervals are a
    # permutation of 1..n-1.
    interval = model.addVars(gaps, intervals, vtype=GRB.BINARY, name="interval")
    # Each neighbouring pair has exactly one interval.
    model.addConstrs((interval.sum(i, "*") == 1 for i in gaps), name="gap")
    # Each interval 1 to n-1 occurs exactly once.
    model.addConstrs((interval.sum("*", d) == 1 for d in intervals), name="interval")
    # diffs[i] is the interval between positions i and i+1.
    diffs = [gp.quicksum(d * interval[i, d] for d in intervals) for i in gaps]

    # step[i] is the signed step x[i+1] - x[i] between neighbours, and size[i] is its
    # absolute value. The absolute value needs a variable, so the step gets its own.
    step = model.addVars(gaps, lb=-(n - 1), ub=n - 1, vtype=GRB.INTEGER, name="step")
    size = model.addVars(gaps, lb=0, ub=n - 1, vtype=GRB.INTEGER, name="size")
    model.addConstrs((step[i] == x[i + 1] - x[i] for i in gaps), name="step")
    model.addConstrs((size[i] == gp.abs_(step[i]) for i in gaps), name="size")
    # The interval between neighbours is the size of their step.
    model.addConstrs((size[i] == diffs[i] for i in gaps), name="distance")

    return model, {"x": x, "diffs": diffs}


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
