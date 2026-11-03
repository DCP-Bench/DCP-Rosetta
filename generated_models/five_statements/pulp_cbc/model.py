# five_statements: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install pulp numpy`) with:
#   python five_statements.py

import pulp


def create_model(instance):
    """Five statements: exactly one of them is false; exactly two of them are false;
    exactly three are false; exactly four are false; exactly five are false. Determine
    which of the statements are true."""
    n = 5  # the number of statements

    problem = pulp.LpProblem("five_statements", pulp.LpMinimize)

    # statements[i] is 1 when statement i + 1 is true, and 0 when it is false
    statements = [pulp.LpVariable(f"statement_{i}", cat="Binary") for i in range(n)]
    # false_count[k] is 1 when exactly k of the statements are false
    false_count = [pulp.LpVariable(f"false_count_{k}", cat="Binary") for k in range(n + 1)]

    # Exactly one count of false statements holds, and it is the number of statements that are false.
    problem += pulp.lpSum(false_count) == 1
    problem += n - pulp.lpSum(statements) == pulp.lpSum(k * var for k, var in enumerate(false_count))

    # Statement i + 1 is true exactly when exactly i + 1 of the statements are false.
    for i in range(n):
        problem += statements[i] == false_count[i + 1]

    return problem, {"statements": statements}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
