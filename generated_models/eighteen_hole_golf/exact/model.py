# eighteen_hole_golf: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/eighteen_hole_golf.html
# Run it (after `pip install exact numpy`) with:
#   python eighteen_hole_golf.py

from exact import Exact


def create_model(instance):
    """A golf course has 18 holes, each 3, 4 or 5 long, and the whole course is 72
    long. Choose the length of each hole."""
    n_holes = 18           # the course has 18 holes
    total_length = 72      # the whole course is 72 long
    shortest, longest = 3, 5  # a hole is 3, 4 or 5 long

    solver = Exact()

    # Exact identifies its variables by name.
    # holes[i] is the length of hole i
    holes = [f"holes_{i}" for i in range(n_holes)]
    for name in holes:
        solver.addVariable(name, shortest, longest)

    # The lengths of the holes add up to the length of the course.
    solver.addConstraint([(1, name) for name in holes], True, total_length, True, total_length)

    return solver, {"holes": holes}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
