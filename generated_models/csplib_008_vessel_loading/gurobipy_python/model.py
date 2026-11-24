# csplib_008_vessel_loading: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_008_vessel_loading.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_008_vessel_loading.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_008_vessel_loading.py csplib_008_vessel_loading.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Place rectangular containers in a single layer on a rectangular deck, each lying parallel
    to the deck's sides, without overlap and with the required separation between certain classes."""
    deck_width = instance["deck_width"]    # the deck's extent along x; the deck runs from 0 to deck_width
    deck_length = instance["deck_length"]  # the deck's extent along y; the deck runs from 0 to deck_length
    width = instance["width"]              # width[i]: the width of container i
    length = instance["length"]            # length[i]: the length of container i
    classes = instance["classes"]          # classes[i]: the class of container i, numbered from 1
    separation = instance["separation"]    # separation[c][d]: the gap required between a class c+1 and a class d+1 container (0-based indices)
    containers = range(instance["n_containers"])  # the containers, numbered from 0

    model = gp.Model("vessel_loading")

    # left[i] and right[i] are the x positions of the two sides of container i, and bottom[i] and
    # top[i] its two y positions. Each side lies on the deck, so from 0 up to the deck's extent.
    left = model.addVars(containers, lb=0, ub=deck_width, vtype=GRB.INTEGER, name="left")
    right = model.addVars(containers, lb=0, ub=deck_width, vtype=GRB.INTEGER, name="right")
    bottom = model.addVars(containers, lb=0, ub=deck_length, vtype=GRB.INTEGER, name="bottom")
    top = model.addVars(containers, lb=0, ub=deck_length, vtype=GRB.INTEGER, name="top")

    # turned[i] is 1 when container i is turned, so that its width runs along y (the deck's length)
    # and its length along x; it is 0 when its width runs along x. Either way the rectangle is
    # width x length or length x width, so the two extents are linear in turned[i].
    turned = model.addVars(containers, vtype=GRB.BINARY, name="turned")
    # Each container's x extent is its width when it is not turned and its length when it is;
    # its y extent is the other one.
    model.addConstrs((right[i] - left[i] == width[i] + (length[i] - width[i]) * turned[i]
                      for i in containers), name="extent_x")
    model.addConstrs((top[i] - bottom[i] == length[i] + (width[i] - length[i]) * turned[i]
                      for i in containers), name="extent_y")

    # No overlap: for each pair of containers a < b, one of four branches holds, and branch[k] is 1
    # when it does: 0 a lies at least sep to the left of b, 1 to its right, 2 below it, 3 above it,
    # where sep is the separation required between their classes. The branch that does not hold is
    # switched off by a big-M: the deck extent along that axis plus sep, which is the most its
    # left side can exceed its right side by.
    for a in containers:
        for b in range(a + 1, len(width)):
            sep = separation[classes[a] - 1][classes[b] - 1]
            big_x = deck_width + sep
            big_y = deck_length + sep
            branch = model.addVars(4, vtype=GRB.BINARY, name=f"branch[{a},{b}]")
            model.addConstr(right[a] + sep <= left[b] + big_x * (1 - branch[0]), name=f"a_left_of_b[{a},{b}]")
            model.addConstr(left[a] >= right[b] + sep - big_x * (1 - branch[1]), name=f"a_right_of_b[{a},{b}]")
            model.addConstr(top[a] + sep <= bottom[b] + big_y * (1 - branch[2]), name=f"a_below_b[{a},{b}]")
            model.addConstr(bottom[a] >= top[b] + sep - big_y * (1 - branch[3]), name=f"a_above_b[{a},{b}]")
            # At least one of the four branches holds, so the pair does not overlap.
            model.addConstr(branch.sum() >= 1, name=f"separate[{a},{b}]")

    # No objective: any placement that meets the constraints answers the question.

    # The positions of the containers: for each container, its left, right, top and bottom sides, as lists over the containers.
    return model, {
        "left": [left[i] for i in containers],
        "right": [right[i] for i in containers],
        "top": [top[i] for i in containers],
        "bottom": [bottom[i] for i in containers],
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
