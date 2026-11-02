"""Progressive party: choose host boats and move the guest crews between hosts, minimising the number of hosts."""
import hexaly.optimizer as hx


def build(instance):
    n, periods = instance["n_boats"], instance["n_periods"]
    capacity, crew = instance["capacity"], instance["crew_size"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    is_host = [model.bool() for _ in range(n)]
    # on[p][b][h] = 1 if the crew of boat b is aboard boat h in period p
    on = [[[model.bool() for _ in range(n)] for _ in range(n)] for _ in range(periods)]

    for p in range(periods):
        for b in range(n):
            # Every crew is aboard exactly one boat in each period
            model.constraint(model.sum(on[p][b]) == 1)
            # A host crew stays on its own boat
            model.constraint(on[p][b][b] >= is_host[b])
            # Crews only go aboard host boats
            for h in range(n):
                model.constraint(on[p][b][h] <= is_host[h])
        # The people aboard a host, its own crew included, fit its capacity
        for h in range(n):
            model.constraint(model.sum(crew[b] * on[p][b][h] for b in range(n)) <= capacity[h])

    # A guest crew does not visit the same host twice
    for b in range(n):
        for h in range(n):
            if h != b:
                model.constraint(model.sum(on[p][b][h] for p in range(periods)) <= 1)
    # Two crews meet at most once
    for b1 in range(n):
        for b2 in range(b1 + 1, n):
            model.constraint(model.sum(on[p][b1][h] * on[p][b2][h] for p in range(periods) for h in range(n)) <= 1)

    # Minimise the number of host boats
    model.minimize(model.sum(is_host))

    # visits[p][b] is the boat (0-based) where crew b is in period p; a host is on its own boat
    visits = [[model.sum(h * on[p][b][h] for h in range(n)) for b in range(n)] for p in range(periods)]
    return optimizer, {"visits": visits, "is_host": is_host}
