# csplib_010_social_golfers_problem: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

import mip


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in a group
    # Every golfer plays every week, so the golfers fill all the groups.
    n_golfers = n_groups * group_size

    model = mip.Model(solver_name="CBC")

    # plays[g][w][k] is 1 when golfer g plays in group k in week w
    plays = [
        [[model.add_var(f"p_{g}_{w}_{k}", var_type=mip.BINARY) for k in range(n_groups)]
         for w in range(n_weeks)]
        for g in range(n_golfers)
    ]

    # together[(a, b, w)] is 1 when golfers a and b play in the same group in week w
    together = {}
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            for w in range(n_weeks):
                together[(a, b, w)] = model.add_var(f"t_{a}_{b}_{w}", lb=0, ub=1, var_type=mip.CONTINUOUS)

    # The pair of golfers a and b, in either order, in week w.
    def together_pair(a, b, w):
        return together[(min(a, b), max(a, b), w)]

    # assign[i][j] is the group golfer i plays in during week j
    assign = [[model.add_var(f"assign_{i}_{j}", lb=0, ub=n_groups - 1, var_type=mip.INTEGER)
               for j in range(n_weeks)] for i in range(n_golfers)]

    # Each golfer plays in exactly one group each week.
    for g in range(n_golfers):
        for w in range(n_weeks):
            model += mip.xsum(plays[g][w][k] for k in range(n_groups)) == 1

    # Each group has exactly group_size golfers in each week.
    for w in range(n_weeks):
        for k in range(n_groups):
            model += mip.xsum(plays[g][w][k] for g in range(n_golfers)) == group_size

    # Golfers who play in the same group in a week are marked together that week.
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            for w in range(n_weeks):
                for k in range(n_groups):
                    model += together_pair(a, b, w) >= plays[a][w][k] + plays[b][w][k] - 1

    # Two golfers are together in at most one week.
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            model += mip.xsum(together_pair(a, b, w) for w in range(n_weeks)) <= 1

    # Each golfer plays with exactly group_size - 1 others each week.
    for g in range(n_golfers):
        for w in range(n_weeks):
            model += mip.xsum(together_pair(g, h, w) for h in range(n_golfers) if h != g) == group_size - 1

    # The group number of each golfer in each week is the group the golfer plays in.
    for i in range(n_golfers):
        for j in range(n_weeks):
            model += assign[i][j] == mip.xsum(k * plays[i][j][k] for k in range(n_groups))

    # Any schedule that meets the rules above is a solution, so there is no objective.
    return model, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
