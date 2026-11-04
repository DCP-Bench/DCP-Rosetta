# five_statements: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install exact numpy`) with:
#   python five_statements.py

from exact import Exact


def create_model(instance):
    """Five statements: statement k says that exactly k of these five statements are
    false, for k from 1 to 5. Decide which statements are true."""
    n_statements = 5  # the number of statements

    solver = Exact()

    # Exact identifies its variables by name.
    # statements[i] is 1 when statement i + 1 is true
    statements = [f"statements_{i}" for i in range(n_statements)]
    for name in statements:
        solver.addVariable(name, 0, 1)

    # exactly_false[k] is 1 when exactly k of the statements are false, for k from 0 to n_statements
    exactly_false = [f"exactly_{k}_false" for k in range(n_statements + 1)]
    for name in exactly_false:
        solver.addVariable(name, 0, 1)
    # Exactly one of these counts of false statements holds.
    solver.addConstraint([(1, name) for name in exactly_false], True, 1, True, 1)
    # The true statements number n_statements minus the false ones.
    solver.addConstraint([(1, name) for name in statements] +
                         [(-(n_statements - k), exactly_false[k]) for k in range(n_statements + 1)],
                         True, 0, True, 0)

    # Statement i + 1 is true exactly when exactly i + 1 statements are false.
    for i in range(n_statements):
        solver.addConstraint([(1, statements[i]), (-1, exactly_false[i + 1])], True, 0, True, 0)

    return solver, {"statements": statements}


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
