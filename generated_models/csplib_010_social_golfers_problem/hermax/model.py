# csplib_010_social_golfers_problem: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Social golfers problem: golfers play once a week, in groups of a fixed size, so that
    every golfer plays in exactly one group each week, and no two golfers are in the same
    group on more than one occasion. Report the group of each golfer in each week."""
    group_size = instance["group_size"]  # the number of golfers in each group
    n_groups = instance["n_groups"]      # the number of groups played in each week
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_golfers = n_groups * group_size    # every golfer plays each week, so the golfers fill all groups

    m = Model()

    # assign[i][w] is the group (0-based) that golfer i plays in during week w
    assign = m.int_matrix("assign", n_golfers, n_weeks, 0, n_groups - 1)

    # Each week, every group holds exactly group_size golfers.
    for w in range(n_weeks):
        for g in range(n_groups):
            m &= (sum_expr(assign[i][w] == g for i in range(n_golfers)) == group_size)

    # Two golfers meet in a week when they are in the same group that week.
    # No two golfers may meet in more than one week.
    for i in range(n_golfers):
        for j in range(i + 1, n_golfers):
            # meets[w] is true when golfers i and j share a group in week w
            meets = []
            for w in range(n_weeks):
                meet = m.bool()
                m &= (assign[i][w] == assign[j][w]).iff(meet)
                meets.append(meet)
            # golfers i and j meet in at most one week
            m &= (sum_expr(meets) <= 1)

    return m, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
