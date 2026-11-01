# birthday_coins: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install pychoco numpy`) with:
#   python birthday_coins.py

from pychoco.model import Model


def create_model(instance):
    """Tommy was given 15 coins (half-crowns, shillings and sixpences) that add up to one
    pound, five shillings and six pence. How many half-crowns was he given?"""
    # Money in pence: a shilling is 12 pence and a pound is 20 shillings.
    shilling = 12
    pound = 20 * shilling
    sixpence = 6
    # pence worth of a half-crown (2 shillings and sixpence), a shilling and a sixpence
    values = [2 * shilling + sixpence, shilling, sixpence]
    total_value = pound + 5 * shilling + sixpence  # the worth of all the coins, in pence
    total_coins = 15                               # the number of coins Tommy was given

    model = Model()

    # coins[c] is the number of coins of kind c; the half-crowns are kind 0
    coins = [model.intvar(0, total_coins, name=f"coins_{c}") for c in range(len(values))]

    # The coins are worth one pound, five shillings and six pence together.
    model.scalar(coins, values, "=", total_value).post()

    # Tommy was given 15 coins in all.
    model.sum(coins, "=", total_coins).post()

    return model, {"half_crowns": coins[0]}, None


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
