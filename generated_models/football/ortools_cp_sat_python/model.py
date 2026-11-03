# football: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install ortools`) with:
#   python football.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Buy football players from four groups (goalkeepers, defenders, midfielders and strikers)
    so that the total price is as close as possible to the GBP 30 million limit without going
    over it. At least the required number of players is bought from each group, and at least
    eleven players in total."""
    budget = 30000  # the most that may be spent, in GBP thousands

    # prices[g][p]: the price of player p of group g
    prices = [
        [730, 1280, 3880],                                             # goalkeepers
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],               # defenders
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],  # midfielders
        [4460, 6470, 7780, 8390, 9500],                                # strikers
    ]
    # n_fewest[g] and n_most[g]: the fewest and the most players to buy from group g. Goalkeepers
    # are exactly 1; the most for the other groups is the size of the group.
    n_fewest = [1, 2, 3, 2]
    n_most = [1] + [len(group) for group in prices[1:]]
    n_min_players = 11  # the fewest players in the squad

    model = cp_model.CpModel()

    # buy[g][p] is true when player p of group g is bought
    buy = [[model.new_bool_var(f"buy_{g}_{p}") for p in range(len(group))]
           for g, group in enumerate(prices)]

    # z is the total price of the players bought, in GBP thousands; it stays within the budget
    z = model.new_int_var(0, budget, "z")

    # Each group supplies between its fewest and its most players.
    for g in range(len(prices)):
        model.add(sum(buy[g]) >= n_fewest[g])
        model.add(sum(buy[g]) <= n_most[g])

    # The squad has at least that many players in total.
    model.add(sum(sum(group) for group in buy) >= n_min_players)

    # Each bought player adds their price to z.
    model.add(z == sum(price * bought
                       for group_prices, group_buy in zip(prices, buy)
                       for price, bought in zip(group_prices, group_buy)))

    # Spend as much as possible.
    model.maximize(z)

    return model, {"z": z}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
