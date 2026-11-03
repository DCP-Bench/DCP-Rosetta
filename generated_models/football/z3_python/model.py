# football: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install z3-solver numpy`) with:
#   python football.py

import z3


def create_model(instance):
    """Buy football players from four positions (goalkeepers, defenders, midfielders and
    strikers) so that the total price is as close as possible to the 30 million GBP limit
    without going over it. The squad must have a set number of players from each position,
    and at least eleven players in total."""
    # Prices are in thousands of GBP, so the limit of 30 million GBP is 30000.
    budget = 30000

    # Each position: the fewest and the most players to buy there (None for no upper limit),
    # then the price of each player on offer.
    positions = [
        # goalkeepers: exactly one
        ((1, 1), [730, 1280, 3880]),
        # defenders: at least two
        ((2, None), [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]),
        # midfielders: at least three
        ((3, None), [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]),
        # strikers: at least two
        ((2, None), [4460, 6470, 7780, 8390, 9500]),
    ]

    # bought[k][j] is true when player j of position k is bought
    bought = [[z3.Bool(f"bought_{k}_{j}") for j in range(len(prices))]
              for k, (_, prices) in enumerate(positions)]

    # every player on offer, in every position
    everyone = [b for row in bought for b in row]

    solver = z3.Optimize()

    # Each position supplies between its fewest and its most players.
    for k, ((fewest, most), prices) in enumerate(positions):
        if most is None:
            most = len(prices)
        solver.add(z3.AtLeast(*bought[k], fewest))
        solver.add(z3.AtMost(*bought[k], most))

    # The squad has at least eleven players in total.
    solver.add(z3.AtLeast(*everyone, 11))

    # prices_all lists the price of each player in the order of everyone
    prices_all = [price for _, prices in positions for price in prices]

    # z is the total price of the players bought, in GBP thousands. It stays within the budget.
    z = z3.Int("z")
    solver.add(z >= 0, z <= budget,
               z == z3.Sum([z3.If(b, price, 0) for b, price in zip(everyone, prices_all)]))

    solver.maximize(z)

    return solver, {"z": z}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
