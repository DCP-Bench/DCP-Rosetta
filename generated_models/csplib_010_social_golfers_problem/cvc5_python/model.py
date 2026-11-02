# csplib_010_social_golfers_problem: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

import cvc5.pythonic as c5


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion."""
    group_size = instance["group_size"]  # the number of golfers in a group
    n_groups = instance["n_groups"]      # the number of groups playing each week
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_golfers = n_groups * group_size    # every golfer plays every week, so they fill all the groups

    # in_group[i][j][g] is true when golfer i plays in group g in week j
    in_group = [[[c5.Bool(f"in_group_{i}_{j}_{g}") for g in range(n_groups)]
                 for j in range(n_weeks)]
                for i in range(n_golfers)]

    solver = c5.Solver()

    # Each golfer plays in exactly one group each week.
    for i in range(n_golfers):
        for j in range(n_weeks):
            solver.add(c5.Or([in_group[i][j][g] for g in range(n_groups)]))
            for g in range(n_groups):
                for h in range(g + 1, n_groups):
                    solver.add(c5.Or(c5.Not(in_group[i][j][g]), c5.Not(in_group[i][j][h])))

    # Each week, every group holds exactly group_size golfers.
    for j in range(n_weeks):
        for g in range(n_groups):
            solver.add(c5.Sum([c5.If(in_group[i][j][g], 1, 0) for i in range(n_golfers)]) == group_size)

    # meet[(i, k, j)] is true when golfers i and k play in the same group in week j
    meet = {}
    for i in range(n_golfers):
        for k in range(i + 1, n_golfers):
            for j in range(n_weeks):
                meet[(i, k, j)] = c5.Bool(f"meet_{i}_{k}_{j}")

    # Golfers who play in the same group in a week meet that week.
    for (i, k, j), met in meet.items():
        for g in range(n_groups):
            solver.add(c5.Or(c5.Not(in_group[i][j][g]), c5.Not(in_group[k][j][g]), met))

    # Two golfers meet in at most one week.
    for i in range(n_golfers):
        for k in range(i + 1, n_golfers):
            for j1 in range(n_weeks):
                for j2 in range(j1 + 1, n_weeks):
                    solver.add(c5.Or(c5.Not(meet[(i, k, j1)]), c5.Not(meet[(i, k, j2)])))

    # assign[i][j] is the group that golfer i plays in during week j
    assign = [[c5.Sum([c5.If(in_group[i][j][g], g, 0) for g in range(n_groups)])
               for j in range(n_weeks)]
              for i in range(n_golfers)]

    return solver, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
