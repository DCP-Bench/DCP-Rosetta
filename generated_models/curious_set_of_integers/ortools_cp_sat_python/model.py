# curious_set_of_integers: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install ortools`):
#   python curious_set_of_integers.py curious_set_of_integers.json

from ortools.sat.python import cp_model


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n_integers = instance["n"]     # the number of integers in the set, including the one to find
    max_val = instance["max_val"]  # the largest value any integer in the set may take

    model = cp_model.CpModel()

    # x[i] is the i-th integer of the set
    x = [model.new_int_var(0, max_val, f"x_{i}") for i in range(n_integers)]

    # The first four integers are 1, 3, 8 and 120.
    for index, value in enumerate([1, 3, 8, 120]):
        model.add(x[index] == value)
    # All integers differ.
    model.add_all_different(x)

    # The product of any two integers is one less than a perfect square.
    for i in range(n_integers):
        for j in range(i + 1, n_integers):
            # square is one more than product, and root is its square root
            root = model.new_int_var(0, max_val, f"root_{i}_{j}")
            square = model.new_int_var(0, max_val * max_val, f"square_{i}_{j}")
            product = model.new_int_var(0, max_val * max_val, f"product_{i}_{j}")
            model.add_multiplication_equality(square, [root, root])
            model.add_multiplication_equality(product, [x[i], x[j]])
            model.add(square == product + 1)

    return model, {"number": x[-1]}


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
