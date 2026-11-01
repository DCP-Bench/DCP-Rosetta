from hermax.model import Model


def build(instance):
    n = instance["n"]
    c = instance["c"]

    m = Model()

    # x[i][j] is 1 if there's a coin at position (i,j), 0 otherwise
    x = m.int_matrix("x", n, n, 0, 1)

    # Each row must have exactly c coins
    for i in range(n):
        m &= (sum(x.row(i)) == c)

    # Each column must have exactly c coins
    for j in range(n):
        m &= (sum(x.col(j)) == c)

    # Objective: minimize sum of squared horizontal distance from main diagonal
    # Distance from diagonal for position (i,j) is (i - j)^2
    # Use linear expression: sum of distances weighted by coin placement
    total_distance_sq = sum((i - j) ** 2 * x[i][j] for i in range(n) for j in range(n))

    # We need to return z as an output, but for the objective we use the expression directly
    # Create z as the same expression for output
    z = total_distance_sq
    m.obj += z

    return m, {"x": x, "z": z}
