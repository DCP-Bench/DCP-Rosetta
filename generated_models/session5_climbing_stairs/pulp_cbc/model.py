# session5_climbing_stairs: a PuLP (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

import pulp


def create_model(instance):
    """A stair of n steps is climbed in moves, each move taking between m1 and m2
    steps. Find the number of steps taken at each move, with 0 for the moves
    after the top is reached."""
    n = instance["n"]        # the number of steps in the stair
    least = instance["m1"]   # the fewest steps taken in one move
    most = instance["m2"]    # the most steps taken in one move
    moves = range(n)         # at most n moves, since each move climbs at least one step

    # steps[i] is the number of steps taken at move i
    steps = [pulp.LpVariable(f"step_{i}", 0, most, cat="Integer") for i in moves]
    # taken[i] is 1 when move i climbs some steps, and 0 when it takes none
    taken = [pulp.LpVariable(f"taken_{i}", cat="Binary") for i in moves]

    # The moves add up to the whole stair.
    problem = pulp.LpProblem("climbing_stairs", pulp.LpMinimize)
    problem += pulp.lpSum(steps) == n

    # A move takes between m1 and m2 steps, or none at all.
    for i in moves:
        problem += steps[i] >= least * taken[i]
        problem += steps[i] <= most * taken[i]

    # Once a move takes no steps, every later move takes none too.
    for i in range(1, n):
        problem += taken[i] <= taken[i - 1]

    return problem, {"steps": steps}


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
