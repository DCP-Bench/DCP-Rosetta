# aircraft_landing: an Exact (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python aircraft_landing.py aircraft_landing.json

from exact import Exact


def create_model(instance):
    """Aircraft land on a single runway in a fixed order. Give every aircraft a landing
    time inside its window, keep the required separation between consecutive landings,
    and minimise the penalty for landing before or after the target time."""
    earliest = instance["earliest_landing"]      # earliest[i]: start of the landing window of aircraft i
    latest = instance["latest_landing"]          # latest[i]: end of the landing window of aircraft i
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit aircraft i lands before its target
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit aircraft i lands after its target
    separation = instance["separation_time"]     # separation[i][j]: least time between aircraft i landing and aircraft j landing, with i first
    n_aircraft = len(earliest)  # the number of aircraft
    horizon = max(latest)       # no aircraft lands after the latest window end

    solver = Exact()

    # Exact identifies its variables by name.
    # landing_times[i] is the time aircraft i lands. earliness[i] and lateness[i] are how far
    # before and after its target aircraft i lands.
    landing_times = [f"landing_{i}" for i in range(n_aircraft)]
    earliness = [f"earliness_{i}" for i in range(n_aircraft)]
    lateness = [f"lateness_{i}" for i in range(n_aircraft)]
    for i in range(n_aircraft):
        solver.addVariable(landing_times[i], earliest[i], latest[i])
        solver.addVariable(earliness[i], 0, horizon)
        solver.addVariable(lateness[i], 0, horizon)

    # Each landing time is the target plus the lateness, minus the earliness.
    for i in range(n_aircraft):
        solver.addConstraint([(1, landing_times[i]), (-1, lateness[i]), (1, earliness[i])],
                             True, target[i], True, target[i])

    # The aircraft land in index order: each aircraft lands at least the required
    # separation after every aircraft before it.
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            solver.addConstraint([(1, landing_times[j]), (-1, landing_times[i])], True, separation[i][j])

    # The penalty of each aircraft: its earliness and its lateness, each times its penalty.
    penalty_terms = ([(penalty_before[i], earliness[i]) for i in range(n_aircraft)]
                     + [(penalty_after[i], lateness[i]) for i in range(n_aircraft)])
    # total_penalty is the sum of all penalties.
    total_penalty = "total_penalty"
    solver.addVariable(total_penalty, 0, horizon * (sum(penalty_before) + sum(penalty_after)))
    solver.addConstraint(penalty_terms + [(-1, total_penalty)], True, 0, True, 0)

    # Minimise the total penalty.
    solver.setObjective(penalty_terms, minimize=True)

    return solver, {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
