# aircraft_landing: a CPMpy model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python aircraft_landing.py aircraft_landing.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Aircraft landing on a single runway with a fixed landing order: give every
    aircraft a landing time in its time window, keep the required separation
    between landings, and minimise the penalty for landing before or after the
    target time."""
    earliest = np.array(instance["earliest_landing"])  # earliest[i]: start of aircraft i's time window
    latest = np.array(instance["latest_landing"])      # latest[i]: end of aircraft i's time window
    target = np.array(instance["target_landing"])      # target[i]: preferred landing time of aircraft i
    penalty_before = np.array(instance["penalty_before"])  # cost per time unit aircraft i lands before its target
    penalty_after = np.array(instance["penalty_after"])    # cost per time unit aircraft i lands after its target
    separation = instance["separation_time"]  # separation[i][j]: minimum time between landing i and landing j
    n = len(earliest)
    horizon = max(latest)  # no aircraft can land after the latest window end

    # landing_times[i] is the time at which aircraft i lands
    landing_times = cp.intvar(0, horizon, shape=n, name="landing_times")
    # earliness[i] and lateness[i] are how far before and after its target aircraft i lands
    earliness = cp.intvar(0, horizon, shape=n, name="earliness")
    lateness = cp.intvar(0, horizon, shape=n, name="lateness")
    # total_penalty is the summed penalty; no aircraft deviates more than the horizon
    total_penalty = cp.intvar(0, horizon * (sum(penalty_before) + sum(penalty_after)), name="total_penalty")

    model = cp.Model()

    # Every aircraft lands inside its time window.
    model.add(landing_times >= earliest)
    model.add(landing_times <= latest)

    # The deviation from the target is earliness or lateness; the positive penalties
    # make the solver keep one of the two at zero.
    model.add(landing_times - target == lateness - earliness)

    # The landing order is the aircraft index order, so aircraft j lands at least
    # separation[i][j] after aircraft i for every i < j.
    for i in range(n):
        for j in range(i + 1, n):
            model.add(landing_times[j] - landing_times[i] >= separation[i][j])

    # The total penalty weighs each aircraft's earliness and lateness by its penalties.
    model.add(total_penalty == cp.sum(earliness * penalty_before) + cp.sum(lateness * penalty_after))

    # Minimise the total penalty.
    model.minimize(total_penalty)

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
