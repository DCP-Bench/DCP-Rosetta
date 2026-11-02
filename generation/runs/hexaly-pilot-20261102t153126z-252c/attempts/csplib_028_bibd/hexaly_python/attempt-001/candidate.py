"""BIBD: a v x b 0/1 incidence matrix with r ones per row, k per column, and every two rows sharing exactly l ones."""
import hexaly.optimizer as hx


def build(instance):
    v, b, r, k, l = instance["v"], instance["b"], instance["r"], instance["k"], instance["l"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # matrix[i][j] = 1 if object i is in block j
    matrix = [[model.bool() for _ in range(b)] for _ in range(v)]

    # Each object occurs in exactly r blocks
    for i in range(v):
        model.constraint(model.sum(matrix[i]) == r)
    # Each block contains exactly k objects
    for j in range(b):
        model.constraint(model.sum(matrix[i][j] for i in range(v)) == k)
    # Every two distinct objects occur together in exactly l blocks (scalar product of their rows)
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            model.constraint(model.sum(matrix[i1][j] * matrix[i2][j] for j in range(b)) == l)

    return optimizer, {"matrix": matrix}
