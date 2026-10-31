from hermax.model import Model


def build(instance):
    """
    Dinner puzzle: find how many grandparents, parents, and children
    go to dinner given cost and total count constraints.
    - Total people: 20
    - Total cost: $20
    - Grandparents: $3 each, 1-6
    - Parents: $2 each, 1-10
    - Children: $0.50 each, 1-40
    """

    m = Model()

    # Variables
    grandparents = m.int("grandparents", 1, 6)
    parents = m.int("parents", 1, 10)
    children = m.int("children", 1, 40)

    # Constraint: total 20 people
    m &= (grandparents + parents + children == 20)

    # Constraint: total $20 cost
    # 3*g + 2*p + 0.5*c = 20
    # Multiply by 2 to avoid fractions: 6*g + 4*p + c = 40
    m &= (6 * grandparents + 4 * parents + children == 40)

    return m, {
        "grandparents": grandparents,
        "parents": parents,
        "children": children,
    }
