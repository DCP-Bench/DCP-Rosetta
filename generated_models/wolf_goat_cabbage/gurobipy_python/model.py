# wolf_goat_cabbage: a Gurobi (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A farmer ferries a wolf, a goat and a cabbage across a river in a boat that carries the farmer and at most one item, and must never leave the wolf alone with the goat or the goat alone with the cabbage. Find the crossings that take all three to the far shore."""
    stage = instance["stage"]  # how many positions the plan has: position 0 is the start, position stage - 1 the end
    stages = range(stage)

    model = gp.Model("wolf_goat_cabbage")

    # wolf[i], goat[i], cabbage[i] and boat[i] are 1 when that item (the boat stands for
    # the farmer) is on the destination shore at position i, and 0 on the starting shore.
    wolf = model.addVars(stages, vtype=GRB.BINARY, name="wolf")
    goat = model.addVars(stages, vtype=GRB.BINARY, name="goat")
    cabbage = model.addVars(stages, vtype=GRB.BINARY, name="cabbage")
    boat = model.addVars(stages, vtype=GRB.BINARY, name="boat")

    # Initial situation: everything on the starting shore.
    for v in (boat, wolf, goat, cabbage):
        model.addConstr(v[0] == 0)

    # Final situation: everything on the destination shore.
    for v in (boat, wolf, goat, cabbage):
        model.addConstr(v[stage - 1] == 1)

    # The boat crosses at every step: it changes shore between positions i - 1 and i.
    model.addConstrs((boat[i] + boat[i - 1] == 1 for i in range(1, stage)), name="boat_moves")

    # The wolf and the goat are never left on one shore without the farmer (the boat).
    # Each of these two lines forbids one shore on which they would be left alone.
    model.addConstrs((wolf[i] + goat[i] + (1 - boat[i]) >= 1 for i in stages), name="wolf_goat_start")
    model.addConstrs(((1 - wolf[i]) + (1 - goat[i]) + boat[i] >= 1 for i in stages), name="wolf_goat_dest")
    # The goat and the cabbage are never left alone on one shore, by the same two lines.
    model.addConstrs((goat[i] + cabbage[i] + (1 - boat[i]) >= 1 for i in stages), name="goat_cabbage_start")
    model.addConstrs(((1 - goat[i]) + (1 - cabbage[i]) + boat[i] >= 1 for i in stages), name="goat_cabbage_dest")

    # The boat carries the farmer and at most one item, so at most one of the wolf, goat and
    # cabbage changes shore at each crossing. moved[x, i] is 1 when item x changes shore between
    # positions i and i + 1. It is at least the size of that change, which for 0/1 values is 1
    # exactly when x changes shore.
    items = {"wolf": wolf, "goat": goat, "cabbage": cabbage}
    moved = model.addVars(list(items), range(stage - 1), vtype=GRB.BINARY, name="moved")
    model.addConstrs((moved[x, i] >= items[x][i] - items[x][i + 1] for x in items for i in range(stage - 1)), name="moved_back")
    model.addConstrs((moved[x, i] >= items[x][i + 1] - items[x][i] for x in items for i in range(stage - 1)), name="moved_forth")
    model.addConstrs((moved.sum("*", i) <= 1 for i in range(stage - 1)), name="one_moves")

    # The output: each item's shore at every position, from the start to the end.
    return model, {
        "wolf_pos": [wolf[i] for i in stages],
        "goat_pos": [goat[i] for i in stages],
        "cabbage_pos": [cabbage[i] for i in stages],
        "boat_pos": [boat[i] for i in stages],
    }


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
