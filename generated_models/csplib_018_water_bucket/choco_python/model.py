# csplib_018_water_bucket: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import itertools

from pychoco.model import Model


def create_model(instance):
    """Three buckets hold water, and the first one starts full. Pour water from one
    bucket into another to reach the goal amounts with the fewest transfers. A pour
    stops when the source is empty or the target is full."""
    capacities = instance["capacities"]        # capacities[b]: how much bucket b can hold
    initial_state = instance["initial_state"]  # the amount of water in each bucket at the start
    goal_state = instance["goal_state"]        # the amount of water each bucket must end with
    max_steps = instance["MAX_STEPS"]          # the number of states in the sequence to report
    pad = instance["PADDING_VALUE"]            # the value that fills the states after the goal is reached
    n_buckets = len(capacities)

    # Water is never created or lost, so every state holds this much in total.
    total_water = sum(initial_state)

    # All states: the water in each bucket, within its capacity, adding up to the total.
    all_states = [s for s in itertools.product(*(range(c + 1) for c in capacities))
                  if sum(s) == total_water]
    # The number of each state, used to refer to it in the sequence.
    state_number = {s: k for k, s in enumerate(all_states)}
    pad_number = len(all_states)  # the number after the real states, for padding
    goal_number = state_number[tuple(goal_state)]

    # The allowed steps, as (state, next state) pairs of state numbers. Pouring from
    # bucket i into bucket j moves the smaller of the water in i and the free room in j,
    # and a pour must move water. The goal is followed by padding, and padding by padding.
    moves = set()
    for s in all_states:
        if state_number[s] == goal_number:
            continue
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(s[i], capacities[j] - s[j])
                if amount > 0:
                    after = list(s)
                    after[i] -= amount
                    after[j] += amount
                    moves.add((state_number[s], state_number[tuple(after)]))
    moves.add((goal_number, pad_number))
    moves.add((pad_number, pad_number))

    model = Model()

    # state[t] is the number of the state after t transfers, or the padding number once the goal is passed.
    state = [model.intvar(0, pad_number, name=f"state_{t}") for t in range(max_steps)]
    # sequence[t][b] is the water in bucket b after t transfers, or the padding value.
    sequence = [[model.intvar(min(pad, 0), max(max(capacities), pad), name=f"sequence_{t}_{b}")
                 for b in range(n_buckets)] for t in range(max_steps)]

    # contents pairs each state number with its amounts, and the padding number with the padding value.
    contents = [(k,) + s for k, s in enumerate(all_states)] + [(pad_number,) + (pad,) * n_buckets]
    # Each step of the sequence has the amounts that go with its state number.
    for t in range(max_steps):
        model.table([state[t]] + sequence[t], contents).post()

    # The sequence starts in the initial state.
    model.arithm(state[0], "=", state_number[tuple(initial_state)]).post()

    # Each step is a pour, or padding after the goal.
    for t in range(max_steps - 1):
        model.table([state[t], state[t + 1]], [list(mv) for mv in moves]).post()

    # The last state is the goal or padding, so the goal is reached within the sequence.
    model.member(state[max_steps - 1], [goal_number, pad_number]).post()

    # n_pad counts the padding states in the sequence.
    n_pad = model.intvar(0, max_steps, name="n_pad")
    model.count(pad_number, state, n_pad).post()
    # cost is the number of transfers: the states that are not padding, minus the starting one.
    cost = model.intvar(0, max_steps - 1, name="cost")
    model.arithm(cost, "+", n_pad, "=", max_steps - 1).post()

    # Use as few transfers as possible.
    return model, {"cost": cost, "sequence": sequence}, {"objective": cost, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
