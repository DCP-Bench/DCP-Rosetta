# football: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install pychoco numpy`) with:
#   python football.py

from pychoco.model import Model


def create_model(instance):
    """Football squad: buy players for as close to GBP 30 million as possible without going
    over, taking the required number from each position and at least eleven players in
    total. The output is the total price in GBP thousands."""
    budget = 30000  # the chairman's upper limit, in GBP thousands

    # prices[g][p] is the price of player p of group g, in GBP thousands, for the
    # goalkeepers, defenders, midfielders and strikers on offer.
    prices = [
        [730, 1280, 3880],
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
        [4460, 6470, 7780, 8390, 9500],
    ]
    # n_fewest[g] and n_most[g] are the fewest and the most players that may be bought from
    # group g. One goalkeeper is bought; the other groups can supply every player they have.
    n_fewest = [1, 2, 3, 2]
    n_most = [1] + [len(group) for group in prices[1:]]
    n_min_players = 11  # the fewest players in the squad, in total

    model = Model()

    # buy[g][p] is true when player p of group g is bought
    buy = [[model.boolvar(name=f"buy_{g}_{p}") for p in range(len(group))]
           for g, group in enumerate(prices)]

    # z is the total price of the players bought, in GBP thousands. It stays within the budget.
    z = model.intvar(0, budget, name="z")

    # Each group supplies between its fewest and its most players.
    for g in range(len(prices)):
        model.sum(buy[g], ">=", n_fewest[g]).post()
        model.sum(buy[g], "<=", n_most[g]).post()

    # The squad has at least the minimum number of players in total.
    everyone = [bought for group in buy for bought in group]  # every player on offer
    model.sum(everyone, ">=", n_min_players).post()

    # The price of each player, in the same order as everyone.
    all_prices = [price for group in prices for price in group]
    model.scalar(everyone, all_prices, "=", z).post()

    # Spend as much as possible.
    return model, {"z": z}, {"objective": z, "maximize": True}


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
