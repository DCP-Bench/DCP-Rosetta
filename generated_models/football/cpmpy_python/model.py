# football: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install cpmpy`) with:
#   python football.py

import cpmpy as cp


def create_model(instance):
    """Buy football players from four groups (goalkeepers, defenders, midfielders, strikers)
    so that the total price is as close as possible to the 30 million GBP limit without going
    over it, buying at least the required number from each group and at least eleven players
    in total."""
    # The price list and the purchase rules are the problem statement itself (the instance has
    # no fields). Prices are in thousands of GBP, so that they are integers.
    budget = 30000
    prices = [
        [730, 1280, 3880],                                              # goalkeepers
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],                # defenders
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],   # midfielders
        [4460, 6470, 7780, 8390, 9500],                                 # strikers
    ]
    # Number of players to buy in each group: goalkeepers exactly 1, defenders at least 2,
    # midfielders at least 3, strikers at least 2 (the upper limit is the size of the group).
    min_buy = [1, 2, 3, 2]
    max_buy = [1] + [len(group) for group in prices[1:]]
    min_total = 11  # at least eleven players in total

    # buy[g][p] is true when player p of group g is bought
    buy = [cp.boolvar(shape=len(group), name=f"buy{g}") for g, group in enumerate(prices)]

    # z is the total price of the players bought, in thousands of GBP.
    z = cp.intvar(0, budget, name="z")

    model = cp.Model()

    # Each group supplies between its minimum and its maximum number of players.
    for g in range(len(prices)):
        model.add(cp.sum(buy[g]) >= min_buy[g])
        model.add(cp.sum(buy[g]) <= max_buy[g])

    # At least eleven players are bought in total.
    model.add(cp.sum([cp.sum(group) for group in buy]) >= min_total)

    # z is the total price of the bought players; the domain of z keeps it within the budget.
    model.add(z == cp.sum([cp.sum(buy[g] * prices[g]) for g in range(len(prices))]))

    # Spend as much as possible: the total price should be as close to the budget as it can get.
    model.maximize(z)

    return model, {"z": z}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
