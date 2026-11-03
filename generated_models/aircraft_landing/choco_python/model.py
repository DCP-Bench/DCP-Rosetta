# aircraft_landing: a Choco-solver (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python aircraft_landing.py aircraft_landing.json

from pychoco.model import Model


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
    n_aircraft = len(earliest)  # number of aircraft
    horizon = max(latest)       # no aircraft lands after the latest window end

    model = Model()

    # landing_times[i] is the time at which aircraft i lands, inside its time window
    landing_times = [model.intvar(earliest[i], latest[i], name=f"landing_{i}") for i in range(n_aircraft)]
    # earliness[i] and lateness[i] are how far before and after its target aircraft i lands
    earliness = [model.intvar(0, horizon, name=f"earliness_{i}") for i in range(n_aircraft)]
    lateness = [model.intvar(0, horizon, name=f"lateness_{i}") for i in range(n_aircraft)]
    # total_penalty is the penalty summed over all aircraft, to be minimised
    total_penalty = model.intvar(0, horizon * (sum(penalty_before) + sum(penalty_after)), name="total_penalty")

    # The landing time is the target moved later by the lateness or earlier by the
    # earliness. The penalties are positive, so at the optimum one of the two is zero.
    for i in range(n_aircraft):
        model.scalar([landing_times[i], lateness[i], earliness[i]], [1, -1, 1], "=", target[i]).post()

    # Aircraft land in index order, and each later landing is at least the required
    # separation after each earlier one.
    for i in range(n_aircraft):
        for j in range(i + 1, n_aircraft):
            model.arithm(landing_times[j], "-", landing_times[i], ">=", separation[i][j]).post()

    # Each aircraft pays its penalty per unit of earliness and of lateness.
    model.scalar(earliness + lateness, penalty_before + penalty_after, "=", total_penalty).post()

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}, {"objective": total_penalty, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
