# session3_farmer_and_cows: an Exact (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from exact import Exact


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives
    as much milk as its number. He gives each son a set number of cows, and every
    son gets the same total amount of milk. Decide which son gets each cow."""
    num_cows = instance["num_cows"]          # the number of cows
    num_sons = instance["num_sons"]          # the number of sons, numbered 0 up to num_sons - 1
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s receives

    milk_per_cow = list(range(1, num_cows + 1))          # milk_per_cow[i]: the milk from cow i + 1
    total_milk_per_son = sum(milk_per_cow) // num_sons   # the milk each son must receive

    solver = Exact()

    # Exact identifies its variables by name.
    # cow_assignments[i] is the son who receives cow i + 1
    cow_assignments = [f"cow_{i}" for i in range(num_cows)]
    for name in cow_assignments:
        solver.addVariable(name, 0, num_sons - 1)

    # gets[i][s] is 1 when son s receives cow i + 1, and 0 otherwise
    gets = [[f"gets_{i}_{s}" for s in range(num_sons)] for i in range(num_cows)]
    for i in range(num_cows):
        for s in range(num_sons):
            solver.addVariable(gets[i][s], 0, 1)

    for i in range(num_cows):
        # Each cow goes to exactly one son.
        solver.addConstraint([(1, gets[i][s]) for s in range(num_sons)], True, 1, True, 1)
        # The son named in cow_assignments is the son who receives the cow.
        solver.addConstraint([(s, gets[i][s]) for s in range(1, num_sons)]
                             + [(-1, cow_assignments[i])], True, 0, True, 0)

    for s in range(num_sons):
        # Son s receives exactly cows_per_son[s] cows.
        solver.addConstraint([(1, gets[i][s]) for i in range(num_cows)],
                             True, cows_per_son[s], True, cows_per_son[s])
        # The cows of son s give exactly total_milk_per_son milk.
        solver.addConstraint([(milk_per_cow[i], gets[i][s]) for i in range(num_cows)],
                             True, total_milk_per_son, True, total_milk_per_son)

    return solver, {"cow_assignments": cow_assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
