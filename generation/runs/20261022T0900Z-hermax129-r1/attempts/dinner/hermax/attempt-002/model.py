from hermax.model import Model


def build(instance):
    # Dinner problem: find how many grandparents, parents, and children go to dinner.
    # This problem has no instance fields - all constants come from the problem specification.

    m = Model()

    # Decision variables with problem-specified ranges.
    # Grandparents: 1-6, cost $3 each
    # Parents: 1-10, cost $2 each
    # Children: 1-40, cost $0.50 each
    grandparents = m.int("grandparents", 1, 6)
    parents = m.int("parents", 1, 10)
    children = m.int("children", 1, 40)

    # Total must be 20 people.
    m &= (grandparents + parents + children == 20)

    # Total cost must be $20. Multiply by 2 to avoid decimals:
    # 3*grandparents + 2*parents + 0.5*children = 20 becomes
    # 6*grandparents + 4*parents + 1*children = 40
    m &= (6 * grandparents + 4 * parents + children == 40)

    return m, {
        "grandparents": grandparents,
        "parents": parents,
        "children": children
    }
