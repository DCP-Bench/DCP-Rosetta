"""Divisible by 1 through 9: a 10-digit number using each digit 0..9 once whose first n digits are divisible by n."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # is_digit[p][d] = 1 if the digit in place p (counted from the left) is d. Booleans with linear sums let
    # Hexaly treat "each digit once" and the divisibility rules as one linear system, which it can also prove
    # things about (that no second number exists).
    is_digit = [[model.bool() for _ in range(10)] for _ in range(10)]
    for place in range(10):
        model.constraint(model.sum(is_digit[place]) == 1)   # one digit per place
    for d in range(10):
        model.constraint(model.sum(is_digit[place][d] for place in range(10)) == 1)   # each digit used once
    digits = [model.sum(d * is_digit[place][d] for d in range(10)) for place in range(10)]

    # The first n digits form a number divisible by n, so it is n times a whole quotient. The number of the first
    # n digits is ten times the number of the first n - 1 digits plus digit n, and that number is (n - 1) times
    # its own quotient, which keeps every rule a linear equation: n * quotient[n] = 10 * (n - 1) * quotient[n - 1] + digit n
    quotient = {1: digits[0]}   # the first digit is divisible by 1: it is its own quotient
    for n in range(2, 11):
        quotient[n] = model.int(0, 10 ** n // n)
        model.constraint(n * quotient[n] == 10 * (n - 1) * quotient[n - 1] + digits[n - 1])

    return optimizer, {"digits": digits}
