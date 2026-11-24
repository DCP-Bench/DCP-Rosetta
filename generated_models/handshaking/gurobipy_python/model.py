# handshaking: a Gurobi (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python handshaking.py handshaking.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Hilary and Jocelyn are married and host some couples. Guests shake hands, never with
    themselves or their own spouse. Jocelyn asks everyone else how many hands they shook and all
    the answers differ; find how many hands Hilary shook."""
    n = 2 + 2 * instance["num_couples"]  # the people: Hilary (0), Jocelyn (1), and the guests' couples
    people = range(n)
    # Spouses sit next to each other: 0 and 1, 2 and 3, and so on.
    spouse = [p + 1 if p % 2 == 0 else p - 1 for p in people]

    model = gp.Model("handshaking")

    # shake[i, j], for i < j, is 1 when i and j shook hands; nobody shakes hands
    # with themselves or their spouse, so those pairs have no variable at all.
    pairs = [(i, j) for i in people for j in range(i + 1, n) if j != spouse[i]]
    shake = model.addVars(pairs, vtype=GRB.BINARY, name="shake")

    # hands(p) is the number of hands person p shook: the handshakes that include p.
    def hands(p):
        return gp.quicksum(shake[i, j] for (i, j) in pairs if p in (i, j))

    # has[p, c] is 1 when person p shook exactly c hands. A count c runs from 0 to
    # n - 2, the most anyone can shake (everyone but themselves and their spouse).
    others = [p for p in people if p != 1]  # everyone Jocelyn asked: all but Jocelyn herself
    counts = range(n - 1)
    has = model.addVars(others, counts, vtype=GRB.BINARY, name="has")

    # Everyone Jocelyn asked (all but Jocelyn) shook a different number of hands. These are n - 1
    # people with counts in 0..n-2, so every count is used exactly once.
    # Each of these people has exactly one count.
    model.addConstrs((has.sum(p, "*") == 1 for p in others), name="one_count")
    # That count is the number of handshakes the person was in.
    model.addConstrs((hands(p) == gp.quicksum(c * has[p, c] for c in counts) for p in others), name="count")
    # Each count is used by exactly one person.
    model.addConstrs((has.sum("*", c) == 1 for c in counts), name="distinct")

    # hil is the number of hands Hilary shook. It is a variable of its own so that
    # the declared output is this one number, not every handshake behind it.
    hil = model.addVar(lb=0, ub=n - 2, vtype=GRB.INTEGER, name="hil")
    model.addConstr(hil == hands(0), name="hilary")

    return model, {"hil": hil}


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
