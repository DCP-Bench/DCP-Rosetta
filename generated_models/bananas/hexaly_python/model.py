"""Bananas: 100 fruits for exactly 100 dollars, some of every kind, with as few bananas and apples as possible."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Quantities bought; each fruit is bought at least once
    bananas, oranges, mangoes, apples = (model.int(1, 100) for _ in range(4))

    # 100 fruits
    model.constraint(bananas + oranges + mangoes + apples == 100)
    # 100 dollars: 5 bananas cost 3, 7 oranges 5, 9 mangoes 7 and 3 apples 9, so a banana costs
    # 3/5, an orange 5/7, a mango 7/9 and an apple 3 dollars. Multiplying by 5 * 7 * 9 = 315
    # keeps the equation in integers.
    model.constraint(189 * bananas + 225 * oranges + 245 * mangoes + 945 * apples == 100 * 315)

    # The buyer dislikes bananas and apples: buy as few of them as possible
    model.minimize(bananas + apples)
    return optimizer, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}
