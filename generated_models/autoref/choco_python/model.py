# autoref: a Choco-solver (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python autoref.py autoref.json

from pychoco.model import Model


def create_model(instance):
    """Find a series s[0], s[1], ..., s[n+1] in which every integer i from 0 to n
    occurs exactly s[i] times, and whose last element s[n+1] equals m."""
    n = instance["n"]  # the values 0 to n are counted in the series
    m = instance["m"]  # the required value of the last element

    model = Model()

    # s[k] is the k-th element of the series; every element lies between 0 and n
    s = [model.intvar(0, n, name=f"s_{k}") for k in range(n + 2)]

    # The last element is m.
    model.arithm(s[n + 1], "=", m).post()

    # The value i occurs exactly s[i] times, for every i from 0 to n.
    for i in range(n + 1):
        model.count(i, s, s[i]).post()

    return model, {"s": s}, None


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
