# session3_kidney_exchange: a SCIP (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from pyscipopt import Model


def create_model(instance):
    """A kidney exchange on a waiting list of people. Each person can donate a kidney
    to some of the others. Choose the donations so that as many people as possible
    receive a kidney, where anyone who gives a kidney must receive one and no person
    receives more than one kidney."""
    n = instance["num_people"]       # n: the number of people on the waiting list
    compatible = instance["compatible"]  # compatible[i]: the people that person i can donate a kidney to

    model = Model("session3_kidney_exchange")

    # Assumption about the data: list positions count people from 0 and the
    # people named inside the lists count from 1, so person p is matrix index p - 1.
    # Only the pairs named in compatible may be donations: ub is 0 for every other
    # pair, which fixes that donation to 0.
    may_donate = [[1 if j + 1 in compatible[i] else 0 for j in range(n)] for i in range(n)]

    # x[i, j] is 1 when person i donates a kidney to person j, and 0 when not.
    # The donations form a table of people by people, so they are one matrix variable.
    x = model.addMatrixVar((n, n), vtype="B", name="x", ub=may_donate)

    # Each person's donations received: the column sums of x. Each person's donations given: the row sums.
    received = x.sum(axis=0)
    given = x.sum(axis=1)

    # No person receives more than one kidney.
    model.addMatrixCons(received <= 1)

    # Anyone who gives a kidney must receive one. Every donation has one giver and one
    # receiver, so the totals of given and received agree, and this inequality holds
    # with equality for every person.
    model.addMatrixCons(given <= received)

    # Maximise the number of people who receive a kidney, which is the number of donations.
    model.setObjective(x.sum(), "maximize")

    return model, {"transplants": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
