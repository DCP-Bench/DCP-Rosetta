# clock_triplets: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install exact numpy`) with:
#   python clock_triplets.py

from exact import Exact


def create_model(instance):
    """Arrange the numbers 1 to 12 on the face of a clock so that no three neighbouring
    numbers add up to more than 21, the smallest value the largest such sum can take."""
    n = 12  # the numbers on the clock face, 1 to 12

    solver = Exact()

    # Exact identifies its variables by name.
    # x[i] is the number at position i of the clock face, counting round the face
    x = [f"x_{i}" for i in range(n)]
    for name in x:
        solver.addVariable(name, 1, n)

    # holds[i][v - 1] is 1 when position i shows the number v, and 0 when not
    holds = [[f"x_{i}_is_{v}" for v in range(1, n + 1)] for i in range(n)]
    for i in range(n):
        for name in holds[i]:
            solver.addVariable(name, 0, 1)

        # Each position shows exactly one number.
        solver.addConstraint([(1, name) for name in holds[i]], True, 1, True, 1)

        # The number at position i is the number that position shows.
        solver.addConstraint([(v, holds[i][v - 1]) for v in range(1, n + 1)] + [(-1, x[i])],
                             True, 0, True, 0)

    # Each number appears on exactly one position.
    for v in range(1, n + 1):
        solver.addConstraint([(1, holds[i][v - 1]) for i in range(n)], True, 1, True, 1)

    # Every three neighbouring positions, counting round the clock, add up to at most 21.
    for i in range(n):
        solver.addConstraint([(1, x[i]), (1, x[(i + 1) % n]), (1, x[(i + 2) % n])],
                             False, 0, True, 21)

    return solver, {"x": x}


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
