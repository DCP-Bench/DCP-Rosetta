"""Progressive party: choose host boats and move the guest crews between hosts, minimising the number of hosts.

Some boats are hosts, and their crews stay aboard. The crews of the other boats visit the
hosts, one host per period, over several periods. A boat holds a limited number of people,
a guest crew never revisits a host, and two crews meet at most once.
"""
import hexaly.optimizer as hx


def build(instance):
    # n_boats: number of boats (and so of crews); n_periods: number of successive half-hour periods
    n, periods = instance["n_boats"], instance["n_periods"]
    # capacity[h]: most people boat h can hold at a time; crew_size[b]: number of people in the crew of boat b
    capacity, crew = instance["capacity"], instance["crew_size"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_host[b] = 1 if boat b is designated a host boat
    is_host = [model.bool() for _ in range(n)]
    # on[p][b][h] = 1 if the crew of boat b is aboard boat h in period p
    # (booleans make the capacity a linear sum and the number of meetings a sum of products)
    on = [[[model.bool() for _ in range(n)] for _ in range(n)] for _ in range(periods)]

    for p in range(periods):
        for b in range(n):
            # Every crew is aboard exactly one boat in each period
            model.constraint(model.sum(on[p][b]) == 1)
            # A host crew stays on its own boat
            model.constraint(on[p][b][b] >= is_host[b])
            # Crews only go aboard host boats, so a guest crew visits a host and never a boat without one
            for h in range(n):
                model.constraint(on[p][b][h] <= is_host[h])
        # The people aboard a host, its own crew included, fit its capacity
        for h in range(n):
            model.constraint(model.sum(crew[b] * on[p][b][h] for b in range(n)) <= capacity[h])

    # A guest boat cannot revisit a host: over all periods, crew b is aboard another boat h at most once
    for b in range(n):
        for h in range(n):
            if h != b:
                model.constraint(model.sum(on[p][b][h] for p in range(periods)) <= 1)
    # Guest crews cannot meet more than once: two crews share a boat in at most one period
    for b1 in range(n):
        for b2 in range(b1 + 1, n):
            model.constraint(model.sum(on[p][b1][h] * on[p][b2][h] for p in range(periods) for h in range(n)) <= 1)

    # Minimise the number of host boats
    model.minimize(model.sum(is_host))

    # visits[p][b] is the boat (0-based) where crew b is in period p; a host is on its own boat
    # (the single 1 in on[p][b] picks out h, so the sum of h * on[p][b][h] is that boat's index)
    visits = [[model.sum(h * on[p][b][h] for h in range(n)) for b in range(n)] for p in range(periods)]
    return optimizer, {"visits": visits, "is_host": is_host}
