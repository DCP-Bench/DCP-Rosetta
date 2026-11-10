"""Curious set of integers: a number that can join {1, 3, 8, 120} so that every product of two members is one
less than a perfect square."""
import hexaly.optimizer as hx

SET = [1, 3, 8, 120]  # the set the problem statement gives


def build(instance):
    top = instance["max_val"]  # the largest value the new number may take
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    number = model.int(0, top)  # the number to add to the set

    # The product of the new number with each member, plus 1, is a perfect square
    for member in SET:
        root = model.int(1, int((member * top + 1) ** 0.5) + 1)  # the square root of the product plus 1
        model.constraint(member * number + 1 == root * root)

    return optimizer, {"number": number}
