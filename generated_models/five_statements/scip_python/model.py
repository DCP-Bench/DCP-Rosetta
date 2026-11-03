# five_statements: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python five_statements.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Five statements, statement k saying that exactly k of the five statements
    are false. Determine which of the statements are true.

    The instance file is empty ([]): the statements are fixed by the problem, so
    the instance is not read.
    """
    n = 5  # the number of statements, fixed by the problem
    model = Model("five_statements")

    # t[i] is 1 when statement i+1 is true, and 0 when it is false
    t = [model.addVar(f"t_{i}", vtype="B") for i in range(n)]

    # how many of the statements are true
    true_count = quicksum(t)

    for i in range(n):
        says_false = i + 1               # statement i+1 says exactly i+1 statements are false
        says_true = n - says_false       # so it says exactly this many are true

        # The statement is true exactly when true_count == says_true. An indicator enforces
        # one inequality and takes no equality, so the equality is split into two binaries:
        # at_least[i] is 1 exactly when true_count >= says_true, and at_most[i] is 1 exactly
        # when true_count <= says_true. Each one is tied both ways by a pair of indicators.
        at_least = model.addVar(f"at_least_{i}", vtype="B")
        model.addConsIndicator(true_count >= says_true, binvar=at_least)
        model.addConsIndicator(true_count <= says_true - 1, binvar=at_least, activeone=False)

        at_most = model.addVar(f"at_most_{i}", vtype="B")
        model.addConsIndicator(true_count <= says_true, binvar=at_most)
        model.addConsIndicator(true_count >= says_true + 1, binvar=at_most, activeone=False)

        # Statement i+1 is true exactly when both hold, in both directions.
        model.addConsAnd([at_least, at_most], t[i])

    return model, {"statements": t}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
