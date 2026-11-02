# abbots_puzzle: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install exact numpy`) with:
#   python abbots_puzzle.py

from exact import Exact


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    people = 100
    bushels = 100
    half_bushels = 2 * bushels  # the corn in halves, so that every share is a whole number

    solver = Exact()

    # Exact identifies its variables by name.
    # The numbers of men, women and children, each at most the number of people
    for name in ("men", "women", "children"):
        solver.addVariable(name, 0, people)

    # Everyone is a man, a woman or a child.
    solver.addConstraint([(1, "men"), (1, "women"), (1, "children")], True, people, True, people)

    # The corn is all shared out: a man gets 6 halves, a woman 4 and a child 1.
    solver.addConstraint([(6, "men"), (4, "women"), (1, "children")],
                         True, half_bushels, True, half_bushels)

    # There are five times as many women as men.
    solver.addConstraint([(5, "men"), (-1, "women")], True, 0, True, 0)

    return solver, {"men": "men", "women": "women", "children": "children"}


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
