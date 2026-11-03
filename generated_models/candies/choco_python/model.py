# candies: a Choco-solver (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python candies.py candies.json

from pychoco.model import Model


def create_model(instance):
    """Alice gives candies to the children standing in a line. Every child gets at least one
    candy, and a child with a higher rating than a neighbour gets more candies than that
    neighbour."""
    ratings = instance["ratings"]  # ratings[i]: the rating of child i, in line order
    n = len(ratings)               # the number of children

    model = Model()

    # x[i] is the number of candies child i gets. Each child gets at least one, and no child
    # needs more than n.
    x = [model.intvar(1, n, name=f"x{i}") for i in range(n)]
    # The total number of candies handed out.
    total = model.intvar(1, n * n, name="z")

    # The total is the sum of the candies given out, and it is at least one per child.
    model.sum(x, "=", total).post()
    model.arithm(total, ">=", n).post()

    # Neighbours with different ratings: the higher-rated child gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            model.arithm(x[i - 1], ">", x[i]).post()
        elif ratings[i - 1] < ratings[i]:
            model.arithm(x[i - 1], "<", x[i]).post()

    # The objective is the total number of candies, to be as small as possible.
    return model, {"z": total, "x": x}, {"objective": total, "maximize": False}


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
