# csplib_006_golomb_rulers: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from itertools import combinations

from pyscipopt import Model, quicksum


def tri(k):
    # k(k+1)/2: the least sum of k distinct positive whole numbers
    return k * (k + 1) // 2


def create_model(instance):
    """A Golomb ruler has m marks at whole-number positions 0 = a_0 < a_1 < ... < a_(m-1)
    whose m(m-1)/2 pairwise distances are all different. Find the shortest Golomb ruler,
    the one whose length a_(m-1) is least."""
    m = instance["size"]  # the number of marks m on the ruler

    model = Model("golomb_ruler")

    # Upper bound on every mark position, size * size. This is an ASSUMPTION, not a consequence
    # of the statement: the optimal rulers of the listed
    # instances lie below it. It only limits the search space; if no ruler fitted below it, the
    # solver would report no solution.
    upper = m * m

    # marks[i] is the position of mark i (0-indexed). The first mark is at 0, and the last mark,
    # marks[m-1], is the length of the ruler. Every gap between consecutive marks is a distance
    # between two marks, so the gaps are distinct positive whole numbers: the i gaps before mark i
    # sum to at least tri(i), and the m-1-i gaps after it sum to at least tri(m-1-i), which
    # the ruler must leave room for below the upper bound.
    marks = [model.addVar(f"mark_{i}", vtype="I", lb=tri(i), ub=upper - tri(m - 1 - i))
             for i in range(m)]
    model.addCons(marks[0] == 0)

    # The marks are strictly increasing. SCIP has no strict <, so each mark is at least one
    # more than the mark before it.
    for i in range(m - 1):
        model.addCons(marks[i + 1] - marks[i] >= 1)

    # Each pair of marks i < j has exactly one distance, a value d. SCIP has no all-different
    # constraint, so the distance is one-hot: use[i, j, d] is 1 when the distance between marks
    # i and j is d. The j-i gaps between the two marks are distinct positive whole numbers, so
    # d >= tri(j-i); and by the bounds on the marks, d <= upper - tri(i) - tri(m-1-j).
    use = {}
    pairs_with = {}  # pairs_with[d]: the use variables of every pair for the distance d
    for i, j in combinations(range(m), 2):
        lo, hi = tri(j - i), upper - tri(i) - tri(m - 1 - j)
        for d in range(lo, hi + 1):
            use[i, j, d] = model.addVar(f"use_{i}_{j}_{d}", vtype="B")
            pairs_with.setdefault(d, []).append(use[i, j, d])
        # Each pair of marks has exactly one distance.
        model.addCons(quicksum(use[i, j, d] for d in range(lo, hi + 1)) == 1)
        # The distance between marks i and j is the difference of their positions.
        model.addCons(marks[j] - marks[i] == quicksum(d * use[i, j, d] for d in range(lo, hi + 1)))

    # All pairwise distances are different: each value d is the distance of at most one pair.
    for users in pairs_with.values():
        if len(users) > 1:
            model.addCons(quicksum(users) <= 1)

    # Segment cut (implied by the distinct distances; it is for speed, the model is correct
    # without it). The g(g+1)/2 distances among the g+1 marks from mark i to mark j, with
    # g = j-i, are distinct positive whole numbers, so they sum to at least tri(g(g+1)/2).
    # Written in the marks, mark k has coefficient 2k - i - j in that sum.
    for i, j in combinations(range(m), 2):
        if j - i >= 2:  # for j = i+1 the cut only says the gap is at least 1, as above
            g = j - i
            model.addCons(quicksum((2 * k - i - j) * marks[k] for k in range(i, j + 1))
                          >= tri(g * (g + 1) // 2))

    # Search order (a solver setting, no constraint): branch on the mark positions before the
    # one-hot distance variables, so the search places marks the way a person would.
    for mark in marks:
        model.chgVarBranchPriority(mark, 10)

    # The objective: minimise the length of the ruler, the position of its last mark.
    model.setObjective(marks[m - 1], "minimize")

    return model, {"length": marks[m - 1], "marks": marks}


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
