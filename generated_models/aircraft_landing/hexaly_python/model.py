"""Aircraft landing: land aircraft in their fixed order within their windows, minimising early and late penalties."""
import hexaly.optimizer as hx


def build(instance):
    earliest, latest, target = instance["earliest_landing"], instance["latest_landing"], instance["target_landing"]
    before, after, separation = instance["penalty_before"], instance["penalty_after"], instance["separation_time"]
    n = len(target)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each aircraft lands within its time window
    t = [model.int(earliest[i], latest[i]) for i in range(n)]

    # Fixed landing sequence: aircraft j lands after aircraft i (i < j), at least the separation time later
    for i in range(n):
        for j in range(i + 1, n):
            model.constraint(t[j] >= t[i] + separation[i][j])

    # early[i] and late[i] measure how far aircraft i lands before or after its target. Linear
    # deviations, rather than max(0, ...), give Hexaly a bound it can close.
    early = [model.int(0, max(0, target[i] - earliest[i])) for i in range(n)]
    late = [model.int(0, max(0, latest[i] - target[i])) for i in range(n)]
    for i in range(n):
        model.constraint(t[i] - target[i] == late[i] - early[i])

    # Minimise the total penalty for landing early or late
    total_penalty = model.sum(before[i] * early[i] + after[i] * late[i] for i in range(n))
    model.minimize(total_penalty)
    return optimizer, {"landing_times": t, "total_penalty": total_penalty}
