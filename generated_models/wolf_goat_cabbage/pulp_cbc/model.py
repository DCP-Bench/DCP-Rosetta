# wolf_goat_cabbage: a PuLP (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

import pulp


def create_model(instance):
    """A farmer with a wolf, a goat and a cabbage must cross a river by boat. The
    boat carries only the farmer and at most one of the others. Left alone together,
    the wolf eats the goat and the goat eats the cabbage. Find a sequence of stages
    that brings everything to the other shore without anything being eaten."""
    n_stages = instance["stage"]  # the number of stages, the first and the last included
    stages = range(n_stages)

    problem = pulp.LpProblem("wolf_goat_cabbage", pulp.LpMinimize)

    # wolf_pos[s], goat_pos[s] and cabbage_pos[s] are 0 when that item is on the starting
    # shore at stage s, and 1 when it is on the destination shore.
    wolf_pos = [pulp.LpVariable(f"wolf_{s}", cat="Binary") for s in stages]
    goat_pos = [pulp.LpVariable(f"goat_{s}", cat="Binary") for s in stages]
    cabbage_pos = [pulp.LpVariable(f"cabbage_{s}", cat="Binary") for s in stages]
    # boat_pos[s] is the shore of the boat at stage s, which is also the farmer's shore.
    boat_pos = [pulp.LpVariable(f"boat_{s}", cat="Binary") for s in stages]

    # Everything starts on the starting shore and ends on the destination shore.
    for pos in (boat_pos, wolf_pos, goat_pos, cabbage_pos):
        pos[0].bounds(0, 0)
        pos[-1].bounds(1, 1)

    # The boat crosses the river at every stage.
    for s in stages[1:]:
        problem += boat_pos[s] + boat_pos[s - 1] == 1

    # The wolf and the goat are never left alone: if both are on a shore, the boat is on it too.
    for s in stages:
        problem += wolf_pos[s] + goat_pos[s] - boat_pos[s] >= 0
        problem += wolf_pos[s] + goat_pos[s] - boat_pos[s] <= 1

    # The goat and the cabbage are never left alone: if both are on a shore, the boat is on it too.
    for s in stages:
        problem += goat_pos[s] + cabbage_pos[s] - boat_pos[s] >= 0
        problem += goat_pos[s] + cabbage_pos[s] - boat_pos[s] <= 1

    # At most one item changes shore at each crossing, since the boat carries only one.
    for s in stages[:-1]:
        # moved[k] is at least 1 when item k changes shore between stage s and stage s + 1.
        moved = []
        for name, pos in (("wolf", wolf_pos), ("goat", goat_pos), ("cabbage", cabbage_pos)):
            change = pulp.LpVariable(f"moved_{name}_{s}", 0, 1)
            problem += change >= pos[s] - pos[s + 1]
            problem += change >= pos[s + 1] - pos[s]
            moved.append(change)
        problem += pulp.lpSum(moved) <= 1

    return problem, {"wolf_pos": wolf_pos, "goat_pos": goat_pos,
                     "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}


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
