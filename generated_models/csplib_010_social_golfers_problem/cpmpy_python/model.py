# csplib_010_social_golfers_problem: a CPMpy model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

import cpmpy as cp


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in a group
    # Every golfer plays every week, so the golfers fill all the groups.
    n_golfers = n_groups * group_size

    # assign[g, w] is the group that golfer g plays in during week w
    assign = cp.intvar(0, n_groups - 1, shape=(n_golfers, n_weeks), name="assign")

    model = cp.Model()

    # Each group has exactly group_size golfers in every week.
    for w in range(n_weeks):
        for k in range(n_groups):
            model.add(cp.sum(assign[:, w] == k) == group_size)

    # Two golfers play in the same group in at most one week.
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            model.add(cp.sum(assign[g1, :] == assign[g2, :]) <= 1)

    return model, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
