"""Aircraft landing: land aircraft on one runway in their fixed order, each within its time window and far enough
after the aircraft before it, minimising the penalties for landing earlier or later than its target time."""
import hexaly.optimizer as hx


def build(instance):
    # earliest_landing[i], latest_landing[i]: the time window in which aircraft i may land
    # target_landing[i]: the time at which aircraft i would like to land
    earliest, latest, target = instance["earliest_landing"], instance["latest_landing"], instance["target_landing"]
    # penalty_before[i], penalty_after[i]: cost per time unit that aircraft i lands before / after its target time
    # separation_time[i][j]: minimum time between the landings of aircraft i and j, when i lands first
    before, after, separation = instance["penalty_before"], instance["penalty_after"], instance["separation_time"]
    n = len(target)  # number of aircraft, numbered in their fixed landing order
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # t[i] = landing time of aircraft i; the bounds make each aircraft land within its time window
    t = [model.int(earliest[i], latest[i]) for i in range(n)]

    # Fixed landing sequence: aircraft j lands after aircraft i (i < j), at least the separation time later
    for i in range(n):
        for j in range(i + 1, n):
            model.constraint(t[j] >= t[i] + separation[i][j])

    # early[i] and late[i] = time units aircraft i lands before and after its target time. Their upper bounds are
    # the room the window leaves on each side of the target (0 if the target is outside the window). Linear
    # deviations, rather than max(0, ...), give Hexaly a bound it can close.
    early = [model.int(0, max(0, target[i] - earliest[i])) for i in range(n)]
    late = [model.int(0, max(0, latest[i] - target[i])) for i in range(n)]
    # The landing time differs from the target by the late amount minus the early amount
    for i in range(n):
        model.constraint(t[i] - target[i] == late[i] - early[i])

    # Minimise the total penalty: penalty_before per time unit landed early plus penalty_after per time unit landed late
    total_penalty = model.sum(before[i] * early[i] + after[i] * late[i] for i in range(n))
    model.minimize(total_penalty)
    return optimizer, {"landing_times": t, "total_penalty": total_penalty}
