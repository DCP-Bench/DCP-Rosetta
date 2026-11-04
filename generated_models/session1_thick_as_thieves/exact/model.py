# session1_thick_as_thieves: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install exact numpy`) with:
#   python session1_thick_as_thieves.py

from exact import Exact

SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def create_model(instance):
    """Six suspects, at most two of them guilty: the innocent tell the truth
    and the guilty lie. Who is guilty?"""
    solver = Exact()

    # Exact identifies its variables by name.
    # Each suspect is 1 when guilty, and 0 when innocent.
    for name in SUSPECTS:
        solver.addVariable(name, 0, 1)

    # The getaway car barely held two, so at most two suspects are guilty.
    solver.addConstraint([(1, name) for name in SUSPECTS], False, 0, True, 2)

    # Each suspect is guilty exactly when what he said is false.

    # Bill: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is not.
    solver.addConstraint([(1, "bill"), (1, "crackitt")], True, 1, True, 1)

    # Dodgy: "If Crackitt did it, Bill did it with him." This is false exactly when
    # Crackitt is guilty and Bill is not, so Dodgy is guilty exactly then.
    solver.addConstraint([(1, "dodgy"), (-1, "crackitt")], False, 0, True, 0)
    solver.addConstraint([(1, "dodgy"), (1, "bill")], False, 0, True, 1)
    solver.addConstraint([(1, "dodgy"), (-1, "crackitt"), (1, "bill")], True, 0)

    # Edgy: "Nobody did it alone." This is false exactly when at most one suspect is
    # guilty, so Edgy is guilty exactly then.
    solver.addReification("edgy", True, [(-1, name) for name in SUSPECTS], -1)

    # Fingers: "That's right: it was Artie and Dodgy together." This is false exactly
    # when Artie and Dodgy are not both guilty, so Fingers is guilty exactly then.
    solver.addConstraint([(1, "fingers"), (1, "artie")], True, 1)
    solver.addConstraint([(1, "fingers"), (1, "dodgy")], True, 1)
    solver.addConstraint([(1, "fingers"), (1, "artie"), (1, "dodgy")], False, 0, True, 2)

    return solver, {name: name for name in SUSPECTS}


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
