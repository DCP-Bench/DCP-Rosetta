"""Age changing: applying +2, /8, -3 and *7 in some order to my age gives my husband's age, and applying
them in a different order to his age gives mine."""
import hexaly.optimizer as hx

ADD, DIVIDE, SUBTRACT, MULTIPLY = range(4)  # the four operations; each step uses one, all four once


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    m = model.int(0, 2000)
    h = model.int(0, 2000)

    def chain(start, end):
        """Apply the four operations in an order of their own to start, reaching end; returns that order."""
        order = model.list(4)
        model.constraint(model.count(order) == 4)
        value = [start] + [model.int(0, 2000) for _ in range(3)] + [end]
        for k in range(4):
            before, after = value[k], value[k + 1]
            # The k-th operation: add 2, divide by 8 exactly, subtract 3 or multiply by 7
            model.constraint(model.or_(
                model.and_(order[k] == ADD, after == before + 2),
                model.and_(order[k] == DIVIDE, before == 8 * after),
                model.and_(order[k] == SUBTRACT, after == before - 3),
                model.and_(order[k] == MULTIPLY, after == 7 * before)))
        return order

    to_husband = chain(m, h)
    to_me = chain(h, m)
    # The two orders differ
    model.constraint(model.or_(*[to_husband[k] != to_me[k] for k in range(4)]))

    return optimizer, {"m": m, "h": h}
