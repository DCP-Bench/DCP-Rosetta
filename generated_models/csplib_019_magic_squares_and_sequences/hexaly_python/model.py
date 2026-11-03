"""Magic sequence: x_0..x_{n-1} in 0..n-1 where each value i occurs exactly x_i times in the sequence."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # takes[j][v] = 1 if x_j equals v; Booleans with linear sums
    takes = [[model.bool() for _ in range(n)] for _ in range(n)]
    for j in range(n):
        model.constraint(model.sum(takes[j]) == 1)
    x = [model.sum(v * takes[j][v] for v in range(n)) for j in range(n)]

    # The value i occurs exactly x_i times
    for i in range(n):
        model.constraint(model.sum(takes[j][i] for j in range(n)) == x[i])
    # Implied: there are n occurrences in all, and the values add up to n (i occurs x_i times)
    model.constraint(model.sum(x) == n)
    model.constraint(model.sum(i * x[i] for i in range(n)) == n)

    return optimizer, {"x": x}
