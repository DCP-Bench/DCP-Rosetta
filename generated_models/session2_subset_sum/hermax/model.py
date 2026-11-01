from hermax.model import Model


def build(instance):
    coins = instance["coin_numbers"]
    total = instance["total_coins_lost"]
    n = len(coins)

    m = Model()
    # One count per bag type: how many bags of that type were stolen.
    # A type cannot contribute more bags than fit in the total.
    bags = m.int_vector("bags", n, 0, total)
    counts = []
    for i in range(n):
        ub = total // coins[i]
        # Channel each count to bits, then write the weighted sum over the
        # bits. Weighted sums over IntVars with coefficients this size are
        # slow to encode; the bits form is cheap.
        bits = m.bool_vector(f"bag_bit{i}", max(ub, 1).bit_length())
        expr = sum(2 ** k * bits[k] for k in range(len(bits)))
        m &= (bags[i] == expr)
        m &= (bags[i] <= ub)
        counts.append(expr)

    # The stolen bags hold exactly the lost number of coins.
    m &= (sum(coins[i] * counts[i] for i in range(n)) == total)

    return m, {"bags": bags}
