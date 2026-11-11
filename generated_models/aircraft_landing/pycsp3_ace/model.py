# aircraft_landing: a PyCSP3 model from DCP Rosetta.
# Download the `aircraft_landing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_landing.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python aircraft_landing.py aircraft_landing.json

from pycsp3 import *


def create_model(instance):
    """A set of aircraft must land on a single runway in a fixed sequence. Each aircraft has a
    time window and a target landing time; landing early or late costs a penalty per unit of
    time. Any two landings must be separated by a minimum time. Find the landing time of
    each aircraft that minimises the total penalty."""
    earliest_landing = instance["earliest_landing"]  # earliest_landing[i]: the first time aircraft i may land
    latest_landing = instance["latest_landing"]      # latest_landing[i]: the last time aircraft i may land
    target_landing = instance["target_landing"]      # target_landing[i]: the time aircraft i should land
    penalty_before = instance["penalty_before"]      # penalty_before[i]: cost per unit of time aircraft i lands early
    penalty_after = instance["penalty_after"]        # penalty_after[i]: cost per unit of time aircraft i lands late
    separation_time = instance["separation_time"]    # separation_time[i][j]: minimum gap between landing i and a later landing j
    n_aircraft = len(target_landing)

    # Aircraft i lands no earlier than its window opens, so it is early by at most target minus
    # earliest (none when the window opens after its target), and it is late by at most latest
    # minus target (none when the window closes before its target).
    max_earliness = [max(0, target_landing[i] - earliest_landing[i]) for i in range(n_aircraft)]
    max_tardiness = [max(0, latest_landing[i] - target_landing[i]) for i in range(n_aircraft)]

    # landing_times[i] is the time at which aircraft i lands, within its time window.
    landing_times = VarArray(size=n_aircraft, dom=lambda i: range(earliest_landing[i], latest_landing[i] + 1))

    # earliness[i] is how far before its target aircraft i lands (0 when it does not land early).
    earliness = VarArray(size=n_aircraft, dom=lambda i: range(max_earliness[i] + 1))

    # tardiness[i] is how far after its target aircraft i lands (0 when it does not land late).
    tardiness = VarArray(size=n_aircraft, dom=lambda i: range(max_tardiness[i] + 1))

    # total_penalty is the penalty of all aircraft together: each unit of earliness and of
    # tardiness costs its aircraft's penalty, so no choice can cost more than the sum of the
    # largest earliness and tardiness of every aircraft.
    total_bound = sum(penalty_before[i] * max_earliness[i] + penalty_after[i] * max_tardiness[i] for i in range(n_aircraft))
    total_penalty = Var(dom=range(total_bound + 1))

    satisfy(
        # Separation: in the fixed landing sequence, aircraft j lands at least separation_time[i][j]
        # after each earlier aircraft i.
        [landing_times[j] - landing_times[i] >= separation_time[i][j] for i in range(n_aircraft) for j in range(i + 1, n_aircraft)],
        # An aircraft landing before its target is early by the difference, otherwise not early at all.
        [earliness[i] == Maximum(0, target_landing[i] - landing_times[i]) for i in range(n_aircraft)],
        # An aircraft landing after its target is late by the difference, otherwise not late at all.
        [tardiness[i] == Maximum(0, landing_times[i] - target_landing[i]) for i in range(n_aircraft)],
        # The total penalty: each unit of earliness and of tardiness costs its aircraft's penalty.
        total_penalty == Sum(penalty_before[i] * earliness[i] + penalty_after[i] * tardiness[i] for i in range(n_aircraft)),
    )

    # Minimise the total penalty.
    minimize(total_penalty)

    return {"landing_times": landing_times, "total_penalty": total_penalty}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("landing_times =", values(outputs["landing_times"]))
        print("total_penalty =", value(outputs["total_penalty"]))
    else:
        print("No solution:", status())
