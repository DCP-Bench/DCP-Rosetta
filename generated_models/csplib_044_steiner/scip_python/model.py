# csplib_044_steiner: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """The ternary Steiner problem of order n: find n(n-1)/6 triples of
    distinct elements from 1 to n such that any two triples have at most one
    element in common. sets[t][e] is 1 when triple t contains element e+1."""
    n = instance["n"]  # the order: the number of elements, 1 to n
    # n(n-1)/6 triples; the statement requires n mod 6 to be 1 or 3, so this is a whole number
    num_triples = n * (n - 1) // 6

    model = Model("csplib_044_steiner")

    # x[t, e] is 1 when triple t contains element e+1, and 0 when not
    x = model.addMatrixVar((num_triples, n), vtype="B", name="x")

    # Each triple has exactly three elements
    model.addMatrixCons(x.sum(axis=1) == 3)

    # both[t, i, j] is 1 when triple t contains both element i and element j
    # (0-based i < j); addConsAnd ties it to the AND of the two memberships in both directions
    both = {}
    for t in range(num_triples):
        for i in range(n):
            for j in range(i + 1, n):
                both[t, i, j] = model.addVar(vtype="B", name=f"both_{t}_{i}_{j}")
                model.addConsAnd([x[t, i], x[t, j]], both[t, i, j])

    # Two triples sharing two elements would share a pair of elements, so any two
    # triples share at most one element exactly when every pair of elements lies
    # in at most one triple. Each triple holds three pairs, and there are
    # n(n-1)/6 triples, so the n(n-1)/2 pairs are each in exactly one triple.
    for i in range(n):
        for j in range(i + 1, n):
            model.addCons(quicksum(both[t, i, j] for t in range(num_triples)) <= 1)

    # Each element lies in exactly (n-1)/2 triples. Upper bound: the triples through
    # element e each use two of the other n-1 elements, and by the pair constraints
    # no such pair is used twice, so there are at most (n-1)/2 of them. Exactly: the
    # triples have 3 * n(n-1)/6 = n(n-1)/2 element slots in all, which is n times
    # the bound, so no element can fall short of it. The constraint follows from the
    # rest of the model; it is stated as a search aid, because SCIP's LP relaxation
    # does not derive it and the search is much slower without it.
    model.addMatrixCons(x.sum(axis=0) == (n - 1) // 2)

    # No objective: any triple system with these properties is a solution.
    return model, {"sets": x}


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
