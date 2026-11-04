# coin3_application: a Choco-solver (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python coin3_application.py coin3_application.json

from pychoco.model import Model


def create_model(instance):
    """Find the minimum number of coins that allows one to pay exactly any amount
    smaller than a given maximum amount, using a given set of denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable
    n_denominations = len(denominations)        # the number of coin types

    model = Model()

    # x[i] is the number of coins of type i that are carried
    x = [model.intvar(0, max_amount, name=f"x_{i}") for i in range(n_denominations)]

    # Every amount from 1 to max_amount - 1 can be paid exactly from the coins carried.
    for amount in range(1, max_amount):
        # used[i] is the number of coins of type i in the payment of this amount
        used = [model.intvar(0, max_amount, name=f"used_{amount}_{i}") for i in range(n_denominations)]
        # A payment uses no more coins of a type than are carried.
        for i in range(n_denominations):
            model.arithm(used[i], "<=", x[i]).post()
        # The coins used add up to the amount.
        model.scalar(used, denominations, "=", amount).post()

    # num_coins is the total number of coins carried.
    num_coins = model.intvar(0, max_amount, name="num_coins")
    model.sum(x, "=", num_coins).post()

    # Carry as few coins as possible.
    return model, {"x": x}, {"objective": num_coins, "maximize": False}


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
