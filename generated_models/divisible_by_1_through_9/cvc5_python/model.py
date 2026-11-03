# divisible_by_1_through_9: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install cvc5 numpy`) with:
#   python divisible_by_1_through_9.py

import cvc5.pythonic as c5


def create_model(instance):
    """Find a 10-digit number that uses each digit 0 to 9 exactly once, where the
    number formed by its first n digits is divisible by n, for n = 1 to 10."""
    # digits[i] is the digit at position i, read from left to right.
    digits = c5.IntVector("digit", 10)

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each digit is between 0 and 9.
    for d in digits:
        solver.add(d >= 0, d <= 9)

    # Each of the digits 0 to 9 is used exactly once.
    solver.add(c5.Distinct(*digits))

    # The number formed by the first n digits is divisible by n.
    prefix = 0
    for n in range(1, 11):
        prefix = prefix * 10 + digits[n - 1]
        solver.add(prefix % n == 0)

    return solver, {"digits": digits}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
