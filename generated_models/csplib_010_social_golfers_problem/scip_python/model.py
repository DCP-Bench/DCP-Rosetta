# csplib_010_social_golfers_problem: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """The social golfers problem: golfers play once a week, always in groups
    of the same size, and no two golfers may share a group on more than one
    occasion. Output assign[i][j] is the group, numbered from 0, of golfer i
    in week j."""
    group_size = instance["group_size"]  # the number of golfers in each group
    n_groups = instance["n_groups"]      # the number of groups that play each week
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    # Every week the golfers fill n_groups groups of group_size, so there are
    # n_groups * group_size golfers in all.
    n_golfers = n_groups * group_size

    model = Model("social_golfers")

    # plays[g, w, k] is 1 when golfer g is in group k in week w, and 0 when not
    # (indices: golfer, week, group). The group of a golfer is kept as one binary
    # per group rather than as one integer, because the meeting constraints below
    # need to see directly which group each golfer is in.
    plays = model.addMatrixVar((n_golfers, n_weeks, n_groups), vtype="B", name="plays")

    # Every golfer plays in exactly one group in every week.
    model.addMatrixCons(plays.sum(axis=2) == 1)

    # Every group holds exactly group_size golfers in every week.
    model.addMatrixCons(plays.sum(axis=0) == group_size)

    # Symmetry breaking. Renaming the golfers, or renaming the groups of one
    # week, keeps a schedule valid, so each schedule has many equivalent
    # numberings. Week 0 is numbered in blocks: golfers 0 to group_size - 1 in
    # group 0, the next block in group 1, and so on. Golfer 0 is then put in
    # group 0 in every later week. Every schedule has such a numbering, so at
    # least one numbering of each schedule stays in the model.
    first_week = np.eye(n_groups, dtype=int)[np.arange(n_golfers) // group_size]
    model.addMatrixCons(plays[:, 0, :] == first_week)
    model.addMatrixCons(plays[0, 1:, 0] == 1)

    # pairs lists each unordered pair of golfers once, as (g, h) with g < h.
    pairs = [(g, h) for g in range(n_golfers) for h in range(g + 1, n_golfers)]

    # Golfers g and h meet in week w when they are in the same group k that week.
    # meet[p, w, k] is 1 when both golfers of pair p are in group k in week w:
    # a logical and of two binaries, which addConsAnd states in both directions.
    meet = model.addMatrixVar((len(pairs), n_weeks, n_groups), vtype="B", name="meet")
    for p, (g, h) in enumerate(pairs):
        for w in range(n_weeks):
            for k in range(n_groups):
                model.addConsAnd([plays[g, w, k], plays[h, w, k]], meet[p, w, k])

    # Two golfers share a group at most once over all weeks. Each golfer is in
    # one group per week, so for a pair at most one k is 1 in each week, and the
    # sum over weeks and groups counts the weeks in which the pair meets.
    model.addMatrixCons(meet.sum(axis=(1, 2)) <= 1)

    # The output: the group number of each golfer in each week, as the
    # weighted sum over the one-hot choice (the group number is the index k).
    assign = [[quicksum(k * plays[g, w, k] for k in range(n_groups))
               for w in range(n_weeks)]
              for g in range(n_golfers)]

    return model, {"assign": assign}


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
