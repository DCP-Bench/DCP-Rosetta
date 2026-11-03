# aircraft_landing: a hermax (Python) model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install hermax`):
#   python aircraft_landing.py aircraft_landing.json

from hermax.model import Model, sum_expr


def create_model(instance):
    """Land each aircraft inside its time window, keeping the required separation after
    every earlier aircraft, so that the total penalty for landing before or after each
    aircraft's target time is as small as possible."""
    earliest = instance["earliest_landing"]      # earliest[i]: first time aircraft i may land
    latest = instance["latest_landing"]          # latest[i]: last time aircraft i may land
    target = instance["target_landing"]          # target[i]: preferred landing time of aircraft i
    penalty_before = instance["penalty_before"]  # penalty_before[i]: cost per time unit early
    penalty_after = instance["penalty_after"]    # penalty_after[i]: cost per time unit late
    separation = instance["separation_time"]     # separation[i][j]: gap needed when i lands before j
    n = len(earliest)                            # number of aircraft

    m = Model()

    # landing_times[i] is when aircraft i lands, inside its own time window
    landing_times = [m.int(f"landing_time_{i}", earliest[i], latest[i]) for i in range(n)]

    # Aircraft land in the given order, each at least the separation time after every earlier one.
    for i in range(n):
        for j in range(i + 1, n):
            m &= (landing_times[i] + separation[i][j] <= landing_times[j])

    # The penalty of landing aircraft i at time t: per time unit early, or per time unit late.
    def penalty(i, t):
        return penalty_before[i] * max(0, target[i] - t) + penalty_after[i] * max(0, t - target[i])

    # The total penalty sums, per aircraft, its penalty as a step function over its time window.
    total_penalty = sum_expr(
        time.piecewise(base_value=penalty(i, time.lb),
                       steps={t: penalty(i, t) for t in range(time.lb + 1, time.ub + 1)})
        for i, time in enumerate(landing_times))

    # Minimise the total penalty.
    m.obj += total_penalty

    return m, {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
