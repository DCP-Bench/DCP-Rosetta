from hermax.model import Model


def build(instance):
    """
    Bus scheduling problem: minimize the number of buses in each time slot
    to meet demand. Each bus operates for 8 consecutive hours (covers 2 successive
    4-hour slots). The schedule is cyclic (wraps from slot 5 to slot 0).

    Instance: demands - the demand for buses in each of 6 time slots
    Output: x - the number of buses scheduled (starting) in each time slot
    """
    demands = instance["demands"]
    n = len(demands)  # 6 time slots

    m = Model()

    # x[i] = number of buses scheduled to start in slot i
    # A bus starting in slot i operates through slots i and (i+1) mod n
    x = m.int_vector("x", n, 0, max(demands) * 2 if demands else 0)

    # Constraints: buses available in each slot must meet demand
    # Buses in slot i come from buses starting in slot i and slot (i-1) mod n
    for i in range(n):
        buses_in_slot_i = x[i] + x[(i - 1) % n]
        m &= (buses_in_slot_i >= demands[i])

    # Objective: minimize total number of buses
    for i in range(n):
        m.obj[1] += x[i]

    return m, {"x": x}
