# csplib_010_social_golfers_problem: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

from pycsp3 import *


def create_model(instance):
    """A golf club has n_groups * group_size golfers who play once a week, always in n_groups
    groups of group_size golfers, over n_weeks weeks. Find a schedule of play in which no two
    golfers play in the same group on more than one occasion."""
    n_weeks = instance["n_weeks"]  # the number of weeks of play
    n_groups = instance["n_groups"]  # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in each group
    n_golfers = n_groups * group_size  # every golfer plays in every week, in one of the groups

    # assign[i][j] is the group number of golfer i in week j, numbered from 0
    assign = VarArray(size=[n_golfers, n_weeks], dom=range(n_groups))

    satisfy(
        # each group has group_size golfers in every week
        [
            Cardinality(assign[:, week], occurrences={group: group_size for group in range(n_groups)})
            for week in range(n_weeks)
        ],
        # two golfers play in the same group in at most one week
        [
            Sum(assign[p][week] == assign[q][week] for week in range(n_weeks)) <= 1
            for p in range(n_golfers)
            for q in range(p + 1, n_golfers)
        ],
    )

    return {"assign": assign}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("assign", "=")
        for row in outputs["assign"]:
            print(values(row))
    else:
        print("No solution:", status())
