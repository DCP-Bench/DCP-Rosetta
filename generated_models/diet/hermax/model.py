from hermax.model import Model

# Nutrition per unit of each food, from the problem description.
# Rows: calories, chocolate (ounces), sugar (ounces), fat (ounces).
# Columns: chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
NUTRITION = [
    [400, 200, 150, 500],
    [3, 2, 0, 0],
    [2, 2, 4, 4],
    [2, 4, 1, 5],
]


def build(instance):
    price = instance["price"]
    limits = instance["limits"]
    n = len(price)

    # Whole units of each food, written as binary digits so every
    # weighted sum is a linear expression over Booleans.
    bits_needed = max(limits).bit_length()

    m = Model()
    bits = []
    for i in range(n):
        b = m.bool_vector(f"xb{i}", bits_needed)
        bits.append(sum(2 ** k * b[k] for k in range(bits_needed)))

    # Each nutrition type must reach at least its requirement.
    for j in range(len(limits)):
        m &= (sum(NUTRITION[j][i] * bits[i] for i in range(n)) >= limits[j])

    # Minimise the total price paid.
    m.obj += sum(price[i] * bits[i] for i in range(n))

    return m, {"cost": sum(price[i] * bits[i] for i in range(n))}
