from hermax.model import Model


def build(instance):
    # Progressive party: choose host boats and a visit schedule. visits[p][b] is the boat
    # whose location boat b is at in period p. A host stays at its own location, so
    # visits[p][h] == h for hosts. Objective: minimise the number of hosts.
    n = instance["n_boats"]
    P = instance["n_periods"]
    cap = list(instance["capacity"])
    crew = list(instance["crew_size"])

    m = Model()

    is_host = m.bool_vector("is_host", n)
    visits = m.int_matrix("visits", P, n, 0, n - 1)

    for p in range(P):
        for b in range(n):
            # A boat can only be at a host location, and a host is at its own location.
            for v in range(n):
                m &= (~(visits[p][b] == v) | is_host[v])
            m &= (~is_host[b] | (visits[p][b] == b))

    # Capacity: for every host and period, everyone aboard (host crew included) fits.
    for p in range(P):
        for h in range(n):
            m &= (sum(crew[b] * (visits[p][b] == h) for b in range(n)) <= cap[h])

    # Two boats share a location in at most one period. This also limits a guest crew
    # to one visit per host, since hosts sit at their own location.
    for i in range(n):
        for j in range(i + 1, n):
            together = []
            for p in range(P):
                r = m.bool()
                m &= (visits[p][i] == visits[p][j]).iff(r)
                together.append(r)
            m &= (sum(together) <= 1)

    # Minimise the number of host boats.
    m.obj += sum(is_host[b] for b in range(n))

    return m, {"is_host": is_host, "visits": visits}
