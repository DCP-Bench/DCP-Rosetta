"""Three sum: select m of the numbers so that they add up to zero."""
import hexaly.optimizer as hx


def build(instance):
    nums, m = instance["nums"], instance["m"]  # nums[i] = the i-th integer of the collection; m = how many elements must be selected
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # indices[i] = 1 if the element nums[i] is selected
    indices = [model.bool() for _ in nums]

    # Exactly m elements are selected
    model.constraint(model.sum(indices) == m)
    # The selected elements sum to zero (each nums[i] counts once if indices[i] = 1, otherwise not at all)
    model.constraint(model.sum(x * s for x, s in zip(nums, indices)) == 0)

    return optimizer, {"indices": indices}
