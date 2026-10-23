from hermax.model import Model


def build(instance):
    demand = instance["demand"]          # cars of each type
    requires = instance["requires"]      # requires[type][option] in {0, 1}
    at_most = instance["at_most"]        # option o: at most at_most[o] cars per window
    per_slots = instance["per_slots"]    # window length for option o

    n_types = len(demand)
    n_opts = len(at_most)
    n_cars = sum(demand)                 # sequence length, taken from the instance

    m = Model()
    # x[q][c]: position q carries a car of type c. Exactly one type per position.
    x = m.bool_matrix("x", n_cars, n_types)
    for q in range(n_cars):
        m &= x.row(q).exactly_one()

    # Each type c is built exactly demand[c] times.
    for c in range(n_types):
        m &= (sum(x[q][c] for q in range(n_cars)) == demand[c])

    # y[q][o]: the car at position q needs option o. Channelled to x by clauses.
    y = m.bool_matrix("y", n_cars, n_opts)
    for q in range(n_cars):
        for o in range(n_opts):
            for c in range(n_types):
                if requires[c][o]:
                    m &= (~x[q][c] | y[q][o])
                else:
                    m &= (~x[q][c] | ~y[q][o])

    # Capacity: in every window of per_slots[o] consecutive positions, at most at_most[o] cars need option o.
    for o in range(n_opts):
        w = per_slots[o]
        for start in range(n_cars - w + 1):
            m &= (sum(y[q][o] for q in range(start, start + w)) <= at_most[o])

    # Output: the type at each position, as an integer.
    seq = []
    for q in range(n_cars):
        t = m.int(f"t{q}", 0, n_types - 1)
        m &= (t == sum(c * x[q][c] for c in range(1, n_types)))
        seq.append(t)

    return m, {"sequence": seq}
