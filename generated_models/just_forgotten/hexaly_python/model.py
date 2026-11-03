"""Just forgotten: the account number uses each digit 0..n-1 once, and every tried set has exactly the
given number of digits in their correct positions.

Joe tried several sets of digits. In each set the same number of digits sit in their correct position
of the account number, and that is enough to work the number out.
"""
import hexaly.optimizer as hx


def build(instance):
    # sets[t][k]: the digit that tried set t has at position k
    # num_correct_digits: how many digits of every tried set are in their correct position
    sets, correct = instance["sets"], instance["num_correct_digits"]
    # the account number has as many digits as a tried set has positions, and uses each of 0..n-1 once
    n = len(sets[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # digit_at[k][d] = 1 if position k of the account number holds digit d: a permutation
    digit_at = [[model.bool() for _ in range(n)] for _ in range(n)]
    # Each position holds exactly one digit
    for k in range(n):
        model.constraint(model.sum(digit_at[k]) == 1)
    # Each digit from 0 to n-1 is used exactly once
    for d in range(n):
        model.constraint(model.sum(digit_at[k][d] for k in range(n)) == 1)

    # In every tried set, exactly `correct` digits are in their correct position
    for tried in sets:
        model.constraint(model.sum(digit_at[k][tried[k]] for k in range(n)) == correct)

    # x[k] is the digit at position k of the account number
    x = [model.sum(d * digit_at[k][d] for d in range(n)) for k in range(n)]
    return optimizer, {"x": x}
