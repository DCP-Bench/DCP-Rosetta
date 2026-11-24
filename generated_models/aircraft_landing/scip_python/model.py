# aircraft_landing: a SCIP (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python aircraft_landing.py aircraft_landing.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Aircraft landing on one runway, in a fixed landing order.

    Each aircraft must land inside its own time window. The aircraft land in
    the order given by the instance (aircraft 0 first, aircraft n-1 last), and
    any two aircraft need a minimum separation time between their landings.
    Landing earlier than the target time costs a penalty per minute, and
    landing later than the target time costs another. Choose the landing
    time of every aircraft so that the total penalty is as small as possible.
    """
    n = len(instance["earliest_landing"])  # the number of aircraft
    earliest = instance["earliest_landing"]  # earliest[i]: the first minute aircraft i may land
    latest = instance["latest_landing"]  # latest[i]: the last minute aircraft i may land
    target = instance["target_landing"]  # target[i]: the minute aircraft i would like to land
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per minute aircraft i lands before its target
    penalty_after = instance["penalty_after"]  # penalty_after[i]: cost per minute aircraft i lands after its target
    separation = instance["separation_time"]  # separation[i][j]: minutes that must pass between landing i and landing j (i before j)

    model = Model("aircraft_landing")

    # land[i] is the minute aircraft i lands. Its window [earliest, latest]
    # is the bound on the variable, taken from the instance.
    land = [
        model.addVar(f"land_{i}", vtype="I", lb=earliest[i], ub=latest[i])
        for i in range(n)
    ]

    # early[i] is how many minutes before its target aircraft i lands. The
    # constraint below and the minimisation fix its value (see there). Its
    # upper bound is target minus earliest, since the aircraft cannot land
    # before its window opens; the max(0, ...) clamp only matters when the
    # target lies outside the window, which no instance does.
    early = [
        model.addVar(f"early_{i}", vtype="I", lb=0, ub=max(0, target[i] - earliest[i]))
        for i in range(n)
    ]

    # late[i] is how many minutes after its target aircraft i lands. The
    # constraint below and the minimisation fix its value (see there). Its
    # upper bound is latest minus target, since the aircraft cannot land after
    # its window closes; the max(0, ...) clamp only matters when the target
    # lies outside the window, which no instance does.
    late = [
        model.addVar(f"late_{i}", vtype="I", lb=0, ub=max(0, latest[i] - target[i]))
        for i in range(n)
    ]

    # The total penalty, held in its own bounded integer variable. Its upper bound is
    # the largest penalty each aircraft could cost within its window, summed over the
    # aircraft; the max(0, ...) clamps matter only when a target lies outside its window.
    max_penalty = sum(
        penalty_before[i] * max(0, target[i] - earliest[i])
        + penalty_after[i] * max(0, latest[i] - target[i])
        for i in range(n)
    )
    total_penalty = model.addVar("total_penalty", vtype="I", lb=0, ub=max_penalty)

    # Early minutes: early[i] >= target[i] - land[i] (and early[i] >= 0 from its
    # bound). Minimising the penalty, with a positive rate per minute, pulls
    # early[i] down to exactly max(0, target[i] - land[i]).
    for i in range(n):
        model.addCons(early[i] >= target[i] - land[i])

    # Late minutes: late[i] >= land[i] - target[i] (and late[i] >= 0 from its
    # bound). Minimising the penalty, with a positive rate per minute, pulls
    # late[i] down to exactly max(0, land[i] - target[i]).
    for i in range(n):
        model.addCons(late[i] >= land[i] - target[i])

    # Separation: aircraft j comes after aircraft i in the fixed order, so it
    # lands at least separation[i][j] minutes after aircraft i, for every pair
    # i < j. This is the minimum separation between any two landings.
    for i in range(n):
        for j in range(i + 1, n):
            model.addCons(land[j] - land[i] >= separation[i][j])

    # The total penalty is the sum over aircraft of penalty_before per minute
    # early plus penalty_after per minute late.
    model.addCons(
        total_penalty == quicksum(
            penalty_before[i] * early[i] + penalty_after[i] * late[i] for i in range(n)
        )
    )

    # Minimise the total penalty.
    model.setObjective(total_penalty, "minimize")

    return model, {"landing_times": land, "total_penalty": total_penalty}

if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
