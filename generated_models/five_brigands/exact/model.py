# five_brigands: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install exact numpy`) with:
#   python five_brigands.py

from exact import Exact


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, captured
    exactly 200 doubloons altogether. If Alfonso had twelve times as many, Benito three
    times as many, Carlos the same, Diego half as many and Esteban a third as many, they
    would still have 200 doubloons altogether. Each brigand has at least one doubloon.
    How many doubloons has each?"""
    total = 200  # the doubloons the brigands captured altogether

    solver = Exact()

    # Exact identifies its variables by name.
    # Doubloons of Alfonso (A), Benito (B), Carlos (C), Diego (D) and Esteban (E), at least one each
    names = ["A", "B", "C", "D", "E"]
    for name in names:
        solver.addVariable(name, 1, total)

    # Together they have all the doubloons.
    solver.addConstraint([(1, name) for name in names], True, total, True, total)
    # With the changed amounts the total is still 200. Multiplied by 6 to avoid fractions: 72 A + 18 B + 6 C + 3 D + 2 E = 1200.
    solver.addConstraint([(72, "A"), (18, "B"), (6, "C"), (3, "D"), (2, "E")], True, 6 * total, True, 6 * total)

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
