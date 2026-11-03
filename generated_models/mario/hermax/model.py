# mario: a hermax (Python) model from DCP Rosetta.
# Download the `mario.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/mario.html
# Then run it on the first instance (after `pip install hermax`):
#   python mario.py mario.json

from hermax.model import Model


def create_model(instance):
    """Mario starts at his house, visits some of the houses in some order, and ends at
    Luigi's house, from where he returns to Mario's house. Each house has gold and each
    travel arc uses fuel. Collect as much gold as possible without exceeding the fuel
    limit, and report for each house the house that follows it on the route."""
    n = instance["nHouses"]          # the number of houses, numbered 0..n-1
    mario = instance["marioHouse"]   # the house where Mario starts
    luigi = instance["luigiHouse"]   # the house where the route ends
    fuel = instance["arc_fuel"]      # fuel[i][j]: fuel used travelling from house i to house j
    limit = instance["fuelLimit"]    # the most fuel Mario has
    gold = instance["goldInHouse"]   # gold[i]: the gold in house i

    m = Model()
    # x[i][j] is true when the route goes directly from house i to house j.
    # A house left off the route is its own successor, so x[i][i] is true for it.
    x = m.bool_matrix("x", n, n)

    # Every house has exactly one successor and exactly one predecessor.
    for i in range(n):
        m &= x.row(i).exactly_one()
        m &= x.col(i).exactly_one()

    # Mario's house is on the route, and so is Luigi's. The route leaves Luigi's
    # house straight back to Mario's house.
    m &= ~x[mario][mario]
    m &= ~x[luigi][luigi]
    m &= x[luigi][mario]

    # Ordering: Mario's house gets position 0 and each house on the route comes
    # after the house before it. Every arc except the closing one back into
    # Mario's house must move forward, which rules out loops that skip Mario's house.
    pos = m.int_vector("pos", n, 0, n - 1)
    m &= (pos[mario] == 0)
    for i in range(n):
        for j in range(n):
            if i != j and j != mario:
                m &= (pos[j] >= pos[i] + 1).only_if(x[i][j])

    # The fuel used on the route's arcs stays within Mario's limit.
    # (Diagonal entries mark houses off the route and use no fuel.)
    m &= (sum(fuel[i][j] * x[i][j] for i in range(n) for j in range(n) if i != j) <= limit)

    # Output s[i] is the house after house i on the route, or i itself if it is off the route.
    s = m.int_vector("s", n, 0, n - 1)
    for i in range(n):
        m &= (s[i] == sum(j * x[i][j] for j in range(n)))

    # Maximise the gold collected: a house is on the route when x[i][i] is false.
    m.obj += -sum(gold[i] * ~x[i][i] for i in range(n))

    return m, {"s": s}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
