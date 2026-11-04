# csplib_010_social_golfers_problem: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

from exact import Exact


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule their play so that
    no two golfers are in the same group more than once."""
    n_weeks = instance["n_weeks"]        # number of weeks of play
    n_groups = instance["n_groups"]      # number of groups playing each week
    group_size = instance["group_size"]  # number of golfers in each group
    n_golfers = n_groups * group_size    # every golfer plays once a week, so the groups hold all of them

    solver = Exact()

    # Exact identifies its variables by name.
    # assign[g][w] is the group, numbered from 0, that golfer g plays in during week w.
    assign = [[f"assign_{g}_{w}" for w in range(n_weeks)] for g in range(n_golfers)]
    # plays[g][w][k] is 1 when golfer g plays in group k in week w, and 0 otherwise.
    plays = [[[f"plays_{g}_{w}_{k}" for k in range(n_groups)] for w in range(n_weeks)]
             for g in range(n_golfers)]
    for g in range(n_golfers):
        for w in range(n_weeks):
            solver.addVariable(assign[g][w], 0, n_groups - 1)
            for name in plays[g][w]:
                solver.addVariable(name, 0, 1)

            # Each golfer plays in exactly one group every week.
            solver.addConstraint([(1, name) for name in plays[g][w]], True, 1, True, 1)

            # The group of golfer g in week w is the group that golfer plays in.
            solver.addConstraint([(k, plays[g][w][k]) for k in range(1, n_groups)] + [(-1, assign[g][w])],
                                 True, 0, True, 0)

    # Each group has exactly group_size golfers in every week.
    for w in range(n_weeks):
        for k in range(n_groups):
            solver.addConstraint([(1, plays[g][w][k]) for g in range(n_golfers)],
                                 True, group_size, True, group_size)

    # Two golfers meet when they play in the same group in the same week. Each pair of golfers
    # meets in at most one week.
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            # together is forced to 1 in each week and group where both golfers play.
            together = []
            for w in range(n_weeks):
                for k in range(n_groups):
                    name = f"together_{g1}_{g2}_{w}_{k}"
                    solver.addVariable(name, 0, 1)
                    solver.addConstraint([(1, name), (-1, plays[g1][w][k]), (-1, plays[g2][w][k])],
                                         True, -1)
                    together.append((1, name))
            solver.addConstraint(together, False, 0, True, 1)

    return solver, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
