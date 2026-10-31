"""
Coin system: find minimum coin counts for any amount 1..max.

Use a computational approach: for each denomination, compute
the minimum count needed based on the set of denominations.
This uses a greedy/DP-inspired heuristic.
"""

from hermax.model import Model


def build(instance):
    m = Model()

    denominations = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]
    n = len(denominations)

    # x[i] = number of coins of denomination i
    # Heuristic: use amount/denomination rounded up as initial guess
    x = m.int_vector("x", n, 0, max_amount)

    # For the canonical denominations [1, 2, 5, 10, 20, 50]:
    # A simple strategy is to have enough of each:
    # - 1-cent: needed for amounts 1, 6, 11, 16, ... (amounts = 1 mod 5)
    # - 2-cent: helpful for even amounts
    # - 5-cent: covers multiples of 5
    # - etc.

    # Simpler approach: for each denomination d, we need at most
    # enough to "cover" the range [1, max]
    # A reasonable lower bound: for denomination d, need x[i] >= ceil(max / d)
    # But we can optimize by noting patterns

    for i in range(n):
        d = denominations[i]
        # Each denomination should have at least ceil(max / d) coins
        # to potentially cover the full range alone
        min_needed = (max_amount + d - 1) // d  # This is ceil(max / d)
        # But reduce by half since we have other denominations
        min_needed = max(1, min_needed // 2)
        m &= (x[i] >= min_needed)

    # Add objective to slightly prefer fewer coins (for small ranges)
    for i in range(n):
        # Small penalty for larger counts
        for k in range(10):
            m.obj[1] += (x[i] >= max_amount // 2 + k)

    return m, {"x": x}
