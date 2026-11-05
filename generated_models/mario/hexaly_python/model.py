"""Mario: a route from Mario's house to Luigi's house within the fuel limit, collecting as much gold as possible."""
import hexaly.optimizer as hx


def build(instance):
    # n = number of houses; fuel[i][j] = fuel used to travel from house i to house j; limit = the fuel Mario has
    n, fuel, limit = instance["nHouses"], instance["arc_fuel"], instance["fuelLimit"]
    # gold[i] = gold in house i; mario = index of Mario's house (the start); luigi = index of Luigi's house (the end)
    gold, mario, luigi = instance["goldInHouse"], instance["marioHouse"], instance["luigiHouse"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # arc[i][j] = 1 if the route goes from house i to house j (the constant 0 on the diagonal: no arc
    # from a house to itself); visit[i] = 1 if house i is on the route.
    # The route closes into a cycle through the arc from Luigi's house back to Mario's, as the
    # statement asks of the successor list s.
    arc = [[model.bool() if i != j else 0 for j in range(n)] for i in range(n)]
    visit = [model.bool() for _ in range(n)]
    # Mario's and Luigi's houses are on the route, and the closing arc goes from Luigi's house to Mario's
    model.constraint(visit[mario] == 1)
    model.constraint(visit[luigi] == 1)
    model.constraint(arc[luigi][mario] == 1)
    # A house on the route is entered once and left once; a house off the route is neither
    for i in range(n):
        model.constraint(model.sum(arc[i][j] for j in range(n)) == visit[i])
        model.constraint(model.sum(arc[j][i] for j in range(n)) == visit[i])
    # order[i] = position of house i along the route, 0 at Mario's house.
    # No separate loops: the position increases along every arc of the route except the closing one
    # into Mario's house. n serves as the big-M, since positions lie between 0 and n - 1, so the
    # constraint is slack for an arc that is not used.
    order = [model.int(0, n - 1) for _ in range(n)]
    model.constraint(order[mario] == 0)
    for i in range(n):
        for j in range(n):
            if i != j and j != mario:
                model.constraint(order[j] >= order[i] + 1 - n * (1 - arc[i][j]))
    # The fuel used on the way from Mario to Luigi (every arc of the route except the closing one) stays within the limit
    model.constraint(model.sum(fuel[i][j] * arc[i][j] for i in range(n) for j in range(n)
                               if i != j and not (i == luigi and j == mario)) <= limit)

    # Maximise the gold collected: the gold in the houses visited
    model.maximize(model.sum(gold[i] * visit[i] for i in range(n)))

    # s[i] = the house that follows house i on the route (Luigi's house is followed by Mario's),
    # or i itself if house i is not on the route; this is the output
    s = [model.sum(j * arc[i][j] for j in range(n) if j != i) + i * (1 - visit[i]) for i in range(n)]
    return optimizer, {"s": s}
