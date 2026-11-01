# mario: a CPMpy model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python mario.py mario.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Mario collects as much gold as possible by visiting houses. He starts at Mario's
    house and ends at Luigi's house, driving between houses on limited fuel."""
    n_houses = instance["nHouses"]                  # the number of houses
    mario = instance["marioHouse"]                  # the house where Mario starts
    luigi = instance["luigiHouse"]                  # the house where Mario ends
    fuel_limit = instance["fuelLimit"]              # the most fuel Mario can use
    arc_fuel = cp.cpm_array(instance["arc_fuel"])   # arc_fuel[i, j]: the fuel to drive from house i to house j
    gold = np.array(instance["goldInHouse"])        # gold[i]: the gold in house i
    houses = np.arange(n_houses)

    # s[i] is the house that follows house i on the route; s[i] = i if house i is not visited
    s = cp.intvar(0, n_houses - 1, shape=n_houses, name="s")

    model = cp.Model()

    # Every house has its own successor, so the route is a permutation: houses that are
    # not visited point to themselves, and the visited houses form one or more cycles
    # (the position constraints below leave a single cycle).
    model.add(cp.AllDifferent(s))

    # The route closes up: Luigi's house is followed by Mario's house.
    model.add(s[luigi] == mario)

    # order[i] is the position of house i along the route from Mario's house (1, 2, ...).
    # Houses off the route also get a position, so that all positions are distinct.
    order = cp.intvar(1, n_houses, shape=n_houses, name="order")
    model.add(cp.AllDifferent(order))

    # The route starts at Mario's house.
    model.add(order[mario] == 1)

    # Driving from a visited house to its successor advances the position by one, except
    # for the step back to Mario's house that closes the route. This makes the visited
    # houses one single cycle through Mario's and Luigi's houses: a second, separate cycle
    # would need positions that increase all the way around, which is impossible.
    for i in houses:
        model.add(((s[i] != i) & (s[i] != mario)).implies(order[s[i]] == order[i] + 1))

    # A house is either on the route or numbered after Luigi's house, so the positions
    # along the route are not shared with houses that are left out.
    for i in houses:
        model.add((s[i] != i) | (order[luigi] < order[i]))

    # The fuel used on the route stays within the fuel limit. Houses that are not visited
    # cost nothing, since driving from a house to itself uses no fuel.
    model.add(cp.sum([arc_fuel[i, s[i]] for i in houses]) <= fuel_limit)

    # Maximise the gold in the visited houses.
    model.maximize(cp.sum((s != houses) * gold))

    return model, {"s": s}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
