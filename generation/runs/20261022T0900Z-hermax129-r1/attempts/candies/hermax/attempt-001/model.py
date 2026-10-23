from hermax.model import Model


def build(instance):
    # Extract instance data
    ratings = instance["ratings"]
    n = len(ratings)

    # Create model and variables
    m = Model()
    # Each child gets between 1 and n candies
    x = m.int_vector("candies", n, 1, n)

    # Constraint: if ratings[i] > ratings[i+1], then x[i] > x[i+1]
    # Equivalently: if ratings[i] > ratings[i+1], then x[i] >= x[i+1] + 1
    for i in range(n - 1):
        if ratings[i] > ratings[i + 1]:
            # Enforce: x[i] > x[i+1]
            m &= (x[i] > x[i + 1])
        elif ratings[i] < ratings[i + 1]:
            # Enforce: x[i] < x[i+1]
            m &= (x[i] < x[i + 1])
        # If ratings are equal, no constraint between x[i] and x[i+1]

    # Objective: minimize total candies
    total_candies = sum(x)
    m.obj += total_candies

    return m, {"x": x, "z": total_candies}
