# session5_climbing_stairs: a PyCSP3 model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from pycsp3 import *


def create_model(instance):
    """We climb a stair of n steps, taking between m1 and m2 steps at a time. Find the number
    of steps taken at each move, where each move is between m1 and m2 steps, or 0 once the
    top of the stair is reached."""
    n_stairs = instance["n"]  # the number of steps of the stair
    min_move = instance["m1"]  # the fewest steps taken at a time
    max_move = instance["m2"]  # the most steps taken at a time
    n_moves = n_stairs  # each move takes at least one step, so n_stairs moves are enough (taken as the bound on moves)

    # steps[k] is the number of steps taken at move k: between min_move and max_move, or 0 when
    # no step is taken, which is after the top is reached
    steps = VarArray(size=n_moves, dom={0, *range(min_move, max_move + 1)})

    satisfy(
        # The moves take the climber up exactly the n_stairs steps of the stair.
        Sum(steps) == n_stairs,
        # Once the top is reached, every later move is 0: a move of 0 is followed only by moves of 0.
        [imply(steps[k] == 0, steps[k + 1] == 0) for k in range(n_moves - 1)],
    )

    return {"steps": steps}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
