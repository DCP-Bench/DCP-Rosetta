"""Guards and apples: at each gate the boy gives the guard half his apples plus one; after the last gate
he has the one apple he gives the girl."""
import hexaly.optimizer as hx


def build(instance):
    gates = instance["num_gates"]
    # Working back from 1 apple, the count before a gate is 2 * (after + 1), so at most
    # 3 * 2^gates - 2; that bounds every count
    top = 3 * 2 ** gates
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # apples[i] is the number of apples before gate i; apples[gates] is the number after the last gate
    apples = [model.int(0, top) for _ in range(gates + 1)]
    for i in range(gates):
        # He hands over a whole number of apples: half of an even count, plus one
        half = model.int(0, top)
        model.constraint(apples[i] == 2 * half)
        model.constraint(apples[i + 1] == apples[i] - (half + 1))
    # After the last gate he has the one apple for the girl, and none once he has given it
    model.constraint(apples[gates] == 1)

    return optimizer, {"apples": apples}
