# csplib_018_water_bucket: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

from exact import Exact


def create_model(instance):
    """Three buckets hold water, and the first one starts full. Pour water from one
    bucket into another to reach the goal amounts with the fewest transfers. A pour
    stops when the source is empty or the target is full."""
    capacities = instance["capacities"]        # capacities[b]: how much bucket b can hold
    initial_state = instance["initial_state"]  # the amount of water in each bucket at the start
    goal_state = instance["goal_state"]        # the amount of water each bucket must end with
    n_steps = instance["MAX_STEPS"]            # the number of states in the sequence to report
    padding = instance["PADDING_VALUE"]        # the value that fills the states after the goal is reached
    n_buckets = len(capacities)

    # Water is never created or lost, so every state holds this much in total.
    total_water = sum(initial_state)

    # All states (a, b, c) that fit in the buckets and hold the total amount of water.
    states = [(a, b, total_water - a - b)
              for a in range(capacities[0] + 1)
              for b in range(capacities[1] + 1)
              if 0 <= total_water - a - b <= capacities[2]]

    # successors[s] is the set of states one transfer away from s. Pouring from bucket i
    # into bucket j moves the smaller of the water in i and the free room in j. A pour
    # that moves no water is not a transfer, so it is left out.
    successors = {s: set() for s in states}
    for s in states:
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(s[i], capacities[j] - s[j])
                if amount > 0:
                    after = list(s)
                    after[i] -= amount
                    after[j] += amount
                    successors[s].add(tuple(after))

    solver = Exact()

    # Exact identifies its variables by name.
    # at[t][s] is 1 when the state after t transfers is s. at[t]["pad"] is 1 when
    # step t is padding. Exactly one of these holds at every step.
    options = states + ["pad"]
    at = [{s: f"at_{t}_{'_'.join(map(str, s)) if s != 'pad' else 'pad'}" for s in options}
          for t in range(n_steps)]
    for t in range(n_steps):
        for s in options:
            solver.addVariable(at[t][s], 0, 1)
        solver.addConstraint([(1, at[t][s]) for s in options], True, 1, True, 1)

    # sequence[t][b] is the water in bucket b after t transfers, or the padding value at
    # a padded step.
    sequence = [[f"sequence_{t}_{b}" for b in range(n_buckets)] for t in range(n_steps)]
    for t in range(n_steps):
        for b in range(n_buckets):
            solver.addVariable(sequence[t][b], padding, max(capacities[b], padding))
            solver.addConstraint([(s[b], at[t][s]) for s in states] +
                                 [(padding, at[t]["pad"]), (-1, sequence[t][b])],
                                 True, 0, True, 0)

    # The sequence starts in the initial state.
    solver.addConstraint([(1, at[0][tuple(initial_state)])], True, 1, True, 1)

    goal = tuple(goal_state)
    for t in range(n_steps - 1):
        # Once the goal is reached, the next step is padding.
        solver.addConstraint([(1, at[t + 1]["pad"]), (-1, at[t][goal])], True, 0)
        # Padding is followed by padding.
        solver.addConstraint([(1, at[t + 1]["pad"]), (-1, at[t]["pad"])], True, 0)
        # Any other state is followed by one of the states one transfer away from it.
        for s in states:
            if s != goal:
                solver.addConstraint([(1, at[t + 1][u]) for u in successors[s]] + [(-1, at[t][s])],
                                     True, 0)

    # The goal is reached at some step.
    solver.addConstraint([(1, at[t][goal]) for t in range(n_steps)], True, 1)

    # The steps that are not padding are the initial state and one state per transfer,
    # so the number of transfers is their count minus one.
    solver.addVariable("cost", 0, n_steps - 1)
    solver.addConstraint([(1, "cost")] + [(1, at[t]["pad"]) for t in range(n_steps)],
                         True, n_steps - 1, True, n_steps - 1)

    # Use as few transfers as possible.
    solver.setObjective([(1, "cost")], minimize=True)

    return solver, {"cost": "cost", "sequence": sequence}


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
