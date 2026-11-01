# just_forgotten: a Choco-solver (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python just_forgotten.py just_forgotten.json

from pychoco.model import Model


def create_model(instance):
    """Joe's bank account number uses each digit from 0 to n-1 exactly once. In each set
    of digits he tried, a given number of digits are in their correct position. Find the
    account number."""
    sets = instance["sets"]  # sets[k][i] is the digit in position i of the k-th set Joe tried
    num_correct_digits = instance["num_correct_digits"]  # digits in their correct position in each set
    n = len(sets[0])  # the number of digits in the account number

    model = Model()

    # x[i] is the digit in position i of the account number.
    x = [model.intvar(0, n - 1, name=f"x_{i}") for i in range(n)]

    # The account number has each digit from 0 to n-1 exactly once.
    model.all_different(x).post()

    # Each set of digits has exactly num_correct_digits digits in their correct position.
    for tried in sets:
        # in_place[i] is true when position i of the account number holds the digit tried there.
        in_place = [model.arithm(x[i], "=", tried[i]).reify() for i in range(n)]
        model.sum(in_place, "=", num_correct_digits).post()

    return model, {"x": x}, None


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
