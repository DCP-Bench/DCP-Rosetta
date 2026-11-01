# aircraft_landing: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install ortools`):
#   python aircraft_landing.py aircraft_landing.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Aircraft landing on a single runway with a fixed landing order: give every
    aircraft a landing time in its time window, keep the required separation
    between landings, and minimise the penalty for landing before or after the
    target time."""
    earliest = instance["earliest_landing"]      # earliest[i]: start of aircraft i's time window
    latest = instance["latest_landing"]          # latest[i]: end of aircraft i's time window
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit aircraft i lands before its target
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit aircraft i lands after its target
    separation = instance["separation_time"]     # separation[i][j]: minimum time between landing i and landing j
    n_aircraft = len(earliest)                   # the number of aircraft
    horizon = max(latest)  # no aircraft lands after the latest window end

    model = cp_model.CpModel()

    # landing_times[i] is the time at which aircraft i lands, inside its time window
    landing_times = [
        model.new_int_var(earliest[i], latest[i], f"landing_{i}") for i in range(n_aircraft)
    ]
    # earliness[i] and lateness[i] are how far before and after its target aircraft i lands
    earliness = [model.new_int_var(0, horizon, f"earliness_{i}") for i in range(n_aircraft)]
    lateness = [model.new_int_var(0, horizon, f"lateness_{i}") for i in range(n_aircraft)]
    # total_penalty is the penalty summed over all aircraft
    total_penalty = model.new_int_var(
        0, horizon * (sum(penalty_before) + sum(penalty_after)), "total_penalty"
    )

    # The landing time differs from the target by the lateness or the earliness. The
    # penalties are positive, so at the minimum one of the two is zero.
    for i in range(n_aircraft):
        model.add(landing_times[i] - target[i] == lateness[i] - earliness[i])

    # Aircraft land in index order, and each later landing is at least the required
    # separation after each earlier one.
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            model.add(landing_times[j] - landing_times[i] >= separation[i][j])

    # Each aircraft pays its penalty for every unit of earliness and lateness.
    model.add(
        total_penalty
        == sum(
            penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
            for i in range(n_aircraft)
        )
    )
    # Minimise the total penalty.
    model.minimize(total_penalty)

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
