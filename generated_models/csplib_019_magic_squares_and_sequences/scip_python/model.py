# csplib_019_magic_squares_and_sequences: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Magic sequence of length n: a sequence x[0], ..., x[n-1] of integers between
    0 and n-1 such that, for every i, the number i occurs exactly x[i] times in the
    sequence."""
    n = instance["n"]  # the length of the sequence

    model = Model("magic_sequence")

    # x[i] is the i-th entry of the sequence, and also the number of times i occurs
    # in it. The entries are integers between 0 and n-1, as the statement says.
    x = model.addMatrixVar(n, vtype="I", lb=0, ub=n - 1, name="x")

    # b[j, v] is 1 when entry j of the sequence equals v, and 0 when not. SCIP has no
    # constraint that counts how often an integer variable takes a value, so the
    # occurrences are counted over these 0/1 indicators instead.
    b = model.addMatrixVar((n, n), vtype="B", name="b")

    values = np.arange(n)  # the values an entry can take: 0 to n-1, as in the statement

    # Each entry of the sequence takes exactly one value.
    model.addMatrixCons(b.sum(axis=1) == 1)
    # Entry j of the sequence is the value that b selects for it.
    model.addMatrixCons(x == b @ values)
    # The number i occurs x[i] times: the entries equal to i are counted down column i of b.
    model.addMatrixCons(b.sum(axis=0) == x)

    # No objective: the problem asks for any magic sequence, so any solution is an answer.
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
