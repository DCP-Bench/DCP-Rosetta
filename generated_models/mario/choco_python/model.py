# mario: a Choco-solver (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python mario.py mario.json

from pychoco.model import Model


def create_model(instance):
    """Mario drives from his house to Luigi's house, visiting some of the houses on the way
    and collecting their gold. The fuel used on the trip may not exceed the fuel limit."""
    n_houses = instance["nHouses"]            # the number of houses, numbered 0 to n_houses - 1
    mario = instance["marioHouse"]            # the house where Mario starts
    luigi = instance["luigiHouse"]            # the house where Mario ends
    fuel_limit = instance["fuelLimit"]        # the most fuel the trip may use
    arc_fuel = instance["arc_fuel"]           # arc_fuel[i][j]: the fuel to drive from house i to house j
    gold_in_house = instance["goldInHouse"]   # gold_in_house[i]: the gold in house i

    model = Model()

    # s[i] is the house Mario drives to after house i; s[i] = i when house i is not on the route.
    s = [model.intvar(0, n_houses - 1, name=f"s_{i}") for i in range(n_houses)]

    # The houses on the route form one loop, and the houses off the route drive to themselves.
    route_length = model.intvar(2, n_houses, name="route_length")  # the number of houses on the route
    model.sub_circuit(s, 0, route_length).post()

    # The last drive of the route goes from Luigi's house to Mario's house.
    model.arithm(s[luigi], "=", mario).post()

    # fuel[i] is the fuel used by the drive out of house i.
    fuel = []
    for i in range(n_houses):
        fuel_i = model.intvar(0, max(arc_fuel[i]), name=f"fuel_{i}")
        model.element(fuel_i, arc_fuel[i], s[i]).post()
        fuel.append(fuel_i)

    # The fuel used on the trip stays within the fuel limit.
    model.sum(fuel, "<=", fuel_limit).post()

    # on_route[i] is true when house i is on the route.
    on_route = [model.arithm(s[i], "!=", i).reify() for i in range(n_houses)]

    # gold: the total gold of the houses on the route, to be maximized.
    gold = model.intvar(0, sum(gold_in_house), name="gold")
    model.scalar(on_route, gold_in_house, "=", gold).post()

    return model, {"s": s}, {"objective": gold, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
