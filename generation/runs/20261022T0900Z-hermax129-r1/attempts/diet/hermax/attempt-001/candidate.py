from hermax.model import Model


def build(instance):
    # Diet optimization: minimize cost while meeting nutritional requirements.
    # Food: [Cake, IceCream, Cola, Cheesecake]
    # Nutrition:  [[Calories, Chocolate, Sugar, Fat], ...]
    nutrition = [
        [400, 3, 2, 2],  # Chocolate cake
        [200, 2, 2, 4],  # Ice cream
        [150, 0, 4, 1],  # Cola
        [500, 0, 4, 5],  # Cheesecake
    ]

    price = instance["price"]
    limits = instance["limits"]
    n = instance["n"]  # Should be 4

    m = Model()

    # Variables: quantity of each food item (non-negative integers)
    # Reasonable upper bound: limits[i] / min_nutrition[i] for each nutrient
    # Or just use a fixed bound like 20
    quantity = m.int_vector("quantity", n, 0, 20)

    # Nutritional constraints: total nutrition >= limits for each type
    for nutrient_idx in range(4):
        total_nutrition = sum(quantity[i] * nutrition[i][nutrient_idx] for i in range(n))
        m &= (total_nutrition >= limits[nutrient_idx])

    # Objective: minimize cost
    total_cost = sum(quantity[i] * price[i] for i in range(n))

    # Minimize cost: pay 1 for each unit of cost
    # This approach works but creates many soft clauses
    max_cost = 20 * max(price)  # Upper bound on cost
    for c in range(1, min(500, max_cost + 1)):
        m.obj[1] += (total_cost >= c)

    return m, {"cost": total_cost}
