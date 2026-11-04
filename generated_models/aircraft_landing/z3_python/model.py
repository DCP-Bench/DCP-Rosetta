# aircraft_landing: a Z3 (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python aircraft_landing.py aircraft_landing.json

import z3


def create_model(instance):
    """Aircraft land on a single runway in a fixed order. Give every aircraft a landing
    time inside its window, keep the required separation between landings, and minimise
    the penalty for landing before or after the target time."""
    earliest = instance["earliest_landing"]      # earliest[i]: start of aircraft i's landing window
    latest = instance["latest_landing"]          # latest[i]: end of aircraft i's landing window
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit aircraft i lands before its target
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit aircraft i lands after its target
    separation = instance["separation_time"]     # separation[i][j]: least time from the landing of aircraft i to a later landing of aircraft j
    n_aircraft = len(earliest)
    horizon = max(latest)  # no aircraft lands after the latest window end

    # landing_times[i] is the time at which aircraft i lands.
    landing_times = [z3.Int(f"landing_{i}") for i in range(n_aircraft)]
    # earliness[i] and lateness[i] are how far before and after its target aircraft i lands.
    earliness = [z3.Int(f"earliness_{i}") for i in range(n_aircraft)]
    lateness = [z3.Int(f"lateness_{i}") for i in range(n_aircraft)]
    # total_penalty is the penalty summed over all aircraft.
    total_penalty = z3.Int("total_penalty")

    solver = z3.Optimize()

    # Each aircraft lands inside its window, and its earliness and lateness are between 0 and the horizon.
    solver.add([
        z3.And(earliest[i] <= landing_times[i], landing_times[i] <= latest[i])
        for i in range(n_aircraft)
    ])
    solver.add([
        z3.And(0 <= earliness[i], earliness[i] <= horizon, 0 <= lateness[i], lateness[i] <= horizon)
        for i in range(n_aircraft)
    ])

    # Each landing is early by its earliness or late by its lateness, measured from its target.
    solver.add([
        landing_times[i] - target[i] == lateness[i] - earliness[i]
        for i in range(n_aircraft)
    ])

    # The aircraft land in index order, and each later landing comes at least the separation after each earlier one.
    solver.add([
        landing_times[j] - landing_times[i] >= separation[i][j]
        for i in range(n_aircraft)
        for j in range(i + 1, n_aircraft)
    ])

    # The penalty weighs each aircraft's earliness and lateness by its own rates.
    solver.add(
        total_penalty
        == z3.Sum([penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i] for i in range(n_aircraft)])
    )

    solver.minimize(total_penalty)

    return solver, {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
