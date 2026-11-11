# session5_climbing_stairs: a Gurobi (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Climb a stair of n steps in moves of between m1 and m2 steps each; once the top is
    reached, the remaining moves take no steps."""
    n, m1, m2 = instance["n"], instance["m1"], instance["m2"]  # the stair's steps, the smallest and largest move
    moves = range(n)  # at most n moves, since a move that is taken climbs at least one step

    model = gp.Model("climbing_stairs")

    # steps[i] is the number of steps climbed at move i: between m1 and m2 for a move that is taken,
    # and 0 once the top is reached.
    steps = model.addVars(moves, lb=0, ub=m2, vtype=GRB.INTEGER, name="steps")
    # moving[i] is 1 when move i is taken (climbs at least one step), and 0 when it is not.
    moving = model.addVars(moves, vtype=GRB.BINARY, name="moving")

    # The moves climb the whole stair.
    model.addConstr(steps.sum() == n, name="total")

    # A move that is taken climbs between m1 and m2 steps; a move that is not taken climbs none.
    # max(m1, 1) keeps moving[i] at 1 only for a move that really climbs a step, even when m1 is 0.
    model.addConstrs((steps[i] >= max(m1, 1) * moving[i] for i in moves), name="at_least")
    model.addConstrs((steps[i] <= m2 * moving[i] for i in moves), name="at_most")

    # Once a move takes no steps, every later move takes none too.
    model.addConstrs((moving[i] <= moving[i - 1] for i in range(1, n)), name="trailing_zeros")

    # No objective: any sequence of moves that meets the constraints answers the question.

    # The number of steps climbed at each move, as a list of n integers.
    return model, {"steps": [steps[i] for i in moves]}


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
