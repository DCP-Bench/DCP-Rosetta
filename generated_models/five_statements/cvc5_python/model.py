# five_statements: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install cvc5 numpy`) with:
#   python five_statements.py

import cvc5.pythonic as c5


def create_model(instance):
    """Five statements say that exactly one, exactly two, exactly three,
    exactly four and exactly five of these statements are false, in that order.
    Determine which of the statements are true."""
    n_statements = 5  # the number of statements

    # statements[i] is true when statement i + 1 is true
    statements = [c5.Bool(f"statements_{i}") for i in range(n_statements)]

    # The number of false statements
    n_false = c5.Sum([c5.If(c5.Not(s), 1, 0) for s in statements])

    solver = c5.Solver()

    # Statement i + 1 is true exactly when i + 1 statements are false.
    solver.add([statements[i] == (n_false == i + 1) for i in range(n_statements)])

    return solver, {"statements": statements}


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
