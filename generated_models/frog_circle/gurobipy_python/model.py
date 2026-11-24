# frog_circle: a Gurobi (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python frog_circle.py frog_circle.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Frog circle: arrange the cards 1 to n around a circle so that a frog starting on card 1 and jumping k places clockwise from card k lands on every card."""
    n = instance["n"]  # the number of cards, and of places round the circle
    places = range(n)
    cards = range(1, n + 1)

    model = gp.Model("frog_circle")

    # card_at[p, k] is 1 when card k lies at place p.
    card_at = model.addVars(places, cards, vtype=GRB.BINARY, name="card_at")
    # Each place holds exactly one card.
    model.addConstrs((card_at.sum(p, "*") == 1 for p in places), name="one_card")
    # Each card lies at exactly one place.
    model.addConstrs((card_at.sum("*", k) == 1 for k in cards), name="one_place")
    # x[p] is the card at place p.
    x = [gp.quicksum(k * card_at[p, k] for k in cards) for p in places]

    # Not in the statement: card 1 is put at place 0. Turning the circle maps a solution to
    # another solution, so this only picks one of the equal rotations.
    model.addConstr(card_at[0, 1] == 1, name="start_card")

    # From place p the frog jumps x[p] places clockwise, to place (p + x[p]) mod n, so a jump
    # from p to q needs card (q - p) mod n at p. jump[p, q] is 1 when the frog's first n - 1
    # jumps include the jump from p to q.
    jump = model.addVars([(p, q) for p in places for q in places if p != q], vtype=GRB.BINARY, name="jump")
    model.addConstrs((jump[p, q] <= card_at[p, (q - p) % n] for p, q in jump), name="jump_card")

    # The frog lands on every place, so its first n - 1 jumps form one path from place 0 through
    # all the places. Each place is left at most once and entered at most once, nothing jumps
    # back to place 0, and there are n - 1 jumps.
    model.addConstrs((jump.sum(p, "*") <= 1 for p in places), name="leave")
    model.addConstrs((jump.sum("*", p) <= 1 for p in places), name="arrive")
    model.addConstr(jump.sum("*", 0) == 0, name="no_return_to_start")
    model.addConstr(jump.sum() == n - 1, name="jump_count")

    # Not in the statement: step[p] is the number of the jump at which the frog reaches place p,
    # with place 0 at step 0. Each jump of the path raises the step by one, which rules out closed
    # loops of jumps. The upper bound n - 1 is also not from the statement: the path has n - 1 jumps.
    step = model.addVars(places, lb=0, ub=n - 1, vtype=GRB.INTEGER, name="step")
    model.addConstr(step[0] == 0, name="start_step")
    model.addConstrs(((jump[p, q] == 1) >> (step[q] == step[p] + 1) for p, q in jump), name="order")

    # No objective: any arrangement that meets the constraints is an answer.
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
