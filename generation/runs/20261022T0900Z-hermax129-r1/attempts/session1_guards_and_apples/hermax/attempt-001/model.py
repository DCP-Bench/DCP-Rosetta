from hermax.model import Model


def build(instance):
    num_gates = instance["num_gates"]

    # apples[i] is the number of apples before gate i; apples[num_gates] is what is left at the end.
    m = Model()
    # Working backwards, each gate doubles the count and adds two, so the largest count
    # (before the first gate) is 3 * 2**num_gates - 2.
    upper = 3 * 2 ** num_gates - 2
    apples = m.int_vector("apples", num_gates + 1, 0, upper)

    # After the last gate he has one apple left, which he gives to the girl, leaving none.
    m &= (apples[num_gates] == 1)

    for i in range(num_gates):
        # Each guard gets half of his apples plus one, and the number must be an integer,
        # so apples[i] is even and the bribe is apples[i] / 2 + 1.
        # What remains after the bribe is apples[i] / 2 - 1, which is the count before the next gate.
        # Equivalently apples[i] == 2 * apples[i + 1] + 2.
        m &= (apples[i] == 2 * apples[i + 1] + 2)

    return m, {"apples": apples}
