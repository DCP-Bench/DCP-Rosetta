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

    # Minimize total cable cost: sum of cable_count * distance between devices
    # For each cable, add soft clauses that charge based on distance
    for cable in cable_struct:
        dev1_name = cable[0]
        dev2_name = cable[1]
        cable_count = cable[2]

        dev1_idx = device_to_idx[dev1_name]
        dev2_idx = device_to_idx[dev2_name]

        pos1 = device_pos[dev1_idx]
        pos2 = device_pos[dev2_idx]

        # For each pair of positions (i, j), add cost cable_count * |i - j|
        # We charge cable_count for each unit of distance
        # To implement this without an auxiliary variable, we enumerate all possible distances
        # and charge cable_count for each distance that occurs

        # Distance = |pos1 - pos2|
        # For each possible distance d from 1 to n-1, charge if distance >= d
        for d in range(1, n):
            # Charge cable_count if |pos1 - pos2| >= d
            # This is equivalent to: (pos1 - pos2 >= d) OR (pos2 - pos1 >= d)
            m.obj[cable_count] += ((pos1 - pos2 >= d) | (pos2 - pos1 >= d))

    # Calculate final_sum for output
    max_total_cost = sum(cable[2] for cable in cable_struct) * (n - 1)
    final_sum = m.int("final_sum", 0, max_total_cost)

    # Build the sum of cable costs
    cable_costs = []
    for cable in cable_struct:
        dev1_name = cable[0]
        dev2_name = cable[1]
        cable_count = cable[2]

        dev1_idx = device_to_idx[dev1_name]
        dev2_idx = device_to_idx[dev2_name]

        pos1 = device_pos[dev1_idx]
        pos2 = device_pos[dev2_idx]

        # Create expression for cable_count * |pos1 - pos2|
        # Use sum of indicator variables for each distance
        dist_cost = 0
        for d in range(1, n):
            dist_cost = dist_cost + cable_count * ((pos1 - pos2 >= d) | (pos2 - pos1 >= d))
        cable_costs.append(dist_cost)

    total_cost = sum(cable_costs)
    m &= (final_sum == total_cost)

    outputs = {
        "final_sum": final_sum,
    }

    return m, outputs
