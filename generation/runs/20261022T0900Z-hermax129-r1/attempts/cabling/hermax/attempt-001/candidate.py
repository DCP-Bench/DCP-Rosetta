from hermax.model import Model


def build(instance):
    m = Model()

    # Extract instance data
    n = instance["n"]
    devices = instance["devices"]
    cable_struct = instance["cable_struct"]

    # Create a position variable for each device (0 to n-1)
    position = m.int_vector("position", n, 0, n - 1)

    # All devices must have different positions (all_different constraint)
    m &= position.all_different()

    # Parse cable connections
    # cable_struct is a list of [device_A, device_B, num_cables]
    cables = []
    for cable in cable_struct:
        device_a = cable[0]
        device_b = cable[1]
        num_cables = cable[2]
        cables.append((device_a, device_b, num_cables))

    # Create a mapping from device name to index
    device_to_idx = {device: i for i, device in enumerate(devices)}

    # Create absolute difference variables for each cable
    abs_diffs = m.int_vector("abs_diff", len(cables), 0, n - 1)

    # For each cable, add constraints and costs to the objective
    final_sum_expr = 0
    for idx, (device_a, device_b, num_cables) in enumerate(cables):
        idx_a = device_to_idx[device_a]
        idx_b = device_to_idx[device_b]

        # Constraint: abs_diff[idx] >= position[idx_a] - position[idx_b]
        m &= (abs_diffs[idx] >= position[idx_a] - position[idx_b])
        # Constraint: abs_diff[idx] >= position[idx_b] - position[idx_a]
        m &= (abs_diffs[idx] >= position[idx_b] - position[idx_a])

        # Add the cable cost to the objective
        cable_cost = num_cables * abs_diffs[idx]
        m.obj += cable_cost
        final_sum_expr += cable_cost

    return m, {"final_sum": final_sum_expr}
