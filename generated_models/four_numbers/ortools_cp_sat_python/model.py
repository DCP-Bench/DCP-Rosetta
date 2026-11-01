# four_numbers: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install ortools`):
#   python four_numbers.py four_numbers.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Given up to four distinct integers between 1 and 10, find three integers between 1 and
    10 such that every given number is the sum of a subset of the three."""
    numbers = instance["numbers"]  # numbers[i]: the i-th number that must be a subset sum
    n_integers = 3  # how many integers to find

    model = cp_model.CpModel()

    # x[j] is the j-th of the three integers to find
    x = [model.new_int_var(1, 10, f"x_{j}") for j in range(n_integers)]

    for i, number in enumerate(numbers):
        # uses[j] is true when x[j] is part of the subset that sums to numbers[i]
        uses = [model.new_bool_var(f"uses_{i}_{j}") for j in range(n_integers)]
        # part[j] is x[j] when it is used, and 0 otherwise
        part = [model.new_int_var(0, 10, f"part_{i}_{j}") for j in range(n_integers)]
        for j in range(n_integers):
            model.add(part[j] == x[j]).only_enforce_if(uses[j])
            model.add(part[j] == 0).only_enforce_if(~uses[j])
        # The integers in the subset sum to numbers[i].
        model.add(sum(part) == number)

    return model, {"x": x}


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
