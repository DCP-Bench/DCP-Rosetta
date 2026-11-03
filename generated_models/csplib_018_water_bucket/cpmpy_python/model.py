# csplib_018_water_bucket: a CPMpy model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import cpmpy as cp


def create_model(instance):
    """Three buckets hold water and the first one starts full. Pouring water from one
    bucket into another, reach the goal amounts with the fewest transfers. A pour
    stops when the source is empty or the target is full."""
    capacities = instance["capacities"]        # capacities[b]: how much bucket b can hold
    initial_state = instance["initial_state"]  # the amount of water in each bucket at the start
    goal_state = instance["goal_state"]        # the amount of water each bucket must end with
    max_steps = instance["MAX_STEPS"]          # the length of the state sequence to report
    pad = instance["PADDING_VALUE"]            # the value that fills the states after the goal is reached
    n_buckets = len(capacities)

    # Water is never created or lost, so every state holds this much in total.
    total_water = sum(initial_state)

    # All states (a, b, c) that fit in the buckets and hold the total amount of water.
    all_states = [(a, b, total_water - a - b)
                  for a in range(capacities[0] + 1)
                  for b in range(capacities[1] + 1)
                  if 0 <= total_water - a - b <= capacities[2]]

    # All legal pours, as rows (state before, state after). Pouring from bucket i into
    # bucket j moves the smaller of the water in i and the free room in j. A pour that
    # moves nothing is not a transfer, so it is left out.
    transitions = set()
    for state in all_states:
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(state[i], capacities[j] - state[j])
                if amount > 0:
                    after = list(state)
                    after[i] -= amount
                    after[j] += amount
                    transitions.add(tuple(state) + tuple(after))
    transitions = sorted(transitions)

    # sequence[t, b] is the amount of water in bucket b after t transfers. A state that
    # comes after the goal is reached consists of padding values only.
    sequence = cp.intvar(pad, total_water, shape=(max_steps, n_buckets), name="sequence")

    model = cp.Model()

    # The sequence starts in the initial state.
    model.add(sequence[0] == initial_state)

    for t in range(max_steps):
        padded = sequence[t, 0] == pad
        # A state that is not padding holds all the water and respects the capacities.
        model.add((~padded).implies(cp.sum(sequence[t]) == total_water))
        model.add((~padded).implies(cp.all((sequence[t] >= 0) & (sequence[t] <= capacities))))

    for t in range(max_steps - 1):
        padded = sequence[t, 0] == pad
        at_goal = cp.all(sequence[t] == goal_state)
        # Once the goal is reached, every later state is padding.
        model.add(at_goal.implies(cp.all(sequence[t + 1] == pad)))
        # Padding stays padding.
        model.add(padded.implies(cp.all(sequence[t + 1] == pad)))
        # Before the goal is reached, each step is one legal pour. The table holds only
        # pours that move water, so every step changes the state.
        pour = cp.Table(list(sequence[t]) + list(sequence[t + 1]), transitions)
        model.add((~at_goal & ~padded).implies(pour))

    # The goal is reached at some step.
    model.add(cp.any([cp.all(sequence[t] == goal_state) for t in range(max_steps)]))

    # cost is the number of transfers: the states that are not padding, minus the initial one.
    cost = cp.intvar(0, max_steps - 1, name="cost")
    model.add(cost == cp.sum(sequence[:, 0] != pad) - 1)

    # Use as few transfers as possible.
    model.minimize(cost)

    return model, {"cost": cost, "sequence": sequence}


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
