# football: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/football.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python football.py

from docplex.mp.model import Model


def create_model(instance):
    """Football squad: buy players of four kinds, within the numbers required of each kind and at
    least eleven in all, spending as close to the GBP 30 million limit as possible without going
    over."""
    budget = 30000   # the chairman's upper limit, in GBP thousands
    min_players = 11  # at least eleven players in all
    # prices[k][j]: the price in GBP thousands of player j of kind k, for the goalkeepers,
    # defenders, midfielders and strikers in turn
    prices = [[730, 1280, 3880],
              [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],
              [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
              [4460, 6470, 7780, 8390, 9500]]
    # The fewest and the most players to buy of each kind: exactly one goalkeeper, two or more
    # defenders, three or more midfielders and two or more strikers (up to all of them).
    fewest = [1, 2, 3, 2]
    most = [1] + [len(kind) for kind in prices[1:]]
    kinds = range(len(prices))

    model = Model("football")

    # buy[k][j] is 1 when player j of kind k is bought.
    buy = [[model.binary_var(name=f"buy_{k}_{j}") for j in range(len(prices[k]))] for k in kinds]

    # The number bought of each kind is within the numbers required of it.
    for k in kinds:
        model.add_range(fewest[k], model.sum(buy[k]), most[k])

    # At least eleven players in total.
    model.add_constraint(model.sum(b for kind in buy for b in kind) >= min_players)

    # z is the total price of the players bought; it may not go over the budget, and the
    # closer to it the better (maximised below).
    z = model.integer_var(0, budget, name="z")
    model.add_constraint(z == model.sum(price * b for k in kinds for price, b in zip(prices[k], buy[k])))
    model.maximize(z)

    return model, {"z": z}


if __name__ == "__main__":
    model, outputs = create_model({})
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)
