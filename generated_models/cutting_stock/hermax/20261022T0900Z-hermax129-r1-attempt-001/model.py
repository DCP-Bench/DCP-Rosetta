from hermax.model import Model


def build(instance):
    # Cutting Stock Problem: Minimize the total number of raw rolls cut
    # such that each width requirement is met.

    # Extract instance data
    roll_width = instance["roll_width"]
    widths = instance["widths"]
    orders = instance["orders"]
    num_patterns = instance["num_patterns"]
    num_rolls_width = instance["num_rolls_width"]

    m = Model()

    # Decision variables: how many times to use each pattern
    patterns_used = m.int_vector("patterns_used", num_patterns, 0, max(orders))

    # Objective: minimize total rolls used (sum of patterns_used)
    for i in range(num_patterns):
        m.obj[1] += patterns_used[i]

    # Constraints: meet the order requirements for each width
    # For each width j, the total produced must be >= orders[j]
    for j in range(len(widths)):
        total_produced = sum(num_rolls_width[i][j] * patterns_used[i] for i in range(num_patterns))
        m &= (total_produced >= orders[j])

    # The total number of rolls cut is the sum of patterns_used
    min_rolls_cut = sum(patterns_used)

    return m, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}
