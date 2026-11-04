# giant_cat_army: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install z3-solver numpy`) with:
#   python giant_cat_army.py

import z3


def create_model(instance):
    """Start from 0 and build a list of 24 whole numbers. Each next number is the
    previous one plus 5, plus 7, or the square root of the previous one. The numbers
    are all different, at most 60, and the list ends with 14. The list contains 2,
    and later in the list 10."""
    max_value = 60  # the largest number allowed in the list
    length = 24     # the number of entries in the list

    # x[i] is the i-th entry of the list.
    x = [z3.Int(f"x_{i}") for i in range(length)]

    solver = z3.Solver()

    # Every entry is a whole number from 0 to 60.
    solver.add([z3.And(v >= 0, v <= max_value) for v in x])
    # All entries are different.
    solver.add(z3.Distinct(x))
    # The list starts with 0 and ends with 14.
    solver.add(x[0] == 0, x[length - 1] == 14)
    # Each entry comes from the one before it by adding 5, adding 7, or taking the
    # square root. The previous entry is the square of the next one.
    solver.add([z3.Or(x[i + 1] == x[i] + 5, x[i + 1] == x[i] + 7,
                      x[i] == x[i + 1] * x[i + 1])
                for i in range(length - 1)])
    # The list contains 2, and later on it contains 10.
    solver.add(z3.Or([z3.And(x[i] == 2, x[j] == 10)
                      for i in range(1, length) for j in range(i + 1, length)]))

    return solver, {"x": x}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
