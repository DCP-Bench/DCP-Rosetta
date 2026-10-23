from hermax.model import Model


def build(instance):
    values = instance["types_of_coins"]
    available = instance["available_coins"]
    amount = instance["amount"]
    n = len(values)

    m = Model()
    # coin_counts[j] is the number of coins of type j given to Bob.
    counts = m.int_vector("coin_count", n, 0, max(available))

    # Alice only has a limited number of each coin.
    for j in range(n):
        m &= (counts[j] <= available[j])

    # Channel each count to binary digits, so the weighted sum below stays cheap to encode.
    bit_sums = []
    for j in range(n):
        width = max(1, available[j].bit_length())
        bits = m.bool_vector(f"coin_bit{j}", width)
        expr = sum(2 ** k * bits[k] for k in range(width))
        m &= (counts[j] == expr)
        bit_sums.append(expr)

    # The coins given must add up to the amount of change.
    m &= (sum(values[j] * bit_sums[j] for j in range(n)) == amount)

    # Minimise the number of coins used.
    m.obj += sum(counts[j] for j in range(n))

    return m, {"coin_counts": counts}
