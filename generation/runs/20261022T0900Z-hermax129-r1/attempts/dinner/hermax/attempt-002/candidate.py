from hermax.model import Model


def build(instance):
    # Dinner problem: find how many grandparents, parents, and children go to dinner
    # Constraints:
    # - 1-6 grandparents, 1-10 parents, 1-40 children
    # - Total 20 people
    # - Total cost $20 (grandparents $3, parents $2, children $0.50)

    m = Model()

    # Decision variables
    grandparents = m.int("grandparents", 1, 6)
    parents = m.int("parents", 1, 10)
    children = m.int("children", 1, 40)

    # Total 20 people
    m &= (grandparents + parents + children == 20)

    # Total cost $20 - multiply by 2 to avoid decimals:
    # 3*grandparents + 2*parents + 0.5*children = 20
    # 6*grandparents + 4*parents + 1*children = 40
    m &= (6 * grandparents + 4 * parents + children == 40)

    return m, {
        "grandparents": grandparents,
        "parents": parents,
        "children": children
    }
