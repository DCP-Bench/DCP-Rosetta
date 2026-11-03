"""Ages of the sons: three ages with product 36, a sum shared by another triple, and a single oldest son."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    def triple():
        """Three ages of product 36, from the oldest down."""
        ages = [model.int(1, 36) for _ in range(3)]  # the three ages, oldest first; none is more than 36
        model.constraint(ages[0] >= ages[1])
        model.constraint(ages[1] >= ages[2])
        model.constraint(ages[0] * ages[1] * ages[2] == 36)
        return ages

    ages = triple()
    # The sum of the ages was not enough to tell: another triple with product 36 has the same sum
    other = triple()
    model.constraint(model.or_(*[ages[i] != other[i] for i in range(3)]))
    model.constraint(model.sum(ages) == model.sum(other))
    # "The oldest son has blue eyes": there is one oldest son, so the two oldest ages differ
    model.constraint(ages[0] > ages[1])

    return optimizer, {"A1": ages[0], "A2": ages[1], "A3": ages[2]}
