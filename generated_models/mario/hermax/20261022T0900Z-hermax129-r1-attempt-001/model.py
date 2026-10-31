from hermax.model import Model


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel = instance["arc_fuel"]
    limit = instance["fuelLimit"]
    gold = instance["goldInHouse"]

    m = Model()
    # x[i][j] says the route leaves house i for house j. The diagonal x[i][i]
    # says house i is not on the route, so s[i] = i for it.
    x = m.bool_matrix("x", n, n)

    # Every house has exactly one successor and exactly one predecessor.
    for i in range(n):
        m &= x.row(i).exactly_one()
        m &= x.col(i).exactly_one()

    # Mario's house is on the route. Luigi's house is on the route and its
    # successor is Mario's house, which closes the route.
    m &= ~x[mario][mario]
    m &= ~x[luigi][luigi]
    m &= x[luigi][mario]
    for j in range(n):
        if j != mario and j != luigi:
            m &= ~x[luigi][j]
        if j != luigi and j != mario:
            m &= ~x[j][mario]

    # Ordering: each house on the route gets a position, and every arc other
    # than the closing arc into Mario's house moves forward by one. This
    # rules out cycles that avoid Mario's house.
    pos = m.int_vector("pos", n, 0, n - 1)
    m &= (pos[mario] == 0)
    for i in range(n):
        for j in range(n):
            if i != j and j != mario:
                m &= (pos[j] >= pos[i] + 1).only_if(x[i][j])

    # Fuel along the route stays within the limit.
    m &= (sum(fuel[i][j] * x[i][j] for i in range(n) for j in range(n) if i != j)
          <= limit)

    # Output s[i] is the successor of house i (s[i] = i when not on the route).
    s = m.int_vector("s", n, 0, n - 1)
    for i in range(n):
        m &= (s[i] == sum(j * x[i][j] for j in range(n)))

    # Maximise gold: a house on the route is one whose diagonal is false.
    m.obj += 0 - sum(gold[i] * ~x[i][i] for i in range(n))

    return m, {"s": s}
