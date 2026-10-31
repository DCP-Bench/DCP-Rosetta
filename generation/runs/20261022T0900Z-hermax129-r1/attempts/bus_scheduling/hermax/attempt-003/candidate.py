from hermax.model import Model


def build(instance):
    """
    Bus scheduling: minimize the number of buses to meet demand.
    - 6 time slots, each 4 hours
    - Each bus works 8 hours (2 consecutive slots)
    - x[i] = number of buses starting at slot i (working slots i and (i+1)%6)
    - At each slot, must have enough buses to meet demand
    - Objective: minimize total buses used
    """

    m = Model()

    demands = instance["demands"]
    n_slots = len(demands)

    # Number of buses starting at each slot
    # Upper bound: maximum demand (worst case scenario)
    max_demand = max(demands) if demands else 0
    x = m.int_vector("x", n_slots, 0, max_demand)

    # Demand constraints: buses from two consecutive shifts cover each slot
    # Slot i is covered by buses starting at slot (i-1)%n_slots and slot i
    for i in range(n_slots):
        prev_i = (i - 1) % n_slots
        # Buses from previous shift and current shift must meet demand
        m &= (x[prev_i] + x[i] >= demands[i])

    # Minimize total buses: add cost for each bus used
    for i in range(n_slots):
        m.obj[1] += x[i]

    return m, {"x": x}
