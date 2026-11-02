# mario: a Z3 (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python mario.py mario.json

import z3


def create_model(instance):
    """Mario drives from his house to Luigi's house, through some of the other houses,
    and collects the gold in every house he visits. The drive uses at most the fuel
    limit. The route with the most gold is the answer."""
    n_houses = instance["nHouses"]           # the number of houses, numbered 0 to n_houses - 1
    mario = instance["marioHouse"]           # the house Mario starts from
    luigi = instance["luigiHouse"]           # the house Mario drives to at the end
    fuel_limit = instance["fuelLimit"]       # the most fuel the drive may use
    arc_fuel = instance["arc_fuel"]          # arc_fuel[i][j]: the fuel to drive from house i to house j
    gold_in_house = instance["goldInHouse"]  # gold_in_house[i]: the gold in house i

    # succ[i] is the house Mario drives to straight after house i. A house off the route is its own successor.
    succ = [z3.Int(f"succ_{i}") for i in range(n_houses)]

    # drives[i][j] is true when the route goes straight from house i to house j.
    drives = [[succ[i] == j for j in range(n_houses)] for i in range(n_houses)]

    # rank[i] is the place of house i on the route: Mario's house is first (rank 1), and the ranks count up along the route.
    rank = [z3.Int(f"rank_{i}") for i in range(n_houses)]

    solver = z3.Optimize()

    # Every house number is a house, and every rank is between 1 and n_houses.
    for i in range(n_houses):
        solver.add(succ[i] >= 0, succ[i] <= n_houses - 1, rank[i] >= 1, rank[i] <= n_houses)

    # Every house is driven to from exactly one house, itself included.
    for j in range(n_houses):
        solver.add(z3.PbEq([(drives[i][j], 1) for i in range(n_houses)], 1))

    # The route starts at Mario's house, which has rank 1.
    solver.add(rank[mario] == 1)

    # The route ends at Luigi's house, which is followed by Mario's house.
    solver.add(succ[luigi] == mario)

    # Along the route the rank rises by one at each drive, except the drive back into Mario's house that closes the route.
    # So the route cannot split into separate loops.
    for i in range(n_houses):
        for j in range(n_houses):
            if j != i and j != mario:
                solver.add(z3.Implies(drives[i][j], rank[j] == rank[i] + 1))

    # The fuel for the drive from each house to the next stays within the limit. A house off the route costs arc_fuel[i][i].
    fuel_used = z3.Sum([z3.If(drives[i][j], arc_fuel[i][j], 0) for i in range(n_houses) for j in range(n_houses)])
    solver.add(fuel_used <= fuel_limit)

    # The gold collected in the houses on the route. A house off the route gives nothing.
    total_gold = z3.Sum([z3.If(drives[i][i], 0, gold_in_house[i]) for i in range(n_houses)])

    solver.maximize(total_gold)

    return solver, {"s": succ}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
