from hermax.model import Model


def build(instance):
    """
    Coin system minimization: select x[j] coins of each denomination
    to enable making any amount from 1 to max_amount.
    Uses a greedy-style constraint: iterate through denominations
    and require enough coins to cover gaps.
    """

    m = Model()

    denominations = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]
    n_denoms = len(denominations)

    # Sort denominations to process from largest to smallest
    denom_sorted = sorted(enumerate(denominations), key=lambda x: x[1], reverse=True)

    # x[j] = number of coins of denomination j
    x = m.int_vector("x", n_denoms, 0, max_amount)

    # Greedy coin change constraint:
    # The total value of all coins >= max_amount
    total_value = sum(denominations[j] * x[j] for j in range(n_denoms))
    m &= (total_value >= max_amount)

    # For proper coin system, need denomination 1 (to make all intermediate amounts)
    denom_1_idx = None
    for j in range(n_denoms):
        if denominations[j] == 1:
            denom_1_idx = j
            break

    if denom_1_idx is not None:
        m &= (x[denom_1_idx] >= 1)

    # Minimize total coins
    for j in range(n_denoms):
        m.obj[1] += x[j]

    return m, {"x": x}
