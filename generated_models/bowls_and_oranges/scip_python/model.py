# bowls_and_oranges: a SCIP (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Bowls stand in a line at 1 metre intervals, numbered 1 to n. Place all m
    oranges, at most one per bowl, so that no three oranges A, B, C have the
    distance A-B equal to the distance B-C (no three in arithmetic progression).
    Report the bowl numbers used, in ascending order."""
    n = instance["n"]  # the number of bowls in the line; bowl numbers run 1..n
    m = instance["m"]  # the number of oranges to place

    model = Model("bowls_and_oranges")

    # y[k][p] is 1 when the k-th orange from the left sits in bowl index p,
    # i.e. bowl number p + 1. Oranges are interchangeable, so ordering them
    # left to right is what the output asks for; the bowl index is 0-based
    # here and shifted to the 1-based bowl number only in x.
    y = [[model.addVar(f"y_{k}_{p}", vtype="B") for p in range(n)] for k in range(m)]

    # x[k] is the bowl number of the k-th orange from the left (1..n). This is
    # the reported output, an integer variable so it can be read and blocked.
    x = [model.addVar(f"x_{k}", vtype="I", lb=1, ub=n) for k in range(m)]

    # Each orange is in exactly one bowl.
    for k in range(m):
        model.addCons(quicksum(y[k][p] for p in range(n)) == 1)

    # Each bowl holds at most one orange. occ[p] is the number of oranges in
    # bowl index p: 1 when the bowl is used, 0 when empty.
    occ = [quicksum(y[k][p] for k in range(m)) for p in range(n)]
    for p in range(n):
        model.addCons(occ[p] <= 1)

    # Bowl number of each orange: x[k] = p + 1 when the orange sits in bowl index p.
    for k in range(m):
        model.addCons(x[k] == quicksum((p + 1) * y[k][p] for p in range(n)))

    # The bowls are listed in ascending order; bowls are distinct, so strictly.
    for k in range(m - 1):
        model.addCons(x[k] + 1 <= x[k + 1])

    # No three oranges in arithmetic progression: for bowl indices p < q < r
    # with q - p = r - q, not all three bowls may hold an orange. Written as
    # occ[p] + occ[q] + occ[r] <= 2. Every progression is seen with its
    # first bowl p and step d; r = p + 2d must stay inside the line.
    for p in range(n):
        for d in range(1, (n - 1 - p) // 2 + 1):
            model.addCons(occ[p] + occ[p + d] + occ[p + 2 * d] <= 2)

    # No objective: any placement that satisfies the constraints is an answer.

    return model, {"x": x}


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
