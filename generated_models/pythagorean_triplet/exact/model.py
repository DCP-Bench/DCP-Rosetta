# pythagorean_triplet: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install exact numpy`) with:
#   python pythagorean_triplet.py

from exact import Exact


def create_model(instance):
    """Find the Pythagorean triplet: natural numbers a, b and c with a^2 + b^2 = c^2 whose
    sum is 1000."""
    perimeter = 1000  # the sum a + b + c
    largest = perimeter // 2  # each number is less than the other two added together, so it is below half the sum

    solver = Exact()

    # Exact identifies its variables by name.
    # a, b and c are the natural numbers of the triplet, each at most largest
    for name in ("a", "b", "c"):
        solver.addVariable(name, 1, largest)

    # The three numbers add up to the perimeter.
    solver.addConstraint([(1, "a"), (1, "b"), (1, "c")], True, perimeter, True, perimeter)

    # The square of each number, for the Pythagorean relation.
    for name in ("a", "b", "c"):
        solver.addVariable(f"{name}_squared", 1, largest * largest)
        solver.addMultiplication([name, name], True, f"{name}_squared", True, f"{name}_squared")

    # a^2 + b^2 = c^2
    solver.addConstraint([(1, "a_squared"), (1, "b_squared"), (-1, "c_squared")], True, 0, True, 0)

    return solver, {"a": "a", "b": "b", "c": "c"}


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
