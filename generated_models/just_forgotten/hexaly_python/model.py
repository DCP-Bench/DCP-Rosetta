"""Just forgotten: the account number uses each digit 0..n-1 once, and every tried set has exactly the
given number of digits in their correct positions."""
import hexaly.optimizer as hx


def build(instance):
    sets, correct = instance["sets"], instance["num_correct_digits"]
    n = len(sets[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # digit_at[k][d] = 1 if position k of the account number holds digit d: a permutation
    digit_at = [[model.bool() for _ in range(n)] for _ in range(n)]
    for k in range(n):
        model.constraint(model.sum(digit_at[k]) == 1)
    for d in range(n):
        model.constraint(model.sum(digit_at[k][d] for k in range(n)) == 1)

    # In every tried set, exactly `correct` digits are in their correct position
    for tried in sets:
        model.constraint(model.sum(digit_at[k][tried[k]] for k in range(n)) == correct)

    x = [model.sum(d * digit_at[k][d] for d in range(n)) for k in range(n)]
    return optimizer, {"x": x}
