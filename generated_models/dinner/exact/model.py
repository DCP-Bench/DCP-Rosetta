# dinner: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install exact numpy`) with:
#   python dinner.py

from exact import Exact


def create_model(instance):
    """Twenty people go to dinner, grandparents, parents and children, and the
    bill is $20: how many of each go?"""
    solver = Exact()

    # Exact identifies its variables by name.
    # The number of grandparents going to dinner is 1 to 6.
    solver.addVariable("grandparents", 1, 6)
    # The number of parents going to dinner is 1 to 10.
    solver.addVariable("parents", 1, 10)
    # The number of children going to dinner is 1 to 40.
    solver.addVariable("children", 1, 40)

    # Twenty people go to dinner in all.
    solver.addConstraint([(1, "grandparents"), (1, "parents"), (1, "children")], True, 20, True, 20)

    # The bill is $20, which is 40 half dollars. A grandparent costs $3 (6 half dollars), a parent
    # $2 (4) and a child $0.50 (1).
    solver.addConstraint([(6, "grandparents"), (4, "parents"), (1, "children")], True, 40, True, 40)

    return solver, {"grandparents": "grandparents", "parents": "parents", "children": "children"}


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
