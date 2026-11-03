# session1_money_change: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session1_money_change.py session1_money_change.json

from pychoco.model import Model


def create_model(instance):
    """Alice has to give Bob some change. She has coins of several values and a set number of coins of each value. Compose the change from the coins she has, using as few coins as possible."""
    amount = instance["amount"]                    # the change Bob is owed
    types_of_coins = instance["types_of_coins"]    # value of each type of coin
    available_coins = instance["available_coins"]  # how many coins of each type Alice has
    n_types = len(types_of_coins)                  # number of coin types

    model = Model()

    # coin_counts[i] is the number of coins of type i given to Bob, at most the number Alice has
    coin_counts = [model.intvar(0, available_coins[i], name=f"coin_counts_{i}") for i in range(n_types)]

    # The coins given add up to the amount.
    model.scalar(coin_counts, types_of_coins, "=", amount).post()

    # Total number of coins given. Alice wants this as small as possible.
    total_coins = model.intvar(0, sum(available_coins), name="total_coins")
    model.sum(coin_counts, "=", total_coins).post()

    return model, {"coin_counts": coin_counts}, {"objective": total_coins, "maximize": False}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
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
