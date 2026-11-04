# eighteen_hole_golf: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install cvc5 numpy`) with:
#   python eighteen_hole_golf.py

import cvc5.pythonic as c5


def create_model(instance):
    """Generate an 18 hole golf course where each hole has a length of 3, 4 or 5,
    and the total length of the course is 72."""
    n_holes = 18  # the number of holes on the course
    total_length = 72  # the total length of the course

    # holes[i] is the length of hole i + 1
    holes = [c5.Int(f"hole_{i}") for i in range(n_holes)]

    # the rules the hole lengths must meet
    solver = c5.Solver()

    # Each hole is 3, 4 or 5 long.
    for h in holes:
        solver.add(h >= 3)
        solver.add(h <= 5)

    # The holes add up to the total length of the course.
    solver.add(c5.Sum(holes) == total_length)

    return solver, {"holes": holes}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
