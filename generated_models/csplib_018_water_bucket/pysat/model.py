# csplib_018_water_bucket: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import itertools

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def create_model(instance):
    """Water is poured between buckets, each pour stopping when the source is empty or the
    target is full, until the buckets hold the goal amounts. The fewest transfers reach it."""
    capacities = instance["capacities"]        # capacities[b]: how much water bucket b holds when full
    initial_state = instance["initial_state"]  # initial_state[b]: the water in bucket b at the start
    goal_state = instance["goal_state"]        # goal_state[b]: the water bucket b must hold at the end
    max_steps = instance["MAX_STEPS"]          # the number of states in the reported sequence
    pad = instance["PADDING_VALUE"]            # the value that fills the states after the goal is reached
    n_buckets = len(capacities)

    # The water is never created or lost, so the buckets always hold this much together.
    total_water = sum(initial_state)

    # states: how much water each bucket holds, within its capacity, with all the water in the buckets.
    states = [s for s in itertools.product(*(range(c + 1) for c in capacities)) if sum(s) == total_water]
    n_states = len(states)
    index = {s: q for q, s in enumerate(states)}  # index[s]: the number of the state s

    # moves[q]: the states one pour away from state q. A pour moves the smaller of the water in
    # the source and the free room in the target, so it stops when the source is empty or the
    # target is full. A pour that moves no water is not a transfer.
    moves = {q: set() for q in range(n_states)}
    for q, state in enumerate(states):
        for a in range(n_buckets):
            for b in range(n_buckets):
                amount = min(state[a], capacities[b] - state[b])
                if a != b and amount > 0:
                    after = list(state)
                    after[a] -= amount
                    after[b] += amount
                    moves[q].add(index[tuple(after)])

    start = index[tuple(initial_state)]
    goal = index[tuple(goal_state)]

    pool = IDPool()
    formula = WCNF()

    # at[t][q] is true when the buckets hold state q after t transfers. padded[t] is true when
    # the t-th state of the sequence is padding.
    at = [[pool.id(("at", t, q)) for q in range(n_states)] for t in range(max_steps)]
    padded = [pool.id(("padded", t)) for t in range(max_steps)]

    # Each state of the sequence is exactly one state of the buckets, or padding.
    for t in range(max_steps):
        formula.extend(CardEnc.equals(lits=at[t] + [padded[t]], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # The sequence starts in the initial state.
    formula.append([at[0][start]])

    # The goal is reached at some point in the sequence.
    formula.append([at[t][goal] for t in range(max_steps)])

    for t in range(max_steps - 1):
        # After the goal is reached, and after padding, only padding follows.
        formula.append([-at[t][goal], padded[t + 1]])
        formula.append([-padded[t], padded[t + 1]])
        # Any other state is followed by one of its pours.
        for q in range(n_states):
            if q != goal:
                formula.append([-at[t][q]] + [at[t + 1][r] for r in sorted(moves[q])])

    # sequence[t][b] is the water in bucket b after t transfers, or the padding value once the
    # goal is reached. The amounts range from the padding value up to all the water.
    low, high = min(pad, 0), max(total_water, pad)
    sequence = [[Integer(f"sequence_{t}_{b}", low, high, vpool=pool) for b in range(n_buckets)]
                for t in range(max_steps)]
    for t in range(max_steps):
        for b in range(n_buckets):
            var = sequence[t][b]
            formula.extend(var.domain_clauses())
            for q, s in enumerate(states):
                formula.append([-at[t][q], var.equals(s[b])])
            formula.append([-padded[t], var.equals(pad)])

    # cost is the number of transfers: the states that are not padding, minus the initial state.
    # Padding fills every state after the goal, so the states that are not padding come first.
    cost = Integer("cost", 0, max_steps - 1, encoding="coupled", vpool=pool)
    formula.extend(cost.domain_clauses())
    for t in range(1, max_steps):
        formula.append([-cost.ge(t), -padded[t]])
        formula.append([cost.ge(t), padded[t]])

    # Minimise the transfers: each state after the initial one that is not padding is one transfer.
    for t in range(1, max_steps):
        formula.append([padded[t]], weight=1)

    return formula, {"cost": cost, "sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
