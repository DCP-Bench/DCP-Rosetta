# csplib_018_water_bucket: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import itertools

import mip


def create_model(instance):
    """Three buckets hold water, and the first one starts full. Pour water from one
    bucket into another, a pour stopping when the source is empty or the target is
    full. Reach the goal amounts with the fewest transfers, and report the water in
    each bucket after every transfer, padded with the padding value after the goal."""
    caps = instance["capacities"]            # caps[b]: how much water bucket b holds
    init = tuple(instance["initial_state"])  # init[b]: the water in bucket b at the start
    goal = tuple(instance["goal_state"])     # goal[b]: the water bucket b must end with
    steps = instance["MAX_STEPS"]            # the number of rows in the reported sequence
    pad = instance["PADDING_VALUE"]          # the value that fills the rows after the goal
    n_buckets = len(caps)                    # the number of buckets

    # Water is never created or lost, so every state holds this much in total.
    total = sum(init)

    # Every state: the water in each bucket, within the capacities, adding up to the total.
    states = [s for s in itertools.product(*[range(c + 1) for c in caps]) if sum(s) == total]
    index = {s: k for k, s in enumerate(states)}  # the position of each state in states

    # Every pour that moves water, as (state before, state after). A pour goes from bucket i
    # into bucket j until i is empty or j is full.
    moves = []
    for s in states:
        for i in range(n_buckets):
            for j in range(n_buckets):
                if i == j:
                    continue
                amount = min(s[i], caps[j] - s[j])
                if amount <= 0:
                    continue
                after = list(s)
                after[i] -= amount
                after[j] += amount
                moves.append((s, tuple(after)))

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # transfer[t] is 1 when transfer t is a pour, and 0 when it is padding
    transfer = [model.add_var(f"transfer_{t}", var_type=mip.BINARY) for t in range(steps - 1)]
    # Padding stays padding: once a transfer is missing, the later ones are missing too.
    for t in range(1, steps - 1):
        model.add_constr(transfer[t] <= transfer[t - 1])

    # in_state[t][k] is 1 when the water is in state k after t transfers
    # The sequence starts in the initial state and ends in the goal state.
    fixed = {(0, index[init]), (steps - 1, index[goal])}
    in_state = [[model.add_var(f"in_state_{t}_{k}", lb=int((t, k) in fixed), var_type=mip.BINARY)
                 for k in range(len(states))] for t in range(steps)]
    # The water is in exactly one state after each number of transfers.
    for t in range(steps):
        model.add_constr(mip.xsum(in_state[t]) == 1)

    # move[t][m] is 1 when transfer t is the pour moves[m]
    move = [[model.add_var(f"move_{t}_{m}", var_type=mip.BINARY) for m in range(len(moves))]
            for t in range(steps - 1)]

    # out_moves[k] are the pours out of state k, and in_moves[k] the pours into it
    out_moves = [[] for _ in states]
    in_moves = [[] for _ in states]
    for m, (src, dst) in enumerate(moves):
        out_moves[index[src]].append(m)
        in_moves[index[dst]].append(m)

    for t in range(steps - 1):
        # A transfer is exactly one pour, and a padding transfer pours nothing.
        model.add_constr(mip.xsum(move[t]) == transfer[t])
        padding = 1 - transfer[t]  # 1 when transfer t is padding
        for k, s in enumerate(states):
            # The water is in state k before transfer t exactly when transfer t pours out of k.
            # In the goal state, a padding transfer keeps the water there.
            leaving = [move[t][m] for m in out_moves[k]]
            if s == goal:
                model.add_constr(in_state[t][k] == mip.xsum(leaving) + padding)
            else:
                model.add_constr(in_state[t][k] == mip.xsum(leaving))
            # The water is in state k after transfer t exactly when transfer t pours into k.
            # In the goal state, a padding transfer keeps the water there.
            entering = [move[t][m] for m in in_moves[k]]
            if s == goal:
                model.add_constr(in_state[t + 1][k] == mip.xsum(entering) + padding)
            else:
                model.add_constr(in_state[t + 1][k] == mip.xsum(entering))

    # Row 0 of the sequence is the initial state, fixed in the bounds of its entries. Row t
    # (t >= 1) is the water in each bucket after t transfers, or the padding value when fewer
    # than t transfers are made.
    sequence = [[model.add_var(f"bucket_0_{i}", lb=init[i], ub=init[i], var_type=mip.INTEGER)
                 for i in range(n_buckets)]]
    for t in range(1, steps):
        row = []
        at_least_t = transfer[t - 1]  # 1 when there are at least t transfers
        for i in range(n_buckets):
            # the water in bucket i after t transfers
            water = mip.xsum(s[i] * in_state[t][k] for k, s in enumerate(states) if s[i] != 0)
            # bucket i in row t of the sequence
            entry = model.add_var(f"bucket_{t}_{i}", lb=pad, ub=caps[i], var_type=mip.INTEGER)
            model.add_constr(entry - water <= (caps[i] - pad) * (1 - at_least_t))
            model.add_constr(water - entry <= (caps[i] - pad) * (1 - at_least_t))
            model.add_constr(entry <= caps[i] * at_least_t + pad * (1 - at_least_t))
            row.append(entry)
        sequence.append(row)

    # cost is the number of transfers, one for each pour
    cost = mip.xsum(move[t][m] for t in range(steps - 1) for m in range(len(moves)))
    # Use as few transfers as possible.
    model.objective = cost

    return model, {"cost": cost, "sequence": sequence}


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
