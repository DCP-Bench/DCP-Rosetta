"""Mario: a route from Mario's house to Luigi's house within the fuel limit, collecting as much gold as possible."""
import hexaly.optimizer as hx


def build(instance):
    n, fuel, limit = instance["nHouses"], instance["arc_fuel"], instance["fuelLimit"]
    gold, mario, luigi = instance["goldInHouse"], instance["marioHouse"], instance["luigiHouse"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # arc[i][j] = 1 if the route goes from house i to house j; visit[i] = 1 if house i is on it.
    # The route closes into a cycle through the arc from Luigi's house back to Mario's.
    arc = [[model.bool() if i != j else 0 for j in range(n)] for i in range(n)]
    visit = [model.bool() for _ in range(n)]
    model.constraint(visit[mario] == 1)
    model.constraint(visit[luigi] == 1)
    model.constraint(arc[luigi][mario] == 1)
    # A house on the route is entered once and left once; a house off the route is neither
    for i in range(n):
        model.constraint(model.sum(arc[i][j] for j in range(n)) == visit[i])
        model.constraint(model.sum(arc[j][i] for j in range(n)) == visit[i])
    # No separate loops: order[i] increases along every arc of the route except the closing one
    order = [model.int(0, n - 1) for _ in range(n)]
    model.constraint(order[mario] == 0)
    for i in range(n):
        for j in range(n):
            if i != j and j != mario:
                model.constraint(order[j] >= order[i] + 1 - n * (1 - arc[i][j]))
    # The fuel used on the way from Mario to Luigi stays within the limit
    model.constraint(model.sum(fuel[i][j] * arc[i][j] for i in range(n) for j in range(n)
                               if i != j and not (i == luigi and j == mario)) <= limit)

    # Maximise the gold in the houses visited
    model.maximize(model.sum(gold[i] * visit[i] for i in range(n)))

    # s[i] is the house after house i on the route, or i itself if i is not on it
    s = [model.sum(j * arc[i][j] for j in range(n) if j != i) + i * (1 - visit[i]) for i in range(n)]
    return optimizer, {"s": s}
