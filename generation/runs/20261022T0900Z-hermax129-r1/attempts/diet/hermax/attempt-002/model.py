from hermax.model import Model

# Nutrient content per unit of each food fixed by the problem statement.
# Rows: calories, chocolate (ounces), sugar (ounces), fat (ounces).
# Columns: chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
NUTRIENTS = [
    [400, 200, 150, 500],
    [3, 2, 0, 0],
    [2, 2, 4, 4],
    [2, 4, 1, 5],
]


def build(instance):
    price = instance["price"]
    limits = instance["limits"]           # minimum requirement per nutrient

    m = Model()
    # Units of each food bought. Upper bound is the largest requirement, so the
    # domain stays finite for any instance.
    ub = max(limits)
    x = m.int_vector("food", len(price), 0, ub)

    # Each nutrient must reach at least its requirement.
    for i, row in enumerate(NUTRIENTS):
        m &= (sum(row[j] * x[j] for j in range(len(price))) >= limits[i])

    # Minimise the total cost of the diet.
    cost = sum(price[j] * x[j] for j in range(len(price)))
    m.obj += cost

    return m, {"cost": cost}
