# csplib_018_water_bucket: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """The water bucket puzzle: buckets hold at most their capacity, and a transfer pours
    water from one bucket into another until the source is empty or the destination is
    full. Find the fewest transfers that take the water from the initial levels to the
    goal levels. The sequence lists the level of every bucket at each step: sequence[0]
    is the initial state, sequence[t] the state after t transfers, and the padding
    value fills the steps after the goal."""
    capacities = instance["capacities"]  # capacities[b]: the most water bucket b holds
    initial = instance["initial_state"]  # initial[b]: the water in bucket b at the start
    goal = instance["goal_state"]        # goal[b]: the water bucket b must hold at the end
    steps = instance["MAX_STEPS"]        # the length of the sequence: states 0 .. steps-1
    padding = instance["PADDING_VALUE"]  # the value shown in the sequence after the goal
    n = len(capacities)                  # the number of buckets
    T = steps                            # the number of states in the sequence
    cap = np.array(capacities)
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j]  # a pour from i into j

    # A pour never runs from a bucket into itself, so those entries are fixed to 0.
    pair_ok = [[int(i != j) for j in range(n)] for i in range(n)]
    # A pour from i into j holds at most the capacity of j, which bounds it.
    pour_ub = [[0 if i == j else capacities[j] for j in range(n)] for i in range(n)]

    model = Model("csplib_018_water_bucket")

    # level[t, b]: the water in bucket b in state t. Once the goal is reached no water
    # moves, so the levels stay at the goal; the sequence output hides them after that.
    # The bound on each level is the capacity of its bucket, which is a fact of the puzzle.
    level = model.addMatrixVar((T, n), vtype="I", lb=0, ub=[capacities] * T, name="level")
    model.addMatrixCons(level[0] == initial)  # the puzzle starts in the initial state

    # active[t] is 1 while state t is part of the sequence, that is, the goal has not been
    # reached before step t. The initial state is always part of it.
    active = model.addMatrixVar(T, vtype="B", name="active")
    model.addCons(active[0] == 1)

    # done[t] is 1 at the one state where the goal is reached, the last state of the sequence.
    done = model.addMatrixVar(T, vtype="B", name="done")
    model.addCons(done.sum() == 1)
    model.addMatrixCons(active[1:] == active[:-1] - done[:-1])  # the sequence ends at done

    # A done state has the goal levels. An indicator takes no equality, so each bucket gets
    # one indicator for <= and one for >= the goal level.
    for t in range(T):
        for b in range(n):
            model.addConsIndicator(level[t, b] <= goal[b], binvar=done[t])
            model.addConsIndicator(level[t, b] >= goal[b], binvar=done[t])

    # Transfer t takes the water from state t to state t+1. A transfer that is in the
    # sequence pours from one bucket into another, and stops for one of two reasons:
    # empties[t, i, j] = 1: the pour from i stops because bucket i is empty;
    # fills[t, i, j] = 1: the pour from i stops because bucket j is full.
    empties = model.addMatrixVar((T - 1, n, n), vtype="B", ub=[pair_ok] * (T - 1), name="empties")
    fills = model.addMatrixVar((T - 1, n, n), vtype="B", ub=[pair_ok] * (T - 1), name="fills")
    # pour[t, i, j]: the water transfer t moves from bucket i into bucket j
    pour = model.addMatrixVar((T - 1, n, n), vtype="I", lb=0, ub=[pour_ub] * (T - 1), name="pour")

    # Each step in the sequence makes exactly one transfer, a pour that empties or fills one
    # bucket. Once the sequence has ended, no transfer happens.
    model.addMatrixCons((empties + fills).sum(axis=(1, 2)) == active[1:])
    # A pour takes no more than the source holds, and no more than the destination has room for.
    model.addMatrixCons(pour <= level[:-1, :, None])
    model.addMatrixCons(pour <= cap[None, None, :] - level[:-1, None, :])
    # A pair that is not the transfer's pour moves no water. The capacity of j in this
    # linear bound is what limits the pour; it is not a separate assumption.
    model.addMatrixCons(pour <= cap[None, None, :] * (empties + fills))
    # The stopping rules. A pour that empties bucket i moves all of i's water; a pour that
    # fills bucket j moves the room left in j, which is capacities[j] - level[t, j].
    for t in range(T - 1):
        for i, j in pairs:
            model.addConsIndicator(pour[t, i, j] >= level[t, i], binvar=empties[t, i, j])
            model.addConsIndicator(pour[t, i, j] + level[t, j] >= capacities[j], binvar=fills[t, i, j])
    # Water is conserved: each bucket gains what it receives and loses what it gives away.
    model.addMatrixCons(level[1:] == level[:-1] - pour.sum(axis=2) + pour.sum(axis=1))

    # sequence[t, b]: the level of bucket b in state t while the sequence runs, and the
    # padding value afterwards. The padding is assumed to lie below every bucket level,
    # as -1 does in the data, so the lower bound of the sequence is the padding value.
    sequence = model.addMatrixVar((T, n), vtype="I", lb=padding, ub=[capacities] * T, name="sequence")
    for t in range(T):
        for b in range(n):
            # two indicators for the equality with the level, while the sequence runs
            model.addConsIndicator(sequence[t, b] <= level[t, b], binvar=active[t])
            model.addConsIndicator(sequence[t, b] >= level[t, b], binvar=active[t])
            # the padding value once it has ended
            model.addConsIndicator(sequence[t, b] <= padding, binvar=active[t], activeone=False)

    # The cost is the number of transfers: one for each state after the initial one
    # that is part of the sequence. Fewest transfers is the objective.
    cost = active[1:].sum()
    model.setObjective(cost, "minimize")

    return model, {"cost": cost, "sequence": sequence}


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
