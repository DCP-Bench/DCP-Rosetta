# five_statements: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install mip numpy`) with:
#   python five_statements.py

import mip


def create_model(instance):
    """Five statements say that exactly one, exactly two, exactly three, exactly
    four and exactly five of these statements are false. Determine which of
    them are true."""
    n_statements = 5  # the number of statements

    model = mip.Model(solver_name="CBC")

    # statements[i] is 1 when statement i + 1 is true, and 0 when it is false.
    statements = [model.add_var(f"statement_{i + 1}", var_type=mip.BINARY) for i in range(n_statements)]

    # count[j] is 1 when exactly j of the statements are false, and 0 when not.
    count = [model.add_var(f"count_{j}", var_type=mip.BINARY) for j in range(n_statements + 1)]

    # The number of false statements is exactly one of 0 to n_statements.
    model += mip.xsum(count) == 1

    # The number of false statements.
    n_false = mip.xsum(j * count[j] for j in range(n_statements + 1))

    # The statements that are true are the ones that are not false.
    model += mip.xsum(statements) == n_statements - n_false

    # Statement k is true exactly when k of the statements are false.
    for k in range(1, n_statements + 1):
        model += statements[k - 1] == count[k]

    return model, {"statements": statements}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
