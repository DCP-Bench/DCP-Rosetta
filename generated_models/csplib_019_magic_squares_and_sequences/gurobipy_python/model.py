# csplib_019_magic_squares_and_sequences: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A magic sequence of length n is a sequence x[0] to x[n-1] of numbers between 0 and n-1 in which, for every i, the number i occurs exactly x[i] times."""
    n = instance["n"]  # the length of the sequence
    places = range(n)  # the positions 0 to n-1, and the values 0 to n-1 that an entry can take

    model = gp.Model("magic_sequence")

    # holds[p, v] is 1 when the entry at position p is the value v.
    # One-hot values let the occurrences be counted linearly.
    holds = model.addVars(places, places, vtype=GRB.BINARY, name="holds")
    # Each position holds exactly one value (holds.sum(p, "*") adds holds[p, v] over all values v).
    model.addConstrs((holds.sum(p, "*") == 1 for p in places), name="one_value")
    # x[p] is the value at position p, read from the one-hot choice.
    x = [gp.quicksum(v * holds[p, v] for v in places) for p in places]

    # The value i occurs exactly x[i] times (holds.sum("*", i) counts the positions holding i).
    model.addConstrs((holds.sum("*", i) == x[i] for i in places), name="occurs")

    # No objective: any sequence that meets the rules will do.
    return model, {"x": x}


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
