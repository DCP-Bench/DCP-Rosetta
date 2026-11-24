# aircraft_landing: a CPLEX (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python aircraft_landing.py aircraft_landing.json

from docplex.mp.model import Model


def create_model(instance):
    """Aircraft landing: choose the landing time of each aircraft on a single runway so that the
    total penalty for landing before or after its target time is as small as possible. Each aircraft
    lands within its time window, and the aircraft land in index order, with a minimum separation
    time between the landings of any two aircraft."""
    earliest = instance["earliest_landing"]    # earliest landing time of each aircraft
    latest = instance["latest_landing"]        # latest landing time of each aircraft
    target = instance["target_landing"]        # target landing time of each aircraft
    penalty_after = instance["penalty_after"]  # penalty per unit of time landing after the target
    penalty_before = instance["penalty_before"]  # penalty per unit of time landing before the target
    separation = instance["separation_time"]   # separation[i][j]: least time between landings i and j

    n = len(earliest)
    horizon = max(latest + target)  # the latest time in the data: a landing deviates from its target by at most this

    model = Model("aircraft_landing")

    # landing_times[i] is the landing time of aircraft i. Its bounds are the time window of
    # aircraft i.
    landing_times = [model.integer_var(earliest[i], latest[i], name=f"landing_{i}") for i in range(n)]

    # earliness[i] and lateness[i] are how far before and after its target aircraft i lands.
    earliness = [model.integer_var(0, horizon, name=f"earliness_{i}") for i in range(n)]
    lateness = [model.integer_var(0, horizon, name=f"lateness_{i}") for i in range(n)]

    # The landing time differs from the target by lateness minus earliness.
    model.add_constraints(landing_times[i] - target[i] == lateness[i] - earliness[i] for i in range(n))

    # Aircraft land in index order: aircraft j lands at least separation[i][j] after aircraft i,
    # for every i before j.
    model.add_constraints(landing_times[j] - landing_times[i] >= separation[i][j]
                          for i in range(n) for j in range(i + 1, n))

    # Objective: the total penalty for landing before or after the target.
    total_penalty = model.sum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
                              for i in range(n))
    model.minimize(total_penalty)

    return model, {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
