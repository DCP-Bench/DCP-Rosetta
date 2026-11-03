# wolf_goat_cabbage: a Python-MIP (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

import mip
from itertools import product


# A position of the wolf, the goat, the cabbage and the boat on the two shores.
def safe(state):
    # The wolf and the goat, or the goat and the cabbage, can share a shore only
    # when the farmer is on that shore too.
    w, g, c, b = state
    if w == g and b != g:
        return False
    if g == c and b != g:
        return False
    return True


# The positions one crossing of the boat can lead to. The farmer rows to the other
# shore, alone or with one item from his shore, and that item comes along.
def successors(state):
    b = state[3]
    result = []
    for mover in (None, 0, 1, 2):
        nxt = list(state)
        nxt[3] = 1 - b
        if mover is not None:
            if state[mover] != b:
                continue
            nxt[mover] = 1 - state[mover]
        nxt = tuple(nxt)
        if safe(nxt):
            result.append(nxt)
    return result


# The name of a position, for naming its variables.
def label(state):
    return "".join(str(v) for v in state)


def create_model(instance):
    """A farmer with a wolf, a goat and a cabbage must cross a river by boat. The
    boat carries only the farmer and a single item, and if left unattended
    together the wolf eats the goat and the goat eats the cabbage. Find a
    crossing in which nothing is eaten."""
    n_stages = instance["stage"]  # the number of stages in the plan, from the starting shore to the destination shore
    model = mip.Model(solver_name="CBC")

    # Every position in which nothing gets eaten.
    states = [s for s in product((0, 1), repeat=4) if safe(s)]
    # Everything on the starting shore.
    start = (0, 0, 0, 0)
    # Everything on the destination shore.
    goal = (1, 1, 1, 1)

    # The positions each position can lead to in one crossing.
    succ = {s: successors(s) for s in states}
    # The positions each position can be reached from in one crossing.
    pred = {s: [] for s in states}
    for s in states:
        for s2 in succ[s]:
            pred[s2].append(s)

    # x[t, s] is true when the farmer is in position s at stage t. The first stage is
    # the starting position and the last stage is the destination position.
    x = {}
    for t in range(n_stages):
        for s in states:
            fixed = (t == 0 and s == start) or (t == n_stages - 1 and s == goal)
            x[t, s] = model.add_var(f"x_{t}_{label(s)}", var_type=mip.BINARY, lb=int(fixed))

    # y[t, s, s2] is true when the farmer goes from position s at stage t to position s2
    # at stage t + 1.
    y = {}
    for t in range(n_stages - 1):
        for s in states:
            for s2 in succ[s]:
                y[t, s, s2] = model.add_var(f"y_{t}_{label(s)}_{label(s2)}", var_type=mip.BINARY)

    # At every stage the farmer is in exactly one position.
    for t in range(n_stages):
        model.add_constr(mip.xsum(x[t, s] for s in states) == 1)

    # From each position the farmer goes on by exactly one crossing, and each position is
    # reached by exactly one crossing.
    for t in range(n_stages - 1):
        for s in states:
            model.add_constr(mip.xsum(y[t, s, s2] for s2 in succ[s]) == x[t, s])
        for s2 in states:
            model.add_constr(mip.xsum(y[t, s, s2] for s in pred[s2]) == x[t + 1, s2])

    # wolf[t], goat[t], cabbage[t] and boat[t] are true when that thing is on the
    # destination shore at stage t.
    wolf = [model.add_var(f"wolf_{t}", var_type=mip.BINARY) for t in range(n_stages)]
    goat = [model.add_var(f"goat_{t}", var_type=mip.BINARY) for t in range(n_stages)]
    cabbage = [model.add_var(f"cabbage_{t}", var_type=mip.BINARY) for t in range(n_stages)]
    boat = [model.add_var(f"boat_{t}", var_type=mip.BINARY) for t in range(n_stages)]
    # Each of them is on the destination shore at a stage exactly when the position at that
    # stage has it there.
    for t in range(n_stages):
        model.add_constr(wolf[t] == mip.xsum(x[t, s] for s in states if s[0] == 1))
        model.add_constr(goat[t] == mip.xsum(x[t, s] for s in states if s[1] == 1))
        model.add_constr(cabbage[t] == mip.xsum(x[t, s] for s in states if s[2] == 1))
        model.add_constr(boat[t] == mip.xsum(x[t, s] for s in states if s[3] == 1))

    outputs = {
        "wolf_pos": wolf,
        "goat_pos": goat,
        "cabbage_pos": cabbage,
        "boat_pos": boat,
    }
    return model, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
