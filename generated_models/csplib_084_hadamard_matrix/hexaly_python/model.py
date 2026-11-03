"""Hadamard matrix Legendre pairs: +1/-1 sequences a, b of odd length l with PAF(A, s) + PAF(B, s) = -2 and sums 1."""
import hexaly.optimizer as hx


def build(instance):
    l = instance["l"]
    m = (l - 1) // 2
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # a[i], b[i] in {-1, +1}, written as 2 * bit - 1
    a = [2 * model.bool() - 1 for _ in range(l)]
    b = [2 * model.bool() - 1 for _ in range(l)]

    def paf(x, s):
        """Periodic autocorrelation of x at shift s."""
        return model.sum(x[i] * x[(i + s) % l] for i in range(l))

    # The m quadratic constraints
    for s in range(1, m + 1):
        model.constraint(paf(a, s) + paf(b, s) == -2)
    # The two linear constraints
    model.constraint(model.sum(a) == 1)
    model.constraint(model.sum(b) == 1)

    return optimizer, {"a": a, "b": b}
