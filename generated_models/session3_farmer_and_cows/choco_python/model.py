# session3_farmer_and_cows: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

from pychoco.model import Model


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives
    as much milk as its number. He gives each of his sons a set number of cows,
    so that every son gets the same total quantity of milk. Decide which son gets
    each cow."""
    n_cows = instance["num_cows"]            # the number of cows
    n_sons = instance["num_sons"]            # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s receives

    milk = list(range(1, n_cows + 1))   # the milk each cow gives, equal to its number
    milk_per_son = sum(milk) // n_sons  # the total milk each son must receive

    model = Model()

    # the son who receives each cow
    cow_assignments = [model.intvar(0, n_sons - 1, name=f"cow_{c}") for c in range(n_cows)]

    # gets[s][c] is true when son s receives cow c
    gets = [[model.arithm(cow_assignments[c], "=", s).reify() for c in range(n_cows)]
            for s in range(n_sons)]

    for s in range(n_sons):
        # Each son receives the number of cows set for him.
        model.sum(gets[s], "=", cows_per_son[s]).post()
        # The cows of each son give the same total milk.
        model.scalar(gets[s], milk, "=", milk_per_son).post()

    return model, {"cow_assignments": cow_assignments}, None


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
