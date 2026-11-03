# mario: a SCIP (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python mario.py mario.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Mario starts at his house, visits some of the houses and ends at Luigi's
    house, from where he goes back to Mario's house. He collects the gold of the
    houses he visits and must not use more fuel than the limit on the travel.
    Each house is visited at most once. The output s gives, for each house, the
    house after it on the route (s[i] = i when the route skips house i)."""
    n = instance["nHouses"]                   # the number of houses, numbered 0 to n-1
    mario = instance["marioHouse"]            # the house where the route starts
    luigi = instance["luigiHouse"]            # the house where the route ends (Luigi's house)
    gold = np.array(instance["goldInHouse"])  # gold[i]: the gold in house i
    fuel = np.array(instance["arc_fuel"])     # fuel[i][j]: the fuel to travel from house i to house j
    fuel_limit = instance["fuelLimit"]        # the most fuel the whole route may use

    model = Model("mario")

    # x[i][j] is 1 when the route goes straight from house i to house j.
    # x[i][i] is 1 when house i is skipped, so it is its own successor.
    x = model.addMatrixVar((n, n), vtype="B", name="x")

    # Each house has exactly one successor (row sum 1) and exactly one predecessor
    # (column sum 1), so the arcs form disjoint cycles. A skipped house is a cycle
    # of its own (x[i][i] = 1). The other cycles must all pass through Mario's house,
    # which the position constraints below enforce.
    model.addMatrixCons(x.sum(axis=1) == 1)  # one successor per house
    model.addMatrixCons(x.sum(axis=0) == 1)  # one predecessor per house

    # Mario's house and Luigi's house are on the route, so neither is skipped.
    model.addCons(x[mario, mario] == 0)
    model.addCons(x[luigi, luigi] == 0)
    # The route ends at Luigi's house and goes straight back to Mario's house.
    model.addCons(x[luigi, mario] == 1)

    # place[i] is the position of house i on the route, counted from Mario's house
    # as 0. Each house is visited at most once, so the route has at most n houses
    # and the positions run from 0 to n-1 (the bound is derived from that statement).
    place = model.addMatrixVar(n, vtype="I", lb=0, ub=n - 1, name="place")
    model.addCons(place[mario] == 0)
    # Along an arc x[i][j] = 1 that leaves house i for house j, the position of j
    # is at least one more than that of i. Arcs into Mario's house are left out:
    # they close the route, and Mario's position is 0. Arcs i to i are left out too,
    # because a skipped house has no position on the route. Every cycle that avoids
    # Mario's house would need its positions to rise along every arc and return to
    # where it started, which is impossible, so no such cycle can exist.
    for i in range(n):
        for j in range(n):
            if i != j and j != mario:
                model.addConsIndicator(place[j] - place[i] >= 1, binvar=x[i, j])

    # The fuel of the arcs the route travels (x[i][j] = 1), the closing arc from
    # Luigi's house to Mario's house included, is at most the fuel limit. The diagonal
    # of arc_fuel is 0 in the data, so a skipped house (x[i][i] = 1) uses no fuel.
    model.addCons((fuel * x).sum() <= fuel_limit)

    # Maximise the gold collected: the gold of every house, minus the gold of the
    # houses skipped (x[i][i] = 1).
    model.setObjective(int(gold.sum()) - (gold * x.diagonal()).sum(), "maximize")

    # s[i] is the house after house i: the sum of j * x[i][j] over the houses j.
    # Each row has exactly one 1, so this is the successor itself.
    s = x @ np.arange(n)
    return model, {"s": s}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
