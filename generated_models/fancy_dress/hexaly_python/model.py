"""Fancy dress: which green items Mr Greenguest wears, and whether he pays the entrance fee, at least cost."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # t tie, h hat, r shirt, s socks: 1 if worn in green; n = 1 if he pays the entrance fee
    t, h, r, s, n = (model.bool() for _ in range(5))

    # Rule 1: a green tie goes with a green shirt
    rule1 = model.or_(model.not_(t), r)
    # Rule 2: green socks and a green shirt only together with a green tie or a green hat
    rule2 = model.or_(model.not_(model.and_(s, r)), t, h)
    # Rule 3: a green shirt or a green hat, or not wearing green socks, requires a green tie
    rule3 = model.or_(model.not_(model.or_(r, h, model.not_(s))), t)
    # Rule 4: a guest not dressed according to rules 1-3 pays the entrance fee
    model.constraint(n == model.not_(model.and_(rule1, rule2, rule3)))

    # Cost: tie $10, hat $2, socks $12 and the $11 fee; the shirt is already owned, so it costs nothing
    model.minimize(10 * t + 2 * h + 12 * s + 11 * n)
    return optimizer, {"t": t, "h": h, "r": r, "s": s, "n": n}
