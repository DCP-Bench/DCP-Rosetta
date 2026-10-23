from hermax.model import Model


def build(instance):
    demand = instance["demand"]
    requires = instance["requires"]
    at_most = instance["at_most"]
    per_slots = instance["per_slots"]

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)

    m = Model()
    x = m.bool_matrix("x", n_cars, n_types)
    for p in range(n_cars):
        m &= x.row(p).exactly_one()
    for c in range(n_types):
        m &= (sum(x[p][c] for p in range(n_cars)) == demand[c])

    # needs[o][p] is true when the car at position p requires option o.
    needs = []
    for o in range(n_options):
        row = []
        for p in range(n_cars):
            nb = m.bool()
            m &= (sum(x[p][c] for c in range(n_types) if requires[c][o]) <= 0).iff(~nb)
            row.append(nb)
        needs.append(row)

    for o in range(n_options):
        k = per_slots[o]
        cap = at_most[o]
        for start in range(n_cars - k + 1):
            m &= (sum(needs[o][p] for p in range(start, start + k)) <= cap)

    sequence = [sum(c * x[p][c] for c in range(n_types)) for p in range(n_cars)]
    return m, {"sequence": sequence}
