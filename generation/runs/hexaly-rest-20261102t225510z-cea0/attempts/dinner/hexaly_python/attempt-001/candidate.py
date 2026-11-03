"""Dinner: how many grandparents, parents and children go out so that 20 people pay exactly $20."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # 1 to 6 grandparents, 1 to 10 parents and 1 to 40 children
    grandparents = model.int(1, 6)
    parents = model.int(1, 10)
    children = model.int(1, 40)

    # 20 people in all
    model.constraint(grandparents + parents + children == 20)
    # They pay $20: $3 per grandparent, $2 per parent and $0.50 per child, doubled to stay in integers
    model.constraint(6 * grandparents + 4 * parents + children == 40)

    return optimizer, {"grandparents": grandparents, "parents": parents, "children": children}
