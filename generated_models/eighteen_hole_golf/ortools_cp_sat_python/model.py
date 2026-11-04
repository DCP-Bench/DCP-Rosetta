# eighteen_hole_golf: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install ortools`) with:
#   python eighteen_hole_golf.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Find an 18-hole golf course in which every hole is 3, 4 or 5 long and the
    holes add up to 72."""
    n_holes = 18       # the course has 18 holes
    total_length = 72  # the lengths of the holes add up to 72

    model = cp_model.CpModel()

    # holes[i] is the length of hole i, one of 3, 4 or 5
    holes = [model.new_int_var(3, 5, f"hole{i}") for i in range(n_holes)]

    # The holes add up to the length of the course.
    model.add(sum(holes) == total_length)

    return model, {"holes": holes}


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
