# five_statements: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install z3-solver numpy`) with:
#   python five_statements.py

import z3


def create_model(instance):
    """Five statements: statement i says that exactly i of these five statements
    are false. Determine which of the statements are true."""
    n_statements = 5  # the number of statements

    # statements[i] is true when statement i + 1 is true
    statements = z3.BoolVector("statements", n_statements)

    # Each statement counts one toward the number of false statements when it is false.
    false_statements = [(z3.Not(s), 1) for s in statements]

    solver = z3.Solver()

    # Statement i + 1 is true exactly when precisely i + 1 of the statements are false.
    solver.add([statements[i] == z3.PbEq(false_statements, i + 1)
                for i in range(n_statements)])

    return solver, {"statements": list(statements)}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
