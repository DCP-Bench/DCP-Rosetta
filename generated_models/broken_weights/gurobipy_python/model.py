# broken_weights: a Gurobi (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python broken_weights.py broken_weights.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A weight of m pounds broke into n pieces, each a whole number of pounds. Find piece weights so that every whole number of pounds from 1 to m can be weighed on a balance scale, each piece placed on either pan or left off."""
    m = instance["m"]  # total mass of the original weight, in pounds; also the largest mass to weigh
    n = instance["n"]  # number of pieces the weight broke into
    masses = range(1, m + 1)  # every whole mass from 1 to m must be weighable
    pieces = range(n)

    model = gp.Model("broken_weights")

    # Not from the statement: a bound on every piece weight and every load. Each piece weighs at
    # least 1 pound and the pieces sum to m, so no piece weighs more than m - (n - 1).
    top = m - (n - 1)

    # weights[j] is the weight of piece j, in whole pounds. The lower bound 1 is not from the
    # statement: it says a piece has a positive weight.
    weights = model.addVars(pieces, lb=1, ub=top, vtype=GRB.INTEGER, name="weights")
    # The pieces together make up the whole weight of m pounds.
    model.addConstr(weights.sum() == m, name="total_mass")

    # For each mass t and piece j, exactly one of these is 1:
    # plus[t, j] when piece j is on the other pan from mass t (it helps balance t),
    # minus[t, j] when piece j is on the same pan as mass t (it counts against it),
    # off[t, j] when piece j is not used to weigh mass t.
    plus = model.addVars(masses, pieces, vtype=GRB.BINARY, name="plus")
    minus = model.addVars(masses, pieces, vtype=GRB.BINARY, name="minus")
    off = model.addVars(masses, pieces, vtype=GRB.BINARY, name="off")
    # load[t, j] is the signed contribution of piece j to weighing mass t: its weight when on the
    # other pan, minus its weight when on the mass's pan, and 0 when off the scale.
    load = model.addVars(masses, pieces, lb=-top, ub=top, vtype=GRB.INTEGER, name="load")
    model.addConstrs((plus[t, j] + minus[t, j] + off[t, j] == 1 for t in masses for j in pieces), name="one_sign")

    # The load of each piece follows its placement. Each case is an indicator constraint, which
    # keeps the product of the placement and the weight linear.
    model.addConstrs(((plus[t, j] == 1) >> (load[t, j] == weights[j]) for t in masses for j in pieces), name="plus_load")
    model.addConstrs(((minus[t, j] == 1) >> (load[t, j] == -weights[j]) for t in masses for j in pieces), name="minus_load")
    model.addConstrs(((off[t, j] == 1) >> (load[t, j] == 0) for t in masses for j in pieces), name="off_load")

    # The loads of the pieces balance mass t: their sum is exactly t pounds.
    model.addConstrs((load.sum(t, "*") == t for t in masses), name="weigh")

    # No objective: the question asks only for piece weights that work, so any feasible answer will do.

    return model, {"weights": [weights[j] for j in pieces]}


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
