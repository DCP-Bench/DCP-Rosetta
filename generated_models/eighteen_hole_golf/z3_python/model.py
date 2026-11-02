# eighteen_hole_golf: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install z3-solver numpy`) with:
#   python eighteen_hole_golf.py

import z3


def create_model(instance):
    """A golf course has 18 holes, each of length 3, 4 or 5, and the holes add up to
    a total length of 72. Find the length of each hole."""
    n_holes = 18  # the course has 18 holes
    total_length = 72  # the lengths of all holes add up to 72
    min_length, max_length = 3, 5  # a hole is 3, 4 or 5 long

    # holes[i] is the length of hole i
    holes = z3.IntVector("holes", n_holes)

    # The conditions on the hole lengths.
    solver = z3.Solver()

    # Each hole is 3, 4 or 5 long.
    solver.add([z3.And(h >= min_length, h <= max_length) for h in holes])

    # The holes add up to the length of the course.
    solver.add(z3.Sum(holes) == total_length)

    return solver, {"holes": list(holes)}


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
