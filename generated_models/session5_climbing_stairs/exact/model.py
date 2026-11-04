# session5_climbing_stairs: an Exact (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from exact import Exact


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move. Find
    the number of steps taken at each move, or 0 once the top is reached."""
    n = instance["n"]    # the number of steps in the stair, which is also the number of moves
    m1 = instance["m1"]  # the fewest steps taken at one move
    m2 = instance["m2"]  # the most steps taken at one move

    # A move that takes steps takes at least one step, and at least m1 of them.
    fewest = max(m1, 1)

    solver = Exact()

    # Exact identifies its variables by name.
    # steps[i] is the number of steps taken at move i, between 0 and m2
    steps = [f"steps_{i}" for i in range(n)]
    # moves[i] is 1 when move i takes steps, and 0 when the top has been reached before it
    moves = [f"move_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(steps[i], 0, m2)
        solver.addVariable(moves[i], 0, 1)

    # The steps taken add up to the height of the stair.
    solver.addConstraint([(1, name) for name in steps], True, n, True, n)

    for i in range(n):
        # A move takes at most m2 steps, and none when it does not take steps.
        solver.addConstraint([(1, steps[i]), (-m2, moves[i])], False, 0, True, 0)
        # A move that takes steps takes at least the fewest.
        solver.addConstraint([(1, steps[i]), (-fewest, moves[i])], True, 0)

    # Once a move takes no steps, every later move takes none.
    for i in range(1, n):
        solver.addConstraint([(1, moves[i - 1]), (-1, moves[i])], True, 0)

    return solver, {"steps": steps}


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
