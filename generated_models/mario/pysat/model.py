# mario: a PySAT (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python mario.py mario.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Mario collects as much gold as possible by visiting houses. He starts at Mario's
    house and ends at Luigi's house, driving between houses on limited fuel."""
    n = instance["nHouses"]                 # the number of houses
    mario = instance["marioHouse"]          # the house where Mario starts
    luigi = instance["luigiHouse"]          # the house where Mario ends
    fuel_limit = instance["fuelLimit"]      # the most fuel the trip may use
    arc_fuel = instance["arc_fuel"]         # arc_fuel[i][j]: the fuel to drive from house i to house j
    gold = instance["goldInHouse"]          # gold[i]: the gold in house i
    houses = range(n)                       # the houses, numbered 0 to n-1

    pool = IDPool()

    # s[i] is the house that follows house i on the route (i itself when house i is not on the route)
    s = [Integer(f"s_{i}", 0, n - 1, vpool=pool) for i in houses]
    # order[i] is the stop number of house i on the route, from 1 to n. Houses off the route get numbers too.
    order = [Integer(f"order_{i}", 1, n, vpool=pool) for i in houses]
    engine = IntegerEngine(vars=s + order, vpool=pool)

    # Each house has its own successor.
    engine.add_alldifferent(s)
    # Each house has its own stop number.
    engine.add_alldifferent(order)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def arc(i, j):
        """Is the route driven straight from house i to house j?"""
        return s[i].equals(j)

    # The route starts at Mario's house, which is stop 1.
    formula.append([order[mario].equals(1)])

    # The route ends at Luigi's house, which is followed by Mario's house.
    formula.append([arc(luigi, mario)])

    for i in houses:
        # A house on the route, other than the last one, is followed by the house with the next stop number.
        for j in houses:
            if j == i or j == mario:
                continue
            for r in range(1, n):
                formula.append([-arc(i, j), -order[i].equals(r),
                                order[j].equals(r + 1)])
            formula.append([-arc(i, j), -order[i].equals(n)])
        # A house left off the route is numbered after Luigi's house, so houses off the route
        # cannot form loops of their own.
        for r in range(1, n + 1):
            for q in range(1, r + 1):
                formula.append([-arc(i, i), -order[luigi].equals(r),
                                -order[i].equals(q)])

    # The fuel of the drives on the route stays within the fuel limit. Houses left off the route
    # cost no fuel.
    lits, weights = [], []
    for i in houses:
        for j in houses:
            if arc_fuel[i][j] != 0:
                lits.append(arc(i, j))
                weights.append(arc_fuel[i][j])
    if lits:
        formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=fuel_limit,
                                 vpool=pool).clauses)
    elif fuel_limit < 0:
        # No drive costs fuel, so the trip uses no fuel and fits only when the limit is not negative.
        formula.append([])

    # Gold: leaving a house off the route costs its gold, so the route collects as much as it can.
    # A house with negative gold costs its absolute value when it is left off the route.
    for i in houses:
        if gold[i] > 0:
            formula.append([-arc(i, i)], weight=gold[i])
        elif gold[i] < 0:
            formula.append([arc(i, i)], weight=-gold[i])

    return formula, {"s": s}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
