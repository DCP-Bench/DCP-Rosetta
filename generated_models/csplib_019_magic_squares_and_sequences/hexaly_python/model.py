"""Magic sequence: x_0..x_{n-1} in 0..n-1 where each value i occurs exactly x_i times in the sequence."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # length of the sequence; its entries x_j are values between 0 and n - 1
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # takes[j][v] = 1 if entry x_j of the sequence equals v. This one-hot choice of each entry's value
    # makes "how often does value i occur" a linear sum of Booleans.
    takes = [[model.bool() for _ in range(n)] for _ in range(n)]
    # Each entry x_j takes exactly one value
    for j in range(n):
        model.constraint(model.sum(takes[j]) == 1)
    # x[j] = the value of entry j of the sequence: the v for which takes[j][v] = 1
    x = [model.sum(v * takes[j][v] for v in range(n)) for j in range(n)]

    # The value i occurs exactly x_i times, for each i from 0 to n - 1
    for i in range(n):
        model.constraint(model.sum(takes[j][i] for j in range(n)) == x[i])
    # Implied by the definition, added to help the search: the n entries are counted once each, so the
    # counts x_i add up to n; and the entries add up to n as well, which written value by value
    # (value i occurs x_i times) is the sum of i * x_i
    model.constraint(model.sum(x) == n)
    model.constraint(model.sum(i * x[i] for i in range(n)) == n)

    return optimizer, {"x": x}
