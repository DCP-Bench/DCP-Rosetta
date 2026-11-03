# csplib_018_water_bucket: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Three buckets hold water, and the first one starts full. Pour water from one
    bucket into another to reach the goal amounts with the fewest transfers. A pour
    stops when the source is empty or the target is full."""
    capacities = instance["capacities"]        # capacities[b]: how much bucket b can hold
    initial_state = instance["initial_state"]  # the amount of water in each bucket at the start
    goal_state = instance["goal_state"]        # the amount of water each bucket must end with
    n_steps = instance["MAX_STEPS"]            # the number of states in the sequence to report
    pad = instance["PADDING_VALUE"]            # the value that fills the states after the goal is reached
    n_buckets = len(capacities)

    # Water is never created or lost, so every state holds this much in total.
    total_water = sum(initial_state)

    # All states (a, b, c) that fit in the buckets and hold the total amount of water.
    states = [(a, b, total_water - a - b)
              for a in range(capacities[0] + 1)
              for b in range(capacities[1] + 1)
              if 0 <= total_water - a - b <= capacities[2]]

    # All legal pours, from one state to the next. Pouring from bucket i into bucket j
    # moves the smaller of the water in i and the free room in j.
    pourings = set()
    for state in states:
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(state[i], capacities[j] - state[j])
                if amount > 0:
                    after = list(state)
                    after[i] -= amount
                    after[j] += amount
                    pourings.add(tuple(state) + tuple(after))

    # The steps allowed in the sequence: a legal pour from a state other than the goal,
    # the goal followed by padding, or padding followed by padding.
    goal = tuple(goal_state)
    padding = (pad,) * n_buckets
    transitions = {p for p in pourings if p[:n_buckets] != goal}
    transitions.add(goal + padding)
    transitions.add(padding + padding)
    transitions = sorted(transitions)

    model = cp_model.CpModel()

    # sequence[t][b] is the amount of water in bucket b after t transfers, or the padding
    # value once the goal has been reached
    sequence = [[model.new_int_var(pad, total_water, f"sequence_{t}_{b}") for b in range(n_buckets)]
                for t in range(n_steps)]

    # The sequence starts in the initial state.
    for b in range(n_buckets):
        model.add(sequence[0][b] == initial_state[b])

    # Each step follows from the one before by an allowed step.
    for t in range(n_steps - 1):
        model.add_allowed_assignments(sequence[t] + sequence[t + 1], transitions)
    # The last state is the goal or padding, so the goal is reached within the sequence.
    model.add_allowed_assignments(sequence[n_steps - 1], [goal, padding])

    # used[t] is true when state t is a real state and not padding.
    used = []
    for t in range(n_steps):
        flag = model.new_bool_var(f"used_{t}")
        model.add(sequence[t][0] != pad).only_enforce_if(flag)
        model.add(sequence[t][0] == pad).only_enforce_if(~flag)
        used.append(flag)

    # cost is the number of transfers: the real states minus the initial one.
    cost = model.new_int_var(0, n_steps - 1, "cost")
    model.add(cost == sum(used) - 1)

    # Use as few transfers as possible.
    model.minimize(cost)

    return model, {"cost": cost, "sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
