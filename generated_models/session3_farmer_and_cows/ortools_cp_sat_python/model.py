# session3_farmer_and_cows: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install ortools`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives
    as much milk as its number. Each son gets a given number of cows, and every son
    gets the same total amount of milk; decide which son gets each cow."""
    num_cows = instance["num_cows"]          # the number of cows
    num_sons = instance["num_sons"]          # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s receives

    milk = list(range(1, num_cows + 1))      # milk[i]: the milk from cow i+1, equal to its number
    share = sum(milk) // num_sons            # the milk each son must receive

    model = cp_model.CpModel()

    # cow_assignments[i] is the son who receives cow i+1
    cow_assignments = [model.new_int_var(0, num_sons - 1, f"cow_{i}") for i in range(num_cows)]
    # got[i][s] is true when son s receives cow i+1
    got = [[model.new_bool_var(f"got_{i}_{s}") for s in range(num_sons)] for i in range(num_cows)]

    for i in range(num_cows):
        # got[i] and cow_assignments[i] name the same son.
        for s in range(num_sons):
            model.add(cow_assignments[i] == s).only_enforce_if(got[i][s])
            model.add(cow_assignments[i] != s).only_enforce_if(~got[i][s])
        # Each cow goes to exactly one son.
        model.add_exactly_one(got[i])

    for s in range(num_sons):
        # Each son receives the prescribed number of cows.
        model.add(sum(got[i][s] for i in range(num_cows)) == cows_per_son[s])
        # Each son's cows give the same total amount of milk.
        model.add(sum(milk[i] * got[i][s] for i in range(num_cows)) == share)

    return model, {"cow_assignments": cow_assignments}


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
