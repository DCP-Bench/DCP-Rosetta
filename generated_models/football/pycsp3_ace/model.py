# football: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python football.py

from pycsp3 import *


def create_model(instance):
    """Buy players with a total price as close as possible to, without going over,
    the chairman's limit of GBP 30 million: one goalkeeper, at least two defenders,
    at least three midfielders, at least two strikers, and at least eleven players
    in all. Find the total price of the players bought, in GBP thousands."""
    # The prices as the statement lists them, in GBP thousands (0.73 million is 730) because the output is asked in thousands.
    goalkeeper_prices = [730, 1280, 3880]  # g1, g2, g3
    defender_prices = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]  # d1 to d8
    midfielder_prices = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]  # m1 to m10
    striker_prices = [4460, 6470, 7780, 8390, 9500]  # s1 to s5

    # The chairman's upper limit on the total price, in GBP thousands.
    budget = 30000
    # The fewest players that must be bought in all.
    min_players = 11

    # buy_goalkeeper[i] is 1 when goalkeeper g(i + 1) is bought.
    buy_goalkeeper = VarArray(size=len(goalkeeper_prices), dom={0, 1})
    # buy_defender[i] is 1 when defender d(i + 1) is bought.
    buy_defender = VarArray(size=len(defender_prices), dom={0, 1})
    # buy_midfielder[i] is 1 when midfielder m(i + 1) is bought.
    buy_midfielder = VarArray(size=len(midfielder_prices), dom={0, 1})
    # buy_striker[i] is 1 when striker s(i + 1) is bought.
    buy_striker = VarArray(size=len(striker_prices), dom={0, 1})
    # total_price is the total price of the players bought, in GBP thousands; its domain stops at the budget, so it never goes over.
    total_price = Var(dom=range(budget + 1))

    satisfy(
        # Exactly one goalkeeper is bought.
        Sum(buy_goalkeeper) == 1,
        # At least two defenders are bought.
        Sum(buy_defender) >= 2,
        # At least three midfielders are bought.
        Sum(buy_midfielder) >= 3,
        # At least two strikers are bought.
        Sum(buy_striker) >= 2,
        # At least eleven players are bought in total.
        Sum(buy_goalkeeper) + Sum(buy_defender) + Sum(buy_midfielder) + Sum(buy_striker) >= min_players,
        # The total price is the sum of the prices of the players bought.
        total_price == Sum(price * bought for price, bought in zip(goalkeeper_prices, buy_goalkeeper))
        + Sum(price * bought for price, bought in zip(defender_prices, buy_defender))
        + Sum(price * bought for price, bought in zip(midfielder_prices, buy_midfielder))
        + Sum(price * bought for price, bought in zip(striker_prices, buy_striker)),
    )

    # Spend as much of the budget as possible.
    maximize(total_price)

    return {"z": total_price}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
