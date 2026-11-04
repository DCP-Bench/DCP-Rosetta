# aircraft_landing: a PuLP (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python aircraft_landing.py aircraft_landing.json

import pulp


def create_model(instance):
    """Choose a landing time for each aircraft on one runway, in a fixed landing
    order, so that the total penalty for landing early or late is smallest. Each
    landing stays in its time window and keeps the required separation from the
    landings before it."""
    earliest = instance["earliest_landing"]      # earliest[i]: start of aircraft i's time window
    latest = instance["latest_landing"]          # latest[i]: end of aircraft i's time window
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit aircraft i lands after its target
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit aircraft i lands before its target
    separation = instance["separation_time"]     # separation[i][j]: least time between the landing of i and the later landing j
    n_aircraft = len(earliest)

    problem = pulp.LpProblem("aircraft_landing", pulp.LpMinimize)

    # landing_times[i]: time at which aircraft i lands
    landing_times = [pulp.LpVariable(f"landing_{i}", earliest[i], latest[i], cat="Integer")
                     for i in range(n_aircraft)]

    # earliness[i]: how long before its target aircraft i lands
    earliness = [pulp.LpVariable(f"earliness_{i}", 0, cat="Integer") for i in range(n_aircraft)]
    # lateness[i]: how long after its target aircraft i lands
    lateness = [pulp.LpVariable(f"lateness_{i}", 0, cat="Integer") for i in range(n_aircraft)]

    # Penalty of the schedule: early and late minutes, each weighted by its cost.
    penalty = pulp.lpSum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
                         for i in range(n_aircraft))

    # Total penalty of the schedule. Its upper limit is the largest penalty each
    # aircraft could incur anywhere in its time window.
    worst_penalty = sum(max(penalty_before[i] * max(0, target[i] - earliest[i]),
                            penalty_after[i] * max(0, latest[i] - target[i]))
                        for i in range(n_aircraft))
    total_penalty = pulp.LpVariable("total_penalty", 0, worst_penalty, cat="Integer")
    problem += total_penalty == penalty

    # Minimize the total penalty.
    problem += penalty

    # Each landing is either early or late against its target, by the earliness or
    # the lateness.
    for i in range(n_aircraft):
        problem += landing_times[i] - target[i] == lateness[i] - earliness[i]

    # Aircraft land in the given order, each at least the separation time after
    # every landing before it.
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            problem += landing_times[j] - landing_times[i] >= separation[i][j]

    return problem, {"landing_times": landing_times, "total_penalty": total_penalty}


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
