# csplib_010_social_golfers_problem: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

from pychoco.model import Model


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in a group
    n_golfers = n_groups * group_size    # every golfer plays every week, so the golfers fill all the groups

    model = Model()

    # assign[g][w] is the group that golfer g plays in during week w
    assign = [[model.intvar(0, n_groups - 1, name=f"assign_{g}_{w}") for w in range(n_weeks)]
              for g in range(n_golfers)]

    # Each group has exactly group_size golfers in every week.
    for w in range(n_weeks):
        model.global_cardinality([assign[g][w] for g in range(n_golfers)], list(range(n_groups)),
                                 [model.intvar(group_size, group_size) for _ in range(n_groups)]).post()

    # No two golfers share a group in more than one week. For each two weeks w1 and w2, the
    # golfers who share a group in both are exactly those with the same pair of groups, so
    # these pairs must all be different.
    for w1 in range(n_weeks):
        for w2 in range(w1 + 1, n_weeks):
            # pair_ids[g] is the pair of groups of golfer g in weeks w1 and w2, written as one number
            pair_ids = []
            for g in range(n_golfers):
                pair_id = model.intvar(0, n_groups * n_groups - 1, name=f"pair_{g}_{w1}_{w2}")
                model.scalar([assign[g][w1], assign[g][w2]], [n_groups, 1], "=", pair_id).post()
                pair_ids.append(pair_id)
            model.all_different(pair_ids).post()

    return model, {"assign": assign}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
