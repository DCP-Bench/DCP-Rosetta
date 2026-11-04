# football: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install exact numpy`) with:
#   python football.py

from exact import Exact


def create_model(instance):
    """Buy football players from four groups (goalkeepers, defenders, midfielders and strikers), so
    that the total price is as close as possible to GBP 30 million without going over it. The squad
    takes at least the required number from each group, and at least eleven players in total."""
    budget = 30000  # the most that may be spent, in GBP thousands
    # prices[g][p]: the price in GBP thousands of player p of group g, one list per group
    prices = [
        [730, 1280, 3880],
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
        [4460, 6470, 7780, 8390, 9500],
    ]
    # n_fewest[g] and n_most[g]: the fewest and the most players to buy from group g. Exactly one
    # goalkeeper; two or more defenders; three or more midfielders; two or more strikers. The most
    # from each group is the whole group, except goalkeepers.
    n_fewest = [1, 2, 3, 2]
    n_most = [1] + [len(group) for group in prices[1:]]
    n_min_players = 11  # the fewest players in the squad in total

    solver = Exact()

    # Exact identifies its variables by name.
    # buy[g][p] is 1 when player p of group g is bought, and 0 when not
    buy = [[f"buy_{g}_{p}" for p in range(len(group))] for g, group in enumerate(prices)]
    for row in buy:
        for name in row:
            solver.addVariable(name, 0, 1)
    # z is the total price of the players bought, in GBP thousands; it stays within the budget
    solver.addVariable("z", 0, budget)

    # Each group supplies between its fewest and its most players.
    for g in range(len(prices)):
        solver.addConstraint([(1, name) for name in buy[g]], True, n_fewest[g],
                             True, n_most[g])

    # The squad has at least eleven players in total.
    solver.addConstraint([(1, name) for row in buy for name in row], True, n_min_players)

    # priced: the price of each player, paired with the variable that says whether they are bought
    priced = [(price, buy[g][p]) for g, group in enumerate(prices) for p, price in enumerate(group)]
    # z is the total price of the players bought.
    solver.addConstraint(priced + [(-1, "z")], True, 0, True, 0)

    # Spend as much as possible.
    solver.setObjective([(1, "z")], minimize=False)

    return solver, {"z": "z"}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
