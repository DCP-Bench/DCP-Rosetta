"""Devil's word: put a + or - before each number so that the signed numbers add up to the total.

The target total is 666 in the problem statement and is read from the instance.
"""
import hexaly.optimizer as hx


def build(instance):
    # arr[i]: the i-th integer of the array, in order; total: the sum the signed integers must reach
    arr, total = instance["arr"], instance["total"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # plus[i] = 1 if arr[i] gets a +, 0 if it gets a -
    plus = [model.bool() for _ in arr]
    # result[i] is arr[i] with its sign applied: 2 * plus[i] - 1 is +1 for a +, -1 for a -
    result = [(2 * p - 1) * value for p, value in zip(plus, arr)]

    # The signed numbers add up to the total
    model.constraint(model.sum(result) == total)
    return optimizer, {"result": result}
