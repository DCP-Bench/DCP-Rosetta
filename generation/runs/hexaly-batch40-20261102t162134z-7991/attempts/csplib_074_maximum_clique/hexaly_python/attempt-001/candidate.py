"""Maximum clique: the largest set of vertices of which every two are adjacent."""
import hexaly.optimizer as hx


def build(instance):
    n, adj = instance["n"], instance["adj"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # c[i] = 1 if vertex i is in the clique
    c = [model.bool() for _ in range(n)]

    # Two vertices that are not adjacent are not both in the clique
    for i in range(n):
        for j in range(i + 1, n):
            if not adj[i][j]:
                model.constraint(c[i] + c[j] <= 1)

    # Maximise the size of the clique
    model.maximize(model.sum(c))
    return optimizer, {"c": c}
