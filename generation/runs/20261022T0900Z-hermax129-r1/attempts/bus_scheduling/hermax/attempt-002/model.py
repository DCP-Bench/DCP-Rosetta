from hermax.model import Model


def build(instance):
    """
    Bus scheduling: minimize the number of buses to meet demand.
    - 6 time slots, each 4 hours
    - Each bus works 8 hours (2 consecutive slots)
    - x[i] = number of buses starting at slot i (working slots i and (i+1)%6)
    - At each slot, must have enough buses to meet demand
    """

    m = Model()

    demands = instance["demands"]
    n_slots = len(demands)

    # Number of buses starting at each slot
    # Upper bound: max demand across all slots (worst case: one shift covers it)
    max_demand = max(demands) if demands else 0
    x = m.int_vector("x", n_slots, 0, max_demand)

    # Demand constraints: buses from two consecutive shifts cover each slot
    # Each slot i is covered by buses starting at slot i-1 and slot i
    for i in range(n_slots):
        # Buses starting at previous slot and current slot must meet demand
        prev_i = (i - 1) % n_slots
        m &= (x[prev_i] + x[i] >= demands[i])

    # Minimize total buses: pay when each bus x[i] is used (when true)
    for i in range(n_slots):
        m.obj[1] += x[i]

    return m, {"x": x}
