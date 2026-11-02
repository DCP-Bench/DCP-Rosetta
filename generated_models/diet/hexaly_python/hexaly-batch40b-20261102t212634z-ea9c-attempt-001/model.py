"""Diet: choose servings of four foods that meet the nutritional minimums at the lowest cost."""
import hexaly.optimizer as hx

# Per serving: calories, chocolate, sugar and fat (ounces) of chocolate cake, chocolate ice
# cream, cola and pineapple cheesecake. The problem statement fixes this table; the instance
# gives only prices and limits.
CONTENT = [[400, 3, 2, 2],
           [200, 2, 2, 4],
           [150, 0, 4, 1],
           [500, 0, 4, 5]]


def build(instance):
    n, price, limits = instance["n"], instance["price"], instance["limits"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # servings[f] of food f; no requirement needs more servings than its largest limit
    servings = [model.int(0, max(limits)) for _ in range(n)]

    # Every nutrient reaches at least its limit
    for k in range(len(limits)):
        model.constraint(model.sum(CONTENT[f][k] * servings[f] for f in range(n)) >= limits[k])

    # Minimise the cost of the diet
    cost = model.sum(price[f] * servings[f] for f in range(n))
    model.minimize(cost)
    return optimizer, {"cost": cost}
