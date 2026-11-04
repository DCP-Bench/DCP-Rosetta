# session1_five_floors: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install exact numpy`) with:
#   python session1_five_floors.py

from exact import Exact


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of a
    five-floor house; find the floor of each from the clues."""
    # The initials of the five people
    names = "BCFMS"

    solver = Exact()

    # The floors each person can live on, from the clues. Baker is not on the
    # fifth floor, Cooper is not on the first, and Fletcher is on neither the
    # first nor the fifth.
    bounds = {"B": (1, 4), "C": (2, 5), "F": (2, 4), "M": (1, 5), "S": (1, 5)}

    # Exact identifies its variables by name.
    # The floor, from 1 to 5, where each person lives
    for name in names:
        solver.addVariable(name, *bounds[name])

    # on_floor[name][v] is 1 when that person lives on floor v, and 0 otherwise
    on_floor = {name: {v: f"{name}_on_{v}" for v in range(1, 6)} for name in names}
    for name in names:
        for v in range(1, 6):
            solver.addVariable(on_floor[name][v], 0, 1)

    def not_adjacent(p, q):
        """Persons p and q do not live on neighbouring floors."""
        for v in range(1, 5):
            solver.addConstraint([(1, on_floor[p][v]), (1, on_floor[q][v + 1])], False, 0, True, 1)
            solver.addConstraint([(1, on_floor[q][v]), (1, on_floor[p][v + 1])], False, 0, True, 1)

    # Each person lives on exactly one floor, and that is the floor of their variable.
    for name in names:
        solver.addConstraint([(1, on_floor[name][v]) for v in range(1, 6)], True, 1, True, 1)
        solver.addConstraint([(v, on_floor[name][v]) for v in range(1, 6)] + [(-1, name)],
                             True, 0, True, 0)

    # They all live on different floors: each floor has at most one person.
    for v in range(1, 6):
        solver.addConstraint([(1, on_floor[name][v]) for name in names], False, 0, True, 1)

    # Miller lives on a higher floor than Cooper.
    solver.addConstraint([(1, "M"), (-1, "C")], True, 1)

    # Smith and Fletcher, and Fletcher and Cooper, do not live on neighbouring floors.
    not_adjacent("S", "F")
    not_adjacent("F", "C")

    return solver, {name: name for name in names}


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
