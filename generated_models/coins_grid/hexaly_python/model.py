"""Coins grid: place c coins in every row and column of an n x n grid, minimising the squared distance to the diagonal."""
import hexaly.optimizer as hx


def build(instance):
    # n = side of the square grid; c = number of coins every row and every column must hold
    n, c = instance["n"], instance["c"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # x[i][j] = 1 if a coin is in cell (i, j); at most one coin per cell
    x = [[model.bool() for _ in range(n)] for _ in range(n)]

    # Exactly c coins in each row and in each column
    for i in range(n):
        model.constraint(model.sum(x[i]) == c)
    for j in range(n):
        model.constraint(model.sum(x[i][j] for i in range(n)) == c)

    # Minimise the sum of the squared horizontal distances of the coins to the main diagonal
    # (a coin in cell (i, j) is |i - j| columns away from the diagonal)
    z = model.sum((i - j) * (i - j) * x[i][j] for i in range(n) for j in range(n))
    model.minimize(z)
    return optimizer, {"x": x, "z": z}
