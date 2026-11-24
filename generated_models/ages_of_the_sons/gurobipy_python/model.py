# ages_of_the_sons: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python ages_of_the_sons.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find the ages of an old man's three sons, oldest first. Their ages multiply to 36.
    The sum of the ages is the number of windows in a building the old man points to, which
    does not settle them; the clue that the oldest son has blue eyes does.
    """
    product = 36  # the product of the three ages, from the statement
    # No age is above 36: the ages multiply to 36 and none is 0 (implied by the statement, not a limit added to it).
    max_age = 36

    model = gp.Model("ages_of_the_sons")

    # Every triple of ages a >= b >= c from 0 to 36 whose product is 36. The product of three ages
    # is not linear, so the model chooses one triple from this table.
    triples = [(a, b, c) for a in range(max_age + 1) for b in range(a + 1) for c in range(b + 1)
               if a * b * c == product]

    # The answer. pick_a[i] is 1 when the sons' ages (oldest first) are options_a[i].
    # Only triples whose oldest son is strictly older than the second are options: the blue-eyes
    # clue singles out one oldest son. The statement does not say "strictly"; this is read from that clue.
    options_a = [t for t in triples if t[0] > t[1]]
    pick_a = model.addVars(len(options_a), vtype=GRB.BINARY, name="pick_a")
    model.addConstr(pick_a.sum() == 1, name="one_answer")
    # A[k] is the age of the (k+1)-th oldest son in the answer.
    A = [gp.quicksum(t[k] * pick_a[i] for i, t in enumerate(options_a)) for k in range(3)]

    # The rival. pick_b[i] is 1 when the mathematician's other candidate is options_b[i]: a triple
    # of ages with product 36 whose two oldest sons are twins. The blue-eyes clue rules such a
    # triple out, because it has no single oldest son.
    options_b = [t for t in triples if t[0] == t[1]]
    pick_b = model.addVars(len(options_b), vtype=GRB.BINARY, name="pick_b")
    model.addConstr(pick_b.sum() == 1, name="one_rival")
    # B[k] is the age of the (k+1)-th oldest son in the rival.
    B = [gp.quicksum(t[k] * pick_b[i] for i, t in enumerate(options_b)) for k in range(3)]

    # The rival has the same sum of ages as the answer: the number of windows did not settle it.
    model.addConstr(gp.quicksum(A) == gp.quicksum(B), name="same_sum")

    # The outputs are the ages of the answer, oldest first.
    return model, {"A1": A[0], "A2": A[1], "A3": A[2]}


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
