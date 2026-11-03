# csplib_018_water_bucket: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import pulp


def create_model(instance):
    """Three buckets hold water, and the first one starts full. Pour water from one
    bucket into another to reach the goal amounts with the fewest transfers. A pour
    stops when the source is empty or the target is full."""
    capacities = instance["capacities"]                 # capacities[b]: how much bucket b can hold
    initial_state = tuple(instance["initial_state"])    # the amount of water in each bucket at the start
    goal_state = tuple(instance["goal_state"])          # the amount of water each bucket must end with
    n_steps = instance["MAX_STEPS"]                     # the number of states in the sequence to report
    pad = instance["PADDING_VALUE"]                     # the value that fills the states after the goal is reached
    n_buckets = len(capacities)

    # Water is never created or lost, so every state holds this much in total.
    total_water = sum(initial_state)

    # All states (a, b, c) that fit in the buckets and hold all the water.
    states = [(a, b, total_water - a - b)
              for a in range(capacities[0] + 1)
              for b in range(capacities[1] + 1)
              if 0 <= total_water - a - b <= capacities[2]]

    # All pours from one state to the next. A pour from bucket i into bucket j moves the
    # smaller of the water in i and the free room in j. A pour that moves no water is left out.
    pours = set()
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
                    pours.add((state, tuple(after)))
    pours = sorted(pours)

    problem = pulp.LpProblem("water_bucket", pulp.LpMinimize)

    # at[t][state] is 1 when row t of the sequence is that state. A row with no state is padding.
    at = [{st: pulp.LpVariable("at_%d_%s" % (t, "_".join(map(str, st))), cat="Binary")
           for st in states}
          for t in range(n_steps)]

    # pour[t][(s, s2)] is 1 when the transfer after row t turns state s into state s2.
    pour = [{arc: pulp.LpVariable("pour_%d_%s_to_%s" % (t, "_".join(map(str, arc[0])),
                                                       "_".join(map(str, arc[1]))),
                                  cat="Binary")
             for arc in pours}
            for t in range(n_steps - 1)]

    # Each row holds at most one state.
    for t in range(n_steps):
        problem += pulp.lpSum(at[t].values()) <= 1

    # The sequence starts in the initial state.
    problem += at[0][initial_state] == 1

    # Once the goal is reached, no transfer follows. Any other state is followed by one transfer.
    for t in range(n_steps - 1):
        for st in states:
            leaving = pulp.lpSum(var for (s, _), var in pour[t].items() if s == st)
            if st == goal_state:
                problem += leaving == 0
            else:
                problem += leaving == at[t][st]

    # A state appears in the next row only when a transfer leads to it, so padding stays padding.
    for t in range(n_steps - 1):
        for st in states:
            entering = pulp.lpSum(var for (_, s2), var in pour[t].items() if s2 == st)
            problem += at[t + 1][st] == entering

    # The goal appears in the sequence at least once.
    problem += pulp.lpSum(at[t][goal_state] for t in range(n_steps) if goal_state in at[t]) >= 1

    # The cost is the number of transfers: the rows that hold a state, minus the initial one.
    cost = pulp.LpVariable("cost", 0, n_steps - 1, cat="Integer")
    problem += cost == pulp.lpSum(var for t in range(n_steps) for var in at[t].values()) - 1

    # Use as few transfers as possible.
    problem += cost

    # Row t holds the amounts of the state in that row, or the padding value in every bucket when there is none.
    sequence = [[pulp.lpSum(st[b] * var for st, var in at[t].items())
                 + pad * (1 - pulp.lpSum(at[t].values()))
                 for b in range(n_buckets)]
                for t in range(n_steps)]

    return problem, {"cost": cost, "sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
