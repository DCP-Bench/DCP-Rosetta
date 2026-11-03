# session3_farmer_and_cows: a Z3 (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

import z3


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives as
    much milk as its number. He gives each son a set number of cows, so that every
    son gets the same total amount of milk. Decide which son gets each cow."""
    num_cows = instance["num_cows"]          # the number of cows
    num_sons = instance["num_sons"]          # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s receives

    # milk[i]: the milk from cow i+1, equal to its number.
    milk = list(range(1, num_cows + 1))
    # share: the milk each son receives.
    share = sum(milk) // num_sons

    # cow_assignments[i]: the son who receives cow i+1.
    cow_assignments = [z3.Int(f"cow_{i}") for i in range(num_cows)]

    solver = z3.Solver()

    # Every cow goes to one of the sons.
    solver.add([z3.And(0 <= cow, cow <= num_sons - 1) for cow in cow_assignments])

    for son in range(num_sons):
        # got[i]: 1 when cow i+1 goes to this son, 0 otherwise.
        got = [z3.If(cow == son, 1, 0) for cow in cow_assignments]

        # This son receives the prescribed number of cows.
        solver.add(z3.Sum(got) == cows_per_son[son])

        # The cows of this son give the share of milk.
        solver.add(z3.Sum([m * g for m, g in zip(milk, got)]) == share)

    return solver, {"cow_assignments": cow_assignments}


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
