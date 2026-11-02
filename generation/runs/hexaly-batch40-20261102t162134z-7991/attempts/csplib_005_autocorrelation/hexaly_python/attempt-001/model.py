"""Low autocorrelation: a +1/-1 sequence of length n minimising the sum of squared periodic autocorrelations."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # bit[i] = 1 for +1 and 0 for -1; s[i] is the value of the i-th element of the sequence
    bit = [model.bool() for _ in range(n)]
    s = [2 * b - 1 for b in bit]

    # C_k = sum_i s_i * s_{(i+k) mod n}, the periodic autocorrelation at distance k
    c = [model.sum(s[i] * s[(i + k) % n] for i in range(n)) for k in range(1, n)]
    # Minimise E, the sum of the squared autocorrelations
    model.minimize(model.sum(ck * ck for ck in c))
    return optimizer, {"sequence": s}
