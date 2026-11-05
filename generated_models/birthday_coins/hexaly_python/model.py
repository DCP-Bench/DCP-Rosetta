"""Birthday coins: 15 coins of half-crowns (30 pence), shillings (12) and sixpences (6) worth 1 pound 5s 6d."""
import hexaly.optimizer as hx

TOTAL_PENCE = 20 * 12 + 5 * 12 + 6  # 1 pound is 240 pence, 5 shillings are 60 pence, plus 6 pence


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # He was given some of each of the three kinds of coin, 15 coins in all
    half_crowns, shillings, sixpences = (model.int(1, 15) for _ in range(3))
    model.constraint(half_crowns + shillings + sixpences == 15)
    # A half-crown is 30 pence, a shilling 12 and a sixpence 6; together they make 306 pence
    model.constraint(30 * half_crowns + 12 * shillings + 6 * sixpences == TOTAL_PENCE)

    return optimizer, {"half_crowns": half_crowns}
