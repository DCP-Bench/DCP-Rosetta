# autoref: a SCIP (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python autoref.py autoref.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Autoreferential series: find a series S = (s0, s1, ..., sn, sn+1) such
    that for every i from 0 to n the value i occurs exactly s_i times in S,
    and the last entry s_(n+1) equals m. The output s is the series S."""
    n = instance["n"]  # n > 0: the values 0..n each have a constrained count; S has n + 2 entries
    m = instance["m"]  # m >= 0: the required last entry s_(n+1)
    length = n + 2     # S has the entries s_0 .. s_(n+1)

    # Assumption: every entry of S is one of the values 0..n. The statement counts
    # occurrences only of the values 0..n, so the counts cover all n + 2 entries of S
    # only when no entry is above n. The model takes this as given; the statement
    # does not spell it out.
    values = np.arange(n + 1)

    model = Model("autoref")

    # b[j, v] is 1 when entry s_j has the value v, and 0 when not. Counting the
    # occurrences of a value needs one 0/1 per (entry, value) pair, so the entries
    # are modelled one-hot rather than as plain integers.
    b = model.addMatrixVar((length, n + 1), vtype="B", name="b")

    # Each entry takes exactly one value.
    model.addMatrixCons(b.sum(axis=1) == 1)

    # The value of entry j is the weighted sum of its one-hot row (the output s).
    s = (b * values).sum(axis=1)

    # counts[v] is the number of entries of S equal to v.
    counts = b.sum(axis=0)

    # For each i from 0 to n, the number of occurrences of i in S is s_i.
    model.addMatrixCons(counts == s[: n + 1])

    # The last entry s_(n+1) is m.
    model.addCons(s[n + 1] == m)

    # The problem has no objective: it is a satisfaction problem.
    return model, {"s": s}


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
