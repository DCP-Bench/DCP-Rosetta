# arch_friends: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python arch_friends.py

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Harriet bought four pairs of shoes at four stores, one pair at each of four stops
    in order. Find the stop (1 to 4) of each shoe and of each store, from four clues."""
    # The puzzle has no instance data: the shoes, stores and clues are the puzzle's
    # own, mirrored from the reference.
    n = 4  # four shoes, four stores, four stops
    stops = range(1, n + 1)
    shoe_names = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]  # the four shoes
    store_names = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]  # the four stores

    model = gp.Model("arch_friends")

    # shoe_at[s, k] is 1 when shoe s was bought at stop k; store_at[t, k] likewise for
    # store t. Different shoes (stores) come at different stops.
    shoe_at = model.addVars(n, stops, vtype=GRB.BINARY, name="shoe_at")
    store_at = model.addVars(n, stops, vtype=GRB.BINARY, name="store_at")

    # Each shoe (store) is bought at exactly one stop, and each stop has exactly one shoe
    # (store).
    for x in (shoe_at, store_at):
        model.addConstrs(x.sum(i, "*") == 1 for i in range(n))
        model.addConstrs(x.sum("*", k) == 1 for k in stops)

    # shoe[s] and store[t] are the stop at which that shoe or store comes, as expressions.
    shoe = {s: gp.quicksum(k * shoe_at[i, k] for k in stops) for i, s in enumerate(shoe_names)}
    store = {t: gp.quicksum(k * store_at[i, k] for k in stops) for i, t in enumerate(store_names)}
    purple = shoe_names.index("purplepumps")
    footfarm = store_names.index("footfarm")
    tootsies = store_names.index("tootsies")

    # Clue 1: Harriet bought fuchsia flats at Heels in a Handcart, so both are at one stop.
    model.addConstr(shoe["fuchsiaflats"] == store["heelsinahandcart"])

    # Clue 2: the store she visited just after buying her purple pumps was not Tootsies,
    # so purple pumps at stop k and Tootsies at stop k + 1 never both hold.
    model.addConstrs(shoe_at[purple, k] + store_at[tootsies, k + 1] <= 1 for k in range(1, n))

    # Clue 3: the Foot Farm was Harriet's second stop.
    model.addConstr(store_at[footfarm, 2] == 1)

    # Clue 4: two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    model.addConstr(store["theshoepalace"] + 2 == shoe["suedesandals"])

    # No objective: any assignment that meets the four clues answers the puzzle.
    return model, {**shoe, **store}


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
