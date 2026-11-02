"""Cabling: order the devices in a rack so that the total length of the cables between them is minimal."""
import hexaly.optimizer as hx


def build(instance):
    n, devices, cables = instance["n"], instance["devices"], instance["cable_struct"]
    index = {d: i for i, d in enumerate(devices)}
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # at[d][s] = 1 if device d sits in rack slot s: every device in one slot, one device per slot
    at = [[model.bool() for _ in range(n)] for _ in range(n)]
    for d in range(n):
        model.constraint(model.sum(at[d]) == 1)
    for s in range(n):
        model.constraint(model.sum(at[d][s] for d in range(n)) == 1)
    position = [model.sum(s * at[d][s] for s in range(n)) for d in range(n)]

    # A cable between two devices is as long as the distance between their slots; gap[k] is at
    # least that distance both ways, so at the minimum it equals it. Linear, unlike abs().
    lengths = []
    for k, (a, b, count) in enumerate(cables):
        gap = model.int(0, n - 1)
        model.constraint(gap >= position[index[a]] - position[index[b]])
        model.constraint(gap >= position[index[b]] - position[index[a]])
        # count cables run between the two devices
        lengths.append(count * gap)

    final_sum = model.sum(lengths)
    model.minimize(final_sum)
    return optimizer, {"final_sum": final_sum}
