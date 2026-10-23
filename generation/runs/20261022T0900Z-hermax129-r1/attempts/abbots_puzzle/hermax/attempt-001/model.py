from hermax.model import Model


def build(instance):
    # The problem: 100 bushels of corn distributed among 100 people.
    # Each man gets 3 bushels, each woman gets 2 bushels, each child gets 0.5 bushels.
    # There are 5 times as many women as men.
    # Find the number of men, women, and children.

    # Constraints from problem description:
    # 1. men + women + children = 100
    # 2. 3*men + 2*women + 0.5*children = 100
    # 3. women = 5*men

    m = Model()

    # All quantities are non-negative integers.
    # From constraint 1, each can be at most 100.
    men = m.int("men", 0, 100)
    women = m.int("women", 0, 100)
    children = m.int("children", 0, 100)

    # Constraint: men + women + children = 100
    m &= (men + women + children == 100)

    # Constraint: women = 5*men
    m &= (women == 5 * men)

    # Constraint: 3*men + 2*women + 0.5*children = 100
    # Since 0.5*children must be an integer, children must be even.
    # We can multiply by 2 to avoid fractions:
    # 6*men + 4*women + children = 200
    m &= (6 * men + 4 * women + children == 200)

    return m, {"men": men, "women": women, "children": children}
