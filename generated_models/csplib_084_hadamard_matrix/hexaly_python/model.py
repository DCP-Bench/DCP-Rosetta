"""Hadamard matrix Legendre pairs: +1/-1 sequences a, b of odd length l with PAF(A, s) + PAF(B, s) = -2 and sums 1."""
import hexaly.optimizer as hx


def build(instance):
    l = instance["l"]  # the odd length of each of the two sequences a and b
    m = (l - 1) // 2  # number of quadratic constraints, one per shift s = 1..m
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # a[i], b[i] = entry i of sequence A and of sequence B, each -1 or +1; a Boolean bit
    # gives the two values as 2 * bit - 1
    a = [2 * model.bool() - 1 for _ in range(l)]
    b = [2 * model.bool() - 1 for _ in range(l)]

    # paf(x, s) is the periodic autocorrelation of sequence x at shift s: the sum of x[i] * x[i + s],
    # with i + s taken mod l
    def paf(x, s):
        """Periodic autocorrelation of x at shift s."""
        return model.sum(x[i] * x[(i + s) % l] for i in range(l))

    # The m quadratic constraints: for every shift s from 1 to m, PAF(A, s) + PAF(B, s) = -2
    for s in range(1, m + 1):
        model.constraint(paf(a, s) + paf(b, s) == -2)
    # The two linear constraints: the entries of A add up to 1, and so do the entries of B
    model.constraint(model.sum(a) == 1)
    model.constraint(model.sum(b) == 1)

    return optimizer, {"a": a, "b": b}
