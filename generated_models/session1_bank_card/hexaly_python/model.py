"""Bank card: a four-digit PIN abcd with no repeated digit, where cd is 3 times ab and da is 2 times bc."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Every digit starts one of the two-digit numbers ab, bc, cd and da, so none of them is zero
    digits = [model.int(1, 9) for _ in range(4)]
    a, b, c, d = digits

    # No two digits are the same
    for x in range(4):
        for y in range(x + 1, 4):
            model.constraint(digits[x] != digits[y])
    # The 2-digit number cd is 3 times the 2-digit number ab
    model.constraint(10 * c + d == 3 * (10 * a + b))
    # The 2-digit number da is 2 times the 2-digit number bc
    model.constraint(10 * d + a == 2 * (10 * b + c))

    return optimizer, {"a": a, "b": b, "c": c, "d": d}
