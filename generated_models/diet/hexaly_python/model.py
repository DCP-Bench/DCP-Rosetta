"""Diet: choose servings of four foods that meet the nutritional minimums at the lowest cost."""
import hexaly.optimizer as hx

# CONTENT[f][k] = amount of nutrient k in one serving of food f. Foods (rows): chocolate cake (1 slice),
# chocolate ice cream (1 scoop), cola (1 bottle), pineapple cheesecake (1 piece). Nutrients (columns): calories,
# chocolate, sugar, fat, the last three in ounces. The problem statement fixes this table, so it is mirrored
# here; the instance gives only prices and limits.
CONTENT = [[400, 3, 2, 2],
           [200, 2, 2, 4],
           [150, 0, 4, 1],
           [500, 0, 4, 5]]


def build(instance):
    # n = number of foods; price[f] = price of one serving of food f
    # limits[k] = minimum amount of nutrient k the diet must contain (same order as the columns of CONTENT)
    n, price, limits = instance["n"], instance["price"], instance["limits"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # servings[f] = number of servings of food f in the diet. Bound: every nutrient a food holds is at least 1
    # unit per serving, so max(limits) servings of it already cover any limit it helps to meet.
    servings = [model.int(0, max(limits)) for _ in range(n)]

    # Every nutrient reaches at least its limit (the nutritional requirements are minimums)
    for k in range(len(limits)):
        model.constraint(model.sum(CONTENT[f][k] * servings[f] for f in range(n)) >= limits[k])

    # Minimise the cost of the diet: the price of the servings bought
    cost = model.sum(price[f] * servings[f] for f in range(n))
    model.minimize(cost)
    return optimizer, {"cost": cost}
