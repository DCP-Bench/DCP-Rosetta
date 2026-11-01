# csplib_010_social_golfers_problem: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in a group
    n_golfers = n_groups * group_size    # the number of golfers, who fill all the groups

    model = cp_model.CpModel()

    # assign[g][w] is the group that golfer g plays in during week w
    assign = [[model.new_int_var(0, n_groups - 1, f"assign_{g}_{w}") for w in range(n_weeks)]
              for g in range(n_golfers)]
    # in_group[g][w][k] is true when golfer g plays in group k in week w
    in_group = [[[model.new_bool_var(f"in_{g}_{w}_{k}") for k in range(n_groups)]
                 for w in range(n_weeks)]
                for g in range(n_golfers)]

    # Each golfer plays in exactly one group each week, and assign gives that group.
    for g in range(n_golfers):
        for w in range(n_weeks):
            model.add_exactly_one(in_group[g][w])
            model.add(assign[g][w] == sum(k * in_group[g][w][k] for k in range(n_groups)))

    # Each group has exactly group_size golfers in every week.
    for w in range(n_weeks):
        for k in range(n_groups):
            model.add(sum(in_group[g][w][k] for g in range(n_golfers)) == group_size)

    # Two golfers share a group in at most one week.
    for g1 in range(n_golfers):
        for g2 in range(g1 + 1, n_golfers):
            # together[w] is true when golfers g1 and g2 play in the same group in week w
            together = []
            for w in range(n_weeks):
                same = model.new_bool_var(f"same_{g1}_{g2}_{w}")
                model.add(assign[g1][w] == assign[g2][w]).only_enforce_if(same)
                model.add(assign[g1][w] != assign[g2][w]).only_enforce_if(~same)
                together.append(same)
            model.add_at_most_one(together)

    return model, {"assign": assign}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
