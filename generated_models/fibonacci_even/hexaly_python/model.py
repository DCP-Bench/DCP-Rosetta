"""Fibonacci even: the sum of the even-valued Fibonacci terms (starting 1, 2) that do not exceed four million."""
import hexaly.optimizer as hx

LIMIT = 4_000_000
TERMS = 40  # the terms grow past four million long before the 40th


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # fib[i] is the i-th term: it starts 1, 2 and each later term is the sum of the previous two
    fib = [model.int(1, 10 ** 9) for _ in range(TERMS)]
    model.constraint(fib[0] == 1)
    model.constraint(fib[1] == 2)
    for i in range(2, TERMS):
        model.constraint(fib[i] == fib[i - 1] + fib[i - 2])

    # The sum of the even terms that do not exceed the limit
    res = model.sum(model.iif(model.and_(f % 2 == 0, f <= LIMIT), f, 0) for f in fib)
    return optimizer, {"res": res}
