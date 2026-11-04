# session5_climbing_stairs: a CPMpy model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

import cpmpy as cp


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move.
    Find the number of steps taken at each move, or 0 once the top is reached."""
    n = instance["n"]        # the number of steps in the stair
    least = instance["m1"]   # the fewest steps taken at a move
    most = instance["m2"]    # the most steps taken at a move

    # steps[i] is the number of steps taken at move i, 0 if no step is taken
    # (there are at most n moves, since each move climbs at least one step)
    steps = cp.intvar(0, most, shape=n, name="steps")

    model = cp.Model()
    # The moves add up to the whole stair.
    model.add(cp.sum(steps) == n)
    # A move takes between m1 and m2 steps, or none at all.
    model.add((steps >= least) | (steps == 0))
    # Once a move is empty, every later move is empty too.
    for i in range(1, n):
        model.add((steps[i - 1] == 0).implies(steps[i] == 0))

    return model, {"steps": steps}


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
