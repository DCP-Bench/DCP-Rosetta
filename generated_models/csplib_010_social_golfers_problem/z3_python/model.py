# csplib_010_social_golfers_problem: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

import z3


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in a group
    n_golfers = n_groups * group_size    # every golfer plays every week, so the groups are full

    # assign[g][w] is the group that golfer g plays in during week w.
    assign = [[z3.Int(f"assign_{g}_{w}") for w in range(n_weeks)] for g in range(n_golfers)]

    solver = z3.Solver()

    # Each golfer plays in one of the groups in every week.
    for row in assign:
        for cell in row:
            solver.add(z3.And(cell >= 0, cell <= n_groups - 1))

    # Each group has exactly group_size golfers in every week.
    for group in range(n_groups):
        for week in range(n_weeks):
            # the golfers who play in this group in this week
            members = [z3.If(assign[g][week] == group, 1, 0) for g in range(n_golfers)]
            solver.add(z3.Sum(members) == group_size)

    # Two golfers share a group in at most one week.
    for first in range(n_golfers):
        for second in range(first + 1, n_golfers):
            # the weeks in which these two golfers play in the same group
            together = [z3.If(assign[first][week] == assign[second][week], 1, 0)
                        for week in range(n_weeks)]
            solver.add(z3.Sum(together) <= 1)

    return solver, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
