# giant_cat_army: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install ortools`) with:
#   python giant_cat_army.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Build a list that starts with [0], where each next element is the previous one
    plus 5, plus 7, or its square root. The elements are distinct integers of at most
    60, the list has 24 elements, ends with 14, and has 2 before 10."""
    max_value = 60   # the largest value an element may take
    n_elements = 24  # the number of elements in the list

    model = cp_model.CpModel()

    # x[i] is the i-th element of the list. The list starts with 0 and ends with 14.
    x = ([model.new_int_var(0, 0, "x_0")]
         + [model.new_int_var(0, max_value, f"x_{i}") for i in range(1, n_elements - 1)]
         + [model.new_int_var(14, 14, f"x_{n_elements - 1}")])

    # All elements are distinct.
    model.add_all_different(x)

    # steps holds the allowed pairs (a, b) for a step from a to b: b = a + 5, b = a + 7,
    # or a = b * b (b is the square root of a).
    steps = set()
    for v in range(max_value + 1):
        if v + 5 <= max_value:
            steps.add((v, v + 5))
        if v + 7 <= max_value:
            steps.add((v, v + 7))
        if v * v <= max_value:
            steps.add((v * v, v))

    # Each element takes an allowed step to the next one.
    for i in range(n_elements - 1):
        model.add_allowed_assignments([x[i], x[i + 1]], sorted(steps))

    # index2 and index10 are the positions of 2 and 10 in the list; 2 comes before 10.
    index2 = model.new_int_var(1, n_elements - 1, "index2")
    index10 = model.new_int_var(1, n_elements - 1, "index10")
    model.add_element(index2, x, 2)
    model.add_element(index10, x, 10)
    model.add(index2 < index10)

    return model, {"x": x}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
