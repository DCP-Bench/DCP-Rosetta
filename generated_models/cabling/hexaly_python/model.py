"""Cabling: order the devices in a rack so that the total length of the cables between them is minimal."""
import hexaly.optimizer as hx


def build(instance):
    # n = number of 1U devices (= number of rack slots); devices = the device names;
    # cable_struct = one row per connected pair: [first device name, second device name,
    # number of cables between the two]
    n, devices, cables = instance["n"], instance["devices"], instance["cable_struct"]
    # device name -> its index in devices, to look the names in cable_struct up
    index = {d: i for i, d in enumerate(devices)}
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # at[d][s] = 1 if device d sits in rack slot s: every device in one slot, one device per slot
    at = [[model.bool() for _ in range(n)] for _ in range(n)]
    for d in range(n):
        model.constraint(model.sum(at[d]) == 1)
    for s in range(n):
        model.constraint(model.sum(at[d][s] for d in range(n)) == 1)
    # position[d] = the slot number (0 .. n-1) device d sits in
    position = [model.sum(s * at[d][s] for s in range(n)) for d in range(n)]

    # A cable between two devices is as long as the distance between their slots; gap[k] is at
    # least that distance both ways, so at the minimum it equals it. Linear, unlike abs().
    lengths = []
    for k, (a, b, count) in enumerate(cables):
        # distance in slots between the two devices of cable row k; at most n - 1 apart
        gap = model.int(0, n - 1)
        model.constraint(gap >= position[index[a]] - position[index[b]])
        model.constraint(gap >= position[index[b]] - position[index[a]])
        # count cables run between the two devices
        lengths.append(count * gap)

    # The sum of all cable lengths is as short as possible
    final_sum = model.sum(lengths)
    model.minimize(final_sum)
    return optimizer, {"final_sum": final_sum}
