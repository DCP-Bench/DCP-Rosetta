"""Birthday coins: Tommy was given 15 coins, each a half-crown (30 pence), a shilling (12 pence) or a
sixpence (6 pence), though not necessarily coins of all three kinds. Together they are worth
£1 5s 6d. How many half-crowns could he have been given?"""
import hexaly.optimizer as hx


def build(instance):
    # The instance has no fields: every number below is from the problem statement.
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # How many coins of each kind he was given: a kind may be absent (0), and no kind can
    # number more than the 15 coins.
    half_crowns = model.int(0, 15)
    shillings = model.int(0, 15)
    sixpences = model.int(0, 15)

    # He was given 15 coins.
    model.constraint(half_crowns + shillings + sixpences == 15)

    # They add up to £1 5s 6d = 240 + 5 * 12 + 6 = 306 pence; a half-crown is 30 pence, a
    # shilling 12 and a sixpence 6.
    model.constraint(30 * half_crowns + 12 * shillings + 6 * sixpences == 306)

    return optimizer, {"half_crowns": half_crowns}
