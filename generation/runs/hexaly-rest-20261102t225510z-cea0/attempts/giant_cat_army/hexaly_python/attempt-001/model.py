"""Giant cat army: a list of 24 distinct integers from 0 to 60, starting at 0 and ending at 14, each term the previous
plus 5, plus 7 or its square root, with 2 and 10 appearing in that order before 14."""
import hexaly.optimizer as hx

LENGTH = 24
LIMIT = 60


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    x = [model.int(0, LIMIT) for _ in range(LENGTH)]
    model.constraint(x[0] == 0)
    model.constraint(x[LENGTH - 1] == 14)

    # Each term follows from the previous one by adding 5, adding 7 or taking the (whole) square root
    for t in range(LENGTH - 1):
        model.constraint(model.or_(x[t + 1] == x[t] + 5, x[t + 1] == x[t] + 7, x[t] == x[t + 1] * x[t + 1]))
    # All the terms are different
    for a in range(LENGTH):
        for b in range(a + 1, LENGTH):
            model.constraint(x[a] != x[b])
    # 2 and 10 appear in that order (14 is the last term)
    terms = model.array(x)
    at_two = model.int(1, LENGTH - 1)
    at_ten = model.int(1, LENGTH - 1)
    model.constraint(model.at(terms, at_two) == 2)
    model.constraint(model.at(terms, at_ten) == 10)
    model.constraint(at_two < at_ten)

    return optimizer, {"x": x}
