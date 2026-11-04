# fibonacci_even: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install exact numpy`) with:
#   python fibonacci_even.py

from exact import Exact


def create_model(instance):
    """Each new term in the Fibonacci sequence is the sum of the previous two.
    Find the sum of the even-valued terms that do not exceed four million."""
    n_terms = 35        # terms f_1 to f_35 are considered; f_34 is the first term above four million
    limit = 4000000     # terms must not exceed four million
    top = 10 ** 7       # the largest value a term can take; every term considered is below it

    solver = Exact()

    # Exact identifies its variables by name.
    # f[i] is the i-th Fibonacci number, with f[0] = 0 and f[1] = 1
    f = [f"f_{i}" for i in range(n_terms + 1)]
    solver.addVariable(f[0], 0, 0)
    solver.addVariable(f[1], 1, 1)
    solver.addVariable(f[2], 1, 1)
    for name in f[3:]:
        solver.addVariable(name, 0, top)

    # Each term from the fourth on is the sum of the previous two.
    for i in range(3, n_terms + 1):
        solver.addConstraint([(1, f[i]), (-1, f[i - 1]), (-1, f[i - 2])], True, 0, True, 0)

    # added[i - 1] is what term i adds to the answer: the term itself when it is even and does
    # not exceed four million, and 0 otherwise
    added = []
    for i in range(1, n_terms + 1):
        # half_i and odd_i split term i into 2 * half_i + odd_i, so odd_i is 1 when term i is odd
        half, odd = f"half_{i}", f"odd_{i}"
        solver.addVariable(half, 0, top // 2)
        solver.addVariable(odd, 0, 1)
        solver.addConstraint([(2, half), (1, odd), (-1, f[i])], True, 0, True, 0)

        # within_i is 1 when term i does not exceed four million, and 0 when it does
        within, counted, part = f"within_{i}", f"counted_{i}", f"added_{i}"
        solver.addVariable(within, 0, 1)
        solver.addReification(within, True, [(-1, f[i])], -limit)

        # counted_i is 1 exactly when term i is even and within the limit
        solver.addVariable(counted, 0, 1)
        solver.addConstraint([(1, counted), (-1, within)], False, 0, True, 0)
        solver.addConstraint([(1, counted), (1, odd)], False, 0, True, 1)
        solver.addConstraint([(1, counted), (-1, within), (1, odd)], True, 0)

        # added_i is term i when it is counted, and 0 otherwise
        solver.addVariable(part, 0, top)
        solver.addMultiplication([counted, f[i]], True, part, True, part)
        added.append(part)

    # res is the sum of the even terms that do not exceed four million, at most one hundred million
    solver.addVariable("res", 0, 10 ** 8)
    solver.addConstraint([(1, part) for part in added] + [(-1, "res")], True, 0, True, 0)

    return solver, {"res": "res"}


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
