# football: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install pulp numpy`) with:
#   python football.py

import pulp


def create_model(instance):
    """Buy football players from four groups (goalkeepers, defenders, midfielders and strikers)
    so that the total price is as close as possible to GBP 30 million without going over it.
    At least the required number of players is bought from each group, and at least eleven
    players in all."""
    budget = 30000  # GBP 30 million, in thousands of GBP

    # prices[g][p]: the price of player p of group g, in thousands of GBP
    prices = [
        [730, 1280, 3880],                                              # goalkeepers
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],                # defenders
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],   # midfielders
        [4460, 6470, 7780, 8390, 9500],                                 # strikers
    ]
    # fewest[g] and most[g]: the fewest and the most players to buy from group g. There must be
    # exactly one goalkeeper, and the most from any other group is the size of that group.
    fewest = [1, 2, 3, 2]
    most = [1] + [len(group) for group in prices[1:]]
    min_players = 11  # the fewest players in all

    problem = pulp.LpProblem("football", pulp.LpMaximize)

    # buy[g][p] is 1 when player p of group g is bought, and 0 when not
    buy = [[pulp.LpVariable(f"buy_{g}_{p}", cat="Binary") for p in range(len(group))]
           for g, group in enumerate(prices)]

    # Each group supplies between its fewest and its most players.
    for g in range(len(prices)):
        problem += pulp.lpSum(buy[g]) >= fewest[g]
        problem += pulp.lpSum(buy[g]) <= most[g]

    # At least eleven players are bought in all.
    problem += pulp.lpSum(var for group in buy for var in group) >= min_players

    # z is the total price of the players bought, in thousands of GBP, and it stays within the budget.
    z = pulp.LpVariable("z", 0, budget, cat="Integer")
    problem += z == pulp.lpSum(prices[g][p] * buy[g][p]
                               for g in range(len(prices)) for p in range(len(prices[g])))

    # Spend as much as possible.
    problem += z

    return problem, {"z": z}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
