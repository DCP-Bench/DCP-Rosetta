# clock_triplets: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install ortools`) with:
#   python clock_triplets.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Rearrange the numbers 1 to 12 on the face of a clock so that the sum of every three
    adjacent numbers is at most 21, the smallest possible largest sum."""
    n_numbers = 12  # the numbers on the clock face, 1 to 12
    max_sum = 21    # the largest allowed sum of three adjacent numbers

    model = cp_model.CpModel()

    # x[i] is the number at position i of the clock face, going round the face
    x = [model.new_int_var(1, n_numbers, f"x{i}") for i in range(n_numbers)]

    # Each number appears once on the clock.
    model.add_all_different(x)

    # Every three adjacent numbers, wrapping round the face, have a sum of at most max_sum.
    for i in range(n_numbers):
        model.add(x[i] + x[(i - 1) % n_numbers] + x[(i - 2) % n_numbers] <= max_sum)

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
