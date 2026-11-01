# csplib_024_langford: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

from pychoco.model import Model


def create_model(instance):
    """Arrange two copies of each number from 1 to k into one row of 2k places, so that the two
    copies of 1 have one number between them, the two copies of 2 have two numbers between them,
    and so on up to the two copies of k."""
    k = instance["k"]  # the largest number; each number from 1 to k is placed twice

    model = Model()

    # position[i - 1] is the place of the first copy of number i, and position[k + i - 1] is the
    # place of its second copy. The places are numbered 0 to 2k - 1.
    position = [model.intvar(0, 2 * k - 1, name=f"position_{j}") for j in range(2 * k)]
    # sol[p] is the number at place p of the row
    sol = [model.intvar(1, k, name=f"sol_{p}") for p in range(2 * k)]

    # Every copy takes a place of its own.
    model.all_different(position).post()

    for i in range(1, k + 1):
        # The two copies of i have i numbers between them, so they are i + 1 places apart.
        model.arithm(position[i - 1], "+", i + 1, "=", position[k + i - 1]).post()
        # Both places of number i hold the number i.
        model.element(model.intvar(i, i), sol, position[i - 1]).post()
        model.element(model.intvar(i, i), sol, position[k + i - 1]).post()

    return model, {"sol": sol}, None


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
