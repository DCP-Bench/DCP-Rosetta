# among: a SCIP (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python among.py among.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Among: find an array x of n entries, each a whole number from 0 to 7,
    such that exactly m entries of x take one of the values in v. Every other
    entry takes a value from 0 to 7 that is not in v."""
    n = instance["n"]  # n: the number of entries in x
    m = instance["m"]  # m: how many entries of x must take one of the values in v
    v = instance["v"]  # v: the values that exactly m entries of x must take one of

    # The values an entry of x may take: 0 to 7, as the problem statement says.
    # The bounds of x and the one-hot grid below both come from this range.
    DOMAIN = range(8)

    # The values of v that x can take, the ones the count below uses. A value
    # of v outside 0..7 has no grid column, so the count skips it.
    v_in_domain = [k for k in v if k in DOMAIN]

    model = Model("among")

    # x[i] is the value of entry i of x, a whole number from 0 to 7.
    x = [model.addVar(name=f"x_{i}", vtype="I", lb=min(DOMAIN), ub=max(DOMAIN))
         for i in range(n)]

    # is_value[i][k] is 1 when entry x[i] takes the value k, and 0 when not.
    # One grid column per value 0..7; a row is one-hot, so it is a 0/1 view of x[i].
    is_value = [[model.addVar(name=f"is_{i}_{k}", vtype="B") for k in DOMAIN]
                for i in range(n)]

    # Each entry of x takes exactly one value from 0 to 7.
    for i in range(n):
        model.addCons(quicksum(is_value[i]) == 1)

    # x[i] is the value its one-hot row selects, so the grid and x agree.
    for i in range(n):
        model.addCons(x[i] == quicksum(k * is_value[i][k] for k in DOMAIN))

    # Exactly m entries of x take one of the values in v.
    model.addCons(
        quicksum(is_value[i][k] for i in range(n) for k in v_in_domain) == m
    )

    # The problem asks for a feasible x only, so there is no objective.
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
