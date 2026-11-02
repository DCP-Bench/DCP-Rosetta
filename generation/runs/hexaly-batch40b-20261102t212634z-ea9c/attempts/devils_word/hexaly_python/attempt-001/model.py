"""Devil's word: put a + or - before each number so that the signed numbers add up to the total."""
import hexaly.optimizer as hx


def build(instance):
    arr, total = instance["arr"], instance["total"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # plus[i] = 1 if arr[i] gets a +, 0 if it gets a -
    plus = [model.bool() for _ in arr]
    result = [(2 * p - 1) * value for p, value in zip(plus, arr)]

    # The signed numbers add up to the total
    model.constraint(model.sum(result) == total)
    return optimizer, {"result": result}
