# csplib_018_water_bucket: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import functools
import operator

from hermax.model import Model, sum_expr


def any_of(literals):
    """The disjunction of a list of literals."""
    return functools.reduce(operator.or_, literals)


def create_model(instance):
    """Water bucket (CSPLib 18): the buckets start with all the water in the largest one,
    and water is poured between buckets until the largest holds 4 pints and the middle one
    4 pints. A pour empties the source or fills the target, whichever comes first. Find the
    fewest pours, and the sequence of bucket contents, padded after the goal is reached."""
    capacities = instance["capacities"]    # capacities[b]: the most water bucket b holds
    initial = instance["initial_state"]    # initial[b]: the water in bucket b at the start
    goal = instance["goal_state"]          # goal[b]: the water wanted in bucket b at the end
    steps = instance["MAX_STEPS"]          # the length of the reported sequence of states
    pad_value = instance["PADDING_VALUE"]  # the value reported for every bucket after the goal
    buckets = len(capacities)
    total = sum(initial)                   # the water never leaves the buckets, only moves
    lowest = min(0, pad_value)             # smallest value a reported amount can take

    m = Model()

    # sequence[t][b] is the water in bucket b at step t, or the padding value after the goal
    sequence = [[m.int(f"sequence_{t}_{b}", lowest, max(capacities[b], pad_value))
                 for b in range(buckets)] for t in range(steps)]
    # pad[t] is true when step t is after the goal (padding)
    pad = m.bool_vector("pad", steps)
    # reached[t] is true when step t holds the goal amounts
    reached = m.bool_vector("reached", steps)
    # every move is a pour from one bucket to another: pours_t[k] is a pour from moves[k]
    moves = [(i, j) for i in range(buckets) for j in range(buckets) if i != j]
    pours = [m.bool_vector(f"pour_{t}", len(moves)) for t in range(steps - 1)]

    # Each step is either padding or a real state; padding stays on once it starts.
    for t in range(steps):
        # a real state has no negative amounts, and padding has the padding value
        for b in range(buckets):
            m &= (sequence[t][b] >= 0).only_if(~pad[t])
            m &= (sequence[t][b] == pad_value).only_if(pad[t])

    # The sequence starts with the initial state, and it is not padding.
    m &= (~pad[0])
    for b in range(buckets):
        m &= (sequence[0][b] == initial[b])

    # Reaching the goal is recorded: a reached step holds the goal amounts.
    for t in range(steps):
        for b in range(buckets):
            m &= (sequence[t][b] == goal[b]).only_if(reached[t])
    # The goal is reached at some step.
    m &= reached.at_least_one()

    for t in range(steps - 1):
        # Padding never stops: once padding starts it goes on to the end.
        m &= (~pad[t] | pad[t + 1])
        # Padding starts only right after the goal is reached.
        m &= (pad[t] | ~pad[t + 1] | reached[t])
        # After the goal is reached, the next step is padding.
        m &= (~reached[t] | pad[t + 1])

        # A pour happens only between two real states, and exactly one happens between them.
        for k in range(len(moves)):
            m &= (~pours[t][k] | ~pad[t])
            m &= (~pours[t][k] | ~pad[t + 1])
        m &= pours[t].at_most_one()
        m &= any_of([pad[t], pad[t + 1]] + list(pours[t]))

        for k, (i, j) in enumerate(moves):
            pour = pours[t][k]
            before = sequence[t]
            after = sequence[t + 1]
            # The pour from bucket i into bucket j keeps the water in the two buckets.
            m &= (after[i] + after[j] == before[i] + before[j]).only_if(pour)
            # The other buckets are unchanged.
            for c in range(buckets):
                if c not in (i, j):
                    m &= (after[c] == before[c]).only_if(pour)
            # The pour stops when bucket i is empty or bucket j is full.
            m &= (~pour | (after[i] == 0) | (after[j] == capacities[j]))

    # The number of transfers is the number of pours; minimise it.
    transfers = sum_expr(pours[t][k] for t in range(steps - 1) for k in range(len(moves)))
    m.obj += transfers

    return m, {"cost": transfers, "sequence": sequence}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
