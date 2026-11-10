"""Abbot's puzzle: 100 bushels of corn go to 100 people; a man gets 3, a woman 2, a child half a bushel,
and there are five times as many women as men."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The numbers of men, women and children, at most 100 people in all
    men, women, children = (model.int(0, 100) for _ in range(3))

    # 100 people
    model.constraint(men + women + children == 100)
    # 100 bushels: 3 per man, 2 per woman, half per child, doubled to stay in integers
    model.constraint(6 * men + 4 * women + children == 200)
    # Five times as many women as men
    model.constraint(women == 5 * men)

    return optimizer, {"men": men, "women": women, "children": children}
