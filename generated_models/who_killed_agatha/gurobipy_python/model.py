# who_killed_agatha: a Gurobi (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python who_killed_agatha.py who_killed_agatha.json

import gurobipy as gp
from gurobipy import GRB

# The three people named in the statement, as their positions in the list of residents
# in the instance: Agatha is 0, the butler 1 and Charles 2.
AGATHA, BUTLER, CHARLES = 0, 1, 2


def create_model(instance):
    """Aunt Agatha was killed by one of the three residents of Dreadsbury Mansion (Agatha, the butler and Charles); deduce who, from the statement's rules about hatred and wealth."""
    names = instance["names"]  # names[i]: the name of resident i; the model uses only how many there are
    n = len(names)
    people = range(n)

    model = gp.Model("who_killed_agatha")

    # hates[i, j] is 1 when i hates j.
    hates = model.addVars(n, n, vtype=GRB.BINARY, name="hates")
    # richer[i, j] is 1 when i is richer than j.
    richer = model.addVars(n, n, vtype=GRB.BINARY, name="richer")
    # is_killer[i] is 1 when i killed Agatha.
    is_killer = model.addVars(n, vtype=GRB.BINARY, name="is_killer")

    # Someone killed Agatha, and only one resident did.
    model.addConstr(is_killer.sum() == 1, name="one_killer")

    # A killer always hates his victim, Agatha, and is no richer than she is.
    model.addConstrs((is_killer[i] <= hates[i, AGATHA] for i in people), name="killer_hates")
    model.addConstrs((is_killer[i] <= 1 - richer[i, AGATHA] for i in people), name="killer_not_richer")

    # Nobody is richer than himself.
    model.addConstrs((richer[i, i] == 0 for i in people), name="not_richer_than_self")
    # Of any two different people, exactly one is richer than the other. Not in the statement:
    # it rules out two people being equally rich (transitivity is not imposed); it cannot cut
    # off the answer, which is the same without it.
    pairs = [(i, j) for i in people for j in range(i + 1, n)]
    model.addConstrs((richer[i, j] == 1 - richer[j, i] for i, j in pairs), name="richer_one_way")

    # Charles hates no one whom Agatha hates.
    model.addConstrs((hates[AGATHA, i] + hates[CHARLES, i] <= 1 for i in people), name="charles")

    # Agatha hates everybody except the butler (herself included).
    model.addConstrs((hates[AGATHA, i] == (0 if i == BUTLER else 1) for i in people), name="agatha_hates")

    # The butler hates everyone who is not richer than Agatha.
    model.addConstrs((1 - richer[i, AGATHA] <= hates[BUTLER, i] for i in people), name="butler_hates_poorer")
    # The butler hates everyone whom Agatha hates.
    model.addConstrs((hates[AGATHA, i] <= hates[BUTLER, i] for i in people), name="butler_hates_agatha_hates")

    # Nobody hates everyone: each resident fails to hate at least one person.
    model.addConstrs((hates.sum(i, "*") <= n - 1 for i in people), name="not_everyone")

    # No objective. killer is the index of the resident whose is_killer is 1.
    killer = gp.quicksum(i * is_killer[i] for i in people)
    return model, {"killer": killer}


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
