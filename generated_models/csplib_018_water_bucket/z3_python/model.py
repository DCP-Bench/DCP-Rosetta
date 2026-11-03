# csplib_018_water_bucket: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import z3


def create_model(instance):
    """Three buckets with fixed capacities start with some water in them. Pour water from one
    bucket into another, each pour stopping when the source is empty or the target is full, until
    the buckets hold the goal amounts. Use as few pours as possible."""
    capacities = instance["capacities"]        # capacities[b]: how much water bucket b holds when full
    initial_state = instance["initial_state"]  # the amount of water in each bucket at the start
    goal_state = instance["goal_state"]        # the amount of water each bucket must end with
    n_steps = instance["MAX_STEPS"]            # the number of states in the reported sequence
    pad = instance["PADDING_VALUE"]            # the value that fills the states after the goal is reached
    n_buckets = len(capacities)

    # Water is only moved between buckets, so the total stays the same.
    total_water = sum(initial_state)

    # Every way to share the total water among the buckets that respects their capacities.
    states = [(a, b, total_water - a - b)
              for a in range(capacities[0] + 1)
              for b in range(capacities[1] + 1)
              if 0 <= total_water - a - b <= capacities[2]]

    # Every pour from one state to another. Water moves from the source bucket into the target
    # bucket until the source is empty or the target is full.
    pourings = set()
    for state in states:
        for src in range(n_buckets):
            for dst in range(n_buckets):
                if src == dst:
                    continue
                amount = min(state[src], capacities[dst] - state[dst])
                if amount > 0:
                    after = list(state)
                    after[src] -= amount
                    after[dst] += amount
                    pourings.add(tuple(state) + tuple(after))

    # The allowed steps between consecutive states: a pour from any state other than the goal,
    # the goal followed by padding, and padding followed by padding.
    goal = tuple(goal_state)
    padding = (pad,) * n_buckets
    transitions = sorted({p for p in pourings if p[:n_buckets] != goal} | {goal + padding, padding + padding})

    # sequence[t][b] is the amount of water in bucket b after t pours, or the padding value
    # once the goal has been reached.
    sequence = [[z3.Int(f"sequence_{t}_{b}") for b in range(n_buckets)] for t in range(n_steps)]

    solver = z3.Optimize()

    # Each entry lies between the padding value and the total water.
    for t in range(n_steps):
        for b in range(n_buckets):
            solver.add(z3.And(sequence[t][b] >= pad, sequence[t][b] <= total_water))

    # The sequence starts in the initial state.
    for b in range(n_buckets):
        solver.add(sequence[0][b] == initial_state[b])

    # Each state follows from the one before by an allowed step.
    for t in range(n_steps - 1):
        cells = sequence[t] + sequence[t + 1]
        solver.add(z3.Or([z3.And([cell == value for cell, value in zip(cells, row)])
                          for row in transitions]))

    # The sequence ends at the goal or in padding, so the goal is reached within it.
    last = sequence[n_steps - 1]
    solver.add(z3.Or([z3.And([cell == value for cell, value in zip(last, row)])
                      for row in (goal, padding)]))

    # The number of pours is the number of states that are not padding, minus the initial state.
    cost = z3.Int("cost")
    solver.add(cost == z3.Sum([z3.If(sequence[t][0] != pad, 1, 0) for t in range(n_steps)]) - 1)

    solver.minimize(cost)

    return solver, {"cost": cost, "sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
