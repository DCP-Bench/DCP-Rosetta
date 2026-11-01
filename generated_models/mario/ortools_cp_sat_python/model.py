# mario: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install ortools`):
#   python mario.py mario.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Mario collects as much gold as possible by visiting houses. He starts at Mario's
    house and ends at Luigi's house, driving between houses on limited fuel."""
    n = instance["nHouses"]             # the number of houses, numbered 0 to n-1
    mario = instance["marioHouse"]      # the house where Mario starts
    luigi = instance["luigiHouse"]      # the house where Mario ends
    fuel_limit = instance["fuelLimit"]  # the most fuel the trip may use
    arc_fuel = instance["arc_fuel"]     # arc_fuel[i][j]: the fuel to drive from house i to house j
    gold = instance["goldInHouse"]      # gold[i]: the gold in house i

    model = cp_model.CpModel()

    # go[i][j] is true when the route drives from house i straight to house j.
    # go[i][i] is true when house i is not on the route.
    go = [[model.new_bool_var(f"go_{i}_{j}") for j in range(n)] for i in range(n)]

    # The route is one loop: Mario's house, the houses it visits, and back to Mario's house.
    # A house that is not visited is skipped.
    model.add_circuit([(i, j, go[i][j]) for i in range(n) for j in range(n)])

    # Luigi's house is followed by Mario's house, which closes the loop.
    model.add(go[luigi][mario] == 1)

    # s[i] is the house that follows house i on the route (i itself if house i is not on it)
    s = [model.new_int_var(0, n - 1, f"s_{i}") for i in range(n)]
    for i in range(n):
        model.add(s[i] == sum(j * go[i][j] for j in range(n)))

    # The fuel for the drives on the route stays within the limit.
    model.add(sum(arc_fuel[i][j] * go[i][j] for i in range(n) for j in range(n)) <= fuel_limit)

    # Maximise the gold in the houses on the route. A house is on the route unless it is skipped.
    model.maximize(sum(gold[i] * (1 - go[i][i]) for i in range(n)))

    return model, {"s": s}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
