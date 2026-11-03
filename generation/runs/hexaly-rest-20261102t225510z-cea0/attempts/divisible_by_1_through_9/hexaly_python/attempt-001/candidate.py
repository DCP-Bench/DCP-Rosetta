"""Divisible by 1 through 9: a 10-digit number using each digit 0..9 once whose first n digits are divisible by n."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The digits, left to right: 0..9 each once (a full list decision); a 10-digit number has no leading zero
    perm = model.list(10)
    model.constraint(model.count(perm) == 10)
    digits = [perm[i] for i in range(10)]
    model.constraint(digits[0] >= 1)

    # prefix = the number formed by the first n digits; it is divisible by n
    prefix = digits[0]
    for n in range(2, 11):
        prefix = 10 * prefix + digits[n - 1]
        model.constraint(prefix % n == 0)

    return optimizer, {"number": prefix}
