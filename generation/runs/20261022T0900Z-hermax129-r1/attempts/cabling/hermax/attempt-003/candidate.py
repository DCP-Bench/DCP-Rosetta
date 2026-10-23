"""Cabling - minimize total cable length when arranging devices in a rack.

Devices must be arranged in a line. Cable cost is the number of cables times
the distance between devices. Goal: minimize total cost.
"""

from hermax.model import Model


def build(instance):
    n = instance["n"]
    devices = instance["devices"]
    cable_struct = instance["cable_struct"]

    m = Model()

    # Decision variable: position of each device (0 to n-1)
    device_pos = m.int_vector("device_pos", n, 0, n - 1)
    m &= device_pos.all_different()

    # Build a mapping from device name to index
    device_to_idx = {dev: idx for idx, dev in enumerate(devices)}

    # Calculate total cable cost using explicit enumeration of distances
    # For each pair of devices connected by cables, we charge based on their distance

    # Maximum possible total cost
    max_total_cost = sum(cable[2] for cable in cable_struct) * (n - 1)

    # Create auxiliary variable for total cost
    total_cost = m.sum_var([0])  # Start with 0

    # For each cable, add its contribution to total cost
    for cable in cable_struct:
        dev1_name = cable[0]
        dev2_name = cable[1]
        cable_count = cable[2]

        dev1_idx = device_to_idx[dev1_name]
        dev2_idx = device_to_idx[dev2_name]

        pos1 = device_pos[dev1_idx]
        pos2 = device_pos[dev2_idx]

        # Cost for this cable: cable_count * |pos1 - pos2|
        # Enumerate all possible distances
        for d in range(1, n):
            # Charge cable_count * d when distance is exactly d
            # Distance is d if (pos1 - pos2 == d) or (pos2 - pos1 == d)
            dist_eq_d = (pos1 - pos2 == d)
            dist_eq_minus_d = (pos2 - pos1 == d)

            # When distance is d, add cable_count * d to objective
            for _ in range(cable_count * d):
                m.obj[1] += (dist_eq_d | dist_eq_minus_d)

    # Create final_sum variable for output - calculate it separately
    final_sum = m.int("final_sum", 0, max_total_cost)

    # Build constraint: final_sum equals the sum of all cable costs
    cable_cost_sum = 0
    for cable in cable_struct:
        dev1_name = cable[0]
        dev2_name = cable[1]
        cable_count = cable[2]

        dev1_idx = device_to_idx[dev1_name]
        dev2_idx = device_to_idx[dev2_name]

        pos1 = device_pos[dev1_idx]
        pos2 = device_pos[dev2_idx]

        # Create distance expression
        dist = m.max([pos1 - pos2, pos2 - pos1])
        cable_cost = cable_count * dist
        cable_cost_sum = cable_cost_sum + cable_cost

    m &= (final_sum == cable_cost_sum)

    outputs = {
        "final_sum": final_sum,
    }

    return m, outputs
