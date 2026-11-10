# football: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install hermax`) with:
#   python football.py

from hermax.model import Model, sum_expr


def create_model(instance):
    """Buy a football squad from the players on offer so that the total price is as
    close to the GBP 30 million budget as possible without going over. The squad must
    contain a set number of players per position and at least eleven players in all.
    The output is the total price in GBP thousands."""
    # The instance has no fields: the players on offer are fixed by the statement, so
    # they are given here. Prices are in GBP thousands (3.769 million is 3769).
    budget = 30000  # the chairman's upper limit, in GBP thousands
    min_players = 11  # at least this many players in the squad

    # (position name, fewest players to buy, most players to buy or None for no limit, prices)
    positions = [
        ("goalkeeper", 1, 1, [730, 1280, 3880]),  # must buy exactly 1
        ("defender", 2, None, [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]),  # 2 or more
        ("midfielder", 3, None, [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]),  # 3 or more
        ("striker", 2, None, [4460, 6470, 7780, 8390, 9500]),  # 2 or more
    ]

    m = Model()

    # buys[p][j] is true when player j of position p is bought
    buys = [m.bool_vector(name, len(prices)) for name, _, _, prices in positions]

    # Each position's count of players bought lies within its limits.
    for bought, (_, fewest, most, _) in zip(buys, positions):
        m &= (sum(bought) >= fewest)
        if most is not None:
            m &= (sum(bought) <= most)

    # At least eleven players are bought in total.
    m &= (sum(sum(bought) for bought in buys) >= min_players)

    # The total price of the squad, in GBP thousands: each bought player's price.
    spent = sum_expr(price * buys[p][j]
                     for p, (_, _, _, prices) in enumerate(positions)
                     for j, price in enumerate(prices))

    # The squad costs no more than the budget.
    m &= (spent <= budget)

    # Spend as much of the budget as possible.
    m.obj += -spent

    # z is the total price of the squad, in GBP thousands.
    # The objective in the problem's terms: the total price spent, whose negation the solver minimises.
    return m, {"z": spent}, spent


if __name__ == "__main__":
    model, outputs, objective = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)
