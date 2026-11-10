"""Number partitioning: split 1..n into two sets of equal size with equal sums and equal sums of squares."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # the numbers 1 to n are split into two sets
    half = n // 2
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # set_a and set_b hold the numbers 0..n-1 standing for 1..n; together they split them all
    set_a, set_b = model.set(n), model.set(n)
    model.constraint(model.partition(set_a, set_b))
    # The sets have the same cardinality
    model.constraint(model.count(set_a) == half)

    # Equal sums, and equal sums of squares
    number = model.lambda_function(lambda i: i + 1)
    square = model.lambda_function(lambda i: (i + 1) * (i + 1))
    model.constraint(model.sum(set_a, number) == model.sum(set_b, number))
    model.constraint(model.sum(set_a, square) == model.sum(set_b, square))

    # The members of each set, in increasing order
    by_value = model.lambda_function(lambda i: i)
    sorted_a, sorted_b = model.sort(set_a, by_value), model.sort(set_b, by_value)
    return optimizer, {"A": [sorted_a[k] + 1 for k in range(half)],
                       "B": [sorted_b[k] + 1 for k in range(half)]}
