# csplib_018_water_bucket: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

from pycsp3 import *


def create_model(instance):
    """You are given an 8 pint bucket of water, and two empty buckets which can
    contain 5 and 3 pints respectively. You are required to divide the water into
    two by pouring water between buckets (that is, to end up with 4 pints in the
    8 pint bucket, and 4 pints in the 5 pint bucket). A transfer pours water from
    one bucket into another until the first is empty or the second is full. Find
    the minimum number of transfers of water between buckets to reach the goal."""
    capacities = instance["capacities"]  # the capacity, in pints, of each bucket
    initial_state = instance["initial_state"]  # the pints in each bucket at the start
    goal_state = instance["goal_state"]  # the pints in each bucket at the goal
    max_steps = instance["MAX_STEPS"]  # the number of rows of the sequence, the first being the initial state
    padding = instance["PADDING_VALUE"]  # the value of every bucket in a row after the goal is reached
    n_buckets = len(capacities)

    def pour(state, source, target):
        # the state after pouring from bucket source into bucket target until source is empty or target is full
        amount = min(state[source], capacities[target] - state[target])
        after = list(state)
        after[source] -= amount
        after[target] += amount
        return tuple(after)

    # every state, one pint count per bucket, each within the capacity of its bucket
    states = [()]
    for capacity in capacities:
        states = [state + (pints,) for state in states for pints in range(capacity + 1)]

    # every pair of a state and the state after one transfer from one bucket to another; a transfer that moves
    # no water keeps the state, and the minimum never uses one
    transfers = [
        state + pour(state, source, target)
        for state in states
        for source in range(n_buckets)
        for target in range(n_buckets)
        if source != target
    ]

    # sequence[t][k] is the pints in bucket k after t transfers; the domain holds the padding value and every
    # pint count up to the largest capacity
    sequence = VarArray(size=[max_steps, n_buckets], dom={padding, *range(max(capacities) + 1)})

    # a row where every bucket holds the padding value
    padding_row = [padding] * n_buckets

    # the number of transfers, at most max_steps - 1 since the sequence has max_steps rows, the first being the initial state
    cost = Var(dom=range(max_steps))

    satisfy(
        # The sequence starts from the initial state.
        sequence[0][k] == initial_state[k] for k in range(n_buckets)
    )

    satisfy(
        # The goal state appears in the sequence.
        Or([And([sequence[t][k] == goal_state[k] for k in range(n_buckets)]) for t in range(max_steps)])
    )

    satisfy(
        # Each row is one transfer from the row before, or padding; padding follows the goal state only
        # and is followed only by padding.
        Table(
            scope=list(sequence[t]) + list(sequence[t + 1]),
            supports=transfers + [goal_state + padding_row, padding_row + padding_row],
        )
        for t in range(max_steps - 1)
    )

    satisfy(
        # The padding rows are the unused ones, so the transfers are the other rows minus the initial state.
        # A padding row has every bucket at the padding value, so counting the padding value in the first
        # bucket's column counts the padding rows.
        cost == max_steps - 1 - Count(sequence[:, 0], value=padding)
    )

    # The number of transfers is the objective, to be minimised.
    minimize(cost)

    return {"cost": cost, "sequence": sequence}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("cost", "=", value(outputs["cost"]))
        print("sequence", "=", values(outputs["sequence"]))
    else:
        print("No solution:", status())
