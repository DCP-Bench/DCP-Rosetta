from hermax.model import Model


def build(instance):
    packs = instance["packs"]
    target = instance["target"]
    n = len(packs)

    m = Model()
    # counts[i] is the number of packs of size packs[i] bought.
    # An optimal solution never buys more than target // packs[i] + 1 packs of
    # one size: removing one such pack would still meet the target.
    bounds = [target // packs[i] + 1 for i in range(n)]
    counts = [m.int(f"count_{i}", 0, bounds[i]) for i in range(n)]

    # Channel each count to binary digits, so the weighted sums below run over
    # Booleans with small weights.
    bit_values = []
    for i in range(n):
        k_bits = bounds[i].bit_length()
        bits = m.bool_vector(f"bit_{i}", k_bits)
        value = sum(2 ** k * bits[k] for k in range(k_bits))
        m &= (counts[i] == value)
        bit_values.append(value)

    # The packs bought meet or exceed the target.
    m &= (sum(packs[i] * bit_values[i] for i in range(n)) >= target)

    # Minimise the total beers bought, which is the excess over the target.
    m.obj += sum(packs[i] * counts[i] for i in range(n))

    return m, {"counts": counts}
