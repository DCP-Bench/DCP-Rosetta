# session5_climbing_stairs: a SCIP (Python) model from DCP Rosetta.
# Download the `session5_climbing_stairs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session5_climbing_stairs.py session5_climbing_stairs.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Climb a stair of n steps, taking between m1 and m2 steps at each move,
    so that the moves land exactly on the top. The output steps lists the steps
    taken at each of the n move slots: a move's size, or 0 once the top is reached."""
    n = instance["n"]    # the number of steps of the stair
    m1 = instance["m1"]  # the fewest steps a move may take (assumed to be at least 1)
    m2 = instance["m2"]  # the most steps a move may take

    model = Model("session5_climbing_stairs")

    # steps[t] is the number of steps taken at move t, from 0 to m2 (the bound
    # comes from the instance field m2). Since every move takes at least m1 >= 1
    # step, the climb needs at most n moves, so n slots are enough.
    steps = [model.addVar(f"steps_{t}", vtype="I", lb=0, ub=m2) for t in range(n)]

    # moving[t] is 1 when move t takes steps, and 0 when the top was reached before it
    moving = [model.addVar(f"moving_{t}", vtype="B") for t in range(n)]

    for t in range(n):
        # A move that is made takes at least m1 steps (its upper bound m2 is
        # already on steps[t]).
        model.addConsIndicator(steps[t] >= m1, binvar=moving[t])
        # A move that is not made takes no steps.
        model.addConsIndicator(steps[t] <= 0, binvar=moving[t], activeone=False)

    # Once the top is reached the climb stops: no move is made after a move that was not made.
    # The moves are the first ones of the list and the zeros come last.
    for t in range(n - 1):
        model.addCons(moving[t + 1] <= moving[t])

    # The moves together climb exactly n steps, to the top.
    model.addCons(quicksum(steps) == n)

    return model, {"steps": steps}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
