# mario: a PyCSP3 model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python mario.py mario.json

from pycsp3 import *


def create_model(instance):
    """Mario collects as much gold as possible on a route that starts at Mario's house and
    ends at Luigi's house, from where it returns to Mario's house. The travel between
    houses uses fuel, and the route may not use more fuel than Mario has."""
    n_houses = instance["nHouses"]        # the houses are numbered 0 to n_houses - 1
    mario = instance["marioHouse"]        # the house where the route starts
    luigi = instance["luigiHouse"]        # the house the route ends at, before going back to Mario's
    gold = instance["goldInHouse"]        # gold[h] is the gold in house h
    arc_fuel = instance["arc_fuel"]       # arc_fuel[a][b] is the fuel used travelling from house a to house b
    fuel_limit = instance["fuelLimit"]    # the most fuel Mario has
    houses = range(n_houses)
    # the largest travel fuel in the instance, which bounds the fuel of any one travel
    max_arc_fuel = max(max(row) for row in arc_fuel)

    # succ[h] is the house after house h on the route; succ[h] == h when h is not on the route
    succ = VarArray(size=n_houses, dom=houses, id="succ")
    # on_route[h] is 1 when house h is on the route
    on_route = VarArray(size=n_houses, dom={0, 1}, id="on_route")
    # fuel[h] is the fuel used on the travel from house h to its successor
    fuel = VarArray(size=n_houses, dom=range(max_arc_fuel + 1), id="fuel")

    satisfy(
        # Mario's house is on the route, and the route goes from it to another house
        succ[mario] != mario,
        # Luigi's house is followed by Mario's house
        succ[luigi] == mario,
        # each house is the successor of at most one house
        AllDifferent(succ),
        # the houses off the route are their own successors, and the others form one circuit
        Circuit(succ),
        # a house is on the route exactly when it is not its own successor
        [on_route[h] == (succ[h] != h) for h in houses],
        # the fuel of the travel from each house to its successor; a house off the route uses no fuel
        [Table(scope=(succ[h], fuel[h]), supports=[(a, arc_fuel[h][a]) for a in houses if a != h] + [(h, 0)]) for h in houses],
        # the fuel used on the route does not exceed the fuel Mario has
        Sum(fuel) <= fuel_limit,
    )

    # Mario collects the gold of every house on the route
    maximize(Sum(gold[h] * on_route[h] for h in houses))

    return {"s": succ}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
