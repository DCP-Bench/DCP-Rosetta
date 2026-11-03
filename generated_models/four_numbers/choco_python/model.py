# four_numbers: a Choco-solver (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python four_numbers.py four_numbers.json

from pychoco.model import Model


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1 and
    10 such that every given number is the sum of some of the three."""
    numbers = instance["numbers"]  # numbers[i]: the i-th given number
    n_numbers = len(numbers)
    n_integers = 3  # how many integers to find

    model = Model()

    # x[j] is the j-th integer to find
    x = [model.intvar(1, 10, name=f"x_{j}") for j in range(n_integers)]
    # uses[i][j] is true when x[j] is part of the sum that gives numbers[i]
    uses = [[model.boolvar(name=f"uses_{i}_{j}") for j in range(n_integers)]
            for i in range(n_numbers)]

    # Each given number is the sum of the integers used for it.
    for i in range(n_numbers):
        # part[j] is x[j] when it is used for numbers[i], and 0 otherwise
        part = [model.intvar(0, 10, name=f"part_{i}_{j}") for j in range(n_integers)]
        for j in range(n_integers):
            model.times(x[j], uses[i][j], part[j]).post()
        model.sum(part, "=", numbers[i]).post()

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
