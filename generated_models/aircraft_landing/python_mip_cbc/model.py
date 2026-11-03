# aircraft_landing: a Python-MIP (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python aircraft_landing.py aircraft_landing.json

import mip


def create_model(instance):
    """Land a set of aircraft on one runway in the given order. Each aircraft lands
    inside its time window, consecutive landings keep the required separation, and
    the total penalty for landing before or after the target time is as small as
    possible."""
    earliest = instance["earliest_landing"]      # earliest[i]: the start of aircraft i's time window
    latest = instance["latest_landing"]          # latest[i]: the end of aircraft i's time window
    target = instance["target_landing"]          # target[i]: the preferred landing time of aircraft i
    penalty_before = instance["penalty_before"]  # penalty_before[i]: penalty per time unit aircraft i lands before its target
    penalty_after = instance["penalty_after"]    # penalty_after[i]: penalty per time unit aircraft i lands after its target
    separation = instance["separation_time"]     # separation[i][j]: minimum time between aircraft i and a later aircraft j
    n_aircraft = len(target)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # landing[i] is the time at which aircraft i lands, a whole number in its time window.
    landing = [
        model.add_var(f"landing_{i}", lb=earliest[i], ub=latest[i], var_type=mip.INTEGER)
        for i in range(n_aircraft)
    ]
    # early[i] is how many time units before its target aircraft i lands.
    early = [
        model.add_var(f"early_{i}", lb=0, ub=max(target[i] - earliest[i], 0), var_type=mip.INTEGER)
        for i in range(n_aircraft)
    ]
    # late[i] is how many time units after its target aircraft i lands.
    late = [
        model.add_var(f"late_{i}", lb=0, ub=max(latest[i] - target[i], 0), var_type=mip.INTEGER)
        for i in range(n_aircraft)
    ]

    # Landing before or after the target time counts as earliness or lateness.
    for i in range(n_aircraft):
        model += early[i] >= target[i] - landing[i]
        model += late[i] >= landing[i] - target[i]

    # Aircraft land in the given order, and each later aircraft lands at least the
    # separation time after each earlier one.
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            model += landing[j] >= landing[i] + separation[i][j]

    # No landing schedule can cost more than this, which bounds the total penalty.
    max_penalty = sum(
        penalty_before[i] * max(target[i] - earliest[i], 0)
        + penalty_after[i] * max(latest[i] - target[i], 0)
        for i in range(n_aircraft)
    )
    # total is the penalty summed over all aircraft.
    total = model.add_var("total_penalty", lb=0, ub=max_penalty, var_type=mip.INTEGER)
    # Each aircraft pays its penalty per time unit of earliness and of lateness.
    model += total == mip.xsum(
        penalty_before[i] * early[i] + penalty_after[i] * late[i] for i in range(n_aircraft)
    )

    # Minimise the total penalty.
    model.objective = total

    return model, {"landing_times": landing, "total_penalty": total}


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
