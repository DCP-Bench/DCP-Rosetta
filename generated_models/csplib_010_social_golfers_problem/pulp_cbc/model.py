# csplib_010_social_golfers_problem: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

import pulp


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in a group
    n_golfers = n_groups * group_size    # the number of golfers, who fill all the groups

    golfers, weeks, groups = range(n_golfers), range(n_weeks), range(n_groups)

    problem = pulp.LpProblem("social_golfers", pulp.LpMinimize)

    # plays[g][w][k] is 1 when golfer g plays in group k in week w.
    plays = [[[pulp.LpVariable(f"plays_{g}_{w}_{k}", cat="Binary") for k in groups]
              for w in weeks] for g in golfers]

    # assign[g][w] is the group that golfer g plays in during week w.
    assign = [[pulp.LpVariable(f"assign_{g}_{w}", 0, n_groups - 1, cat="Integer")
               for w in weeks] for g in golfers]

    # Every golfer plays in exactly one group each week, and assign gives that group.
    for g in golfers:
        for w in weeks:
            problem += pulp.lpSum(plays[g][w]) == 1
            problem += assign[g][w] == pulp.lpSum(k * plays[g][w][k] for k in groups)

    # Every group has exactly group_size golfers in every week.
    for w in weeks:
        for k in groups:
            problem += pulp.lpSum(plays[g][w][k] for g in golfers) == group_size

    # together[w] is 1 when two golfers play in the same group in week w. Two golfers meet in at most one week.
    for g1 in golfers:
        for g2 in range(g1 + 1, n_golfers):
            together = [pulp.LpVariable(f"together_{g1}_{g2}_{w}", 0, 1) for w in weeks]
            for w in weeks:
                for k in groups:
                    problem += together[w] >= plays[g1][w][k] + plays[g2][w][k] - 1
            problem += pulp.lpSum(together) <= 1

    return problem, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
