# huey_dewey_louie: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python huey_dewey_louie.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Huey, Dewey and Louie make three statements about who is guilty. They cannot lie, so all three statements are true. Find who, if anyone, is guilty."""
    model = gp.Model("huey_dewey_louie")

    # Each variable is 1 when that nephew is guilty, and 0 when not. The problem has no instance data.
    huey = model.addVar(vtype=GRB.BINARY, name="huey")
    dewey = model.addVar(vtype=GRB.BINARY, name="dewey")
    louie = model.addVar(vtype=GRB.BINARY, name="louie")

    # Huey: Dewey and Louie have an equal share in it, so if one is guilty, so is the other.
    model.addConstr(dewey == louie, name="huey_says")

    # Dewey: if Huey is guilty, then so am I.
    model.addConstr(huey <= dewey, name="dewey_says")

    # Louie: Dewey and I are not both guilty.
    model.addConstr(dewey + louie <= 1, name="louie_says")

    return model, {"huey": huey, "dewey": dewey, "louie": louie}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded
