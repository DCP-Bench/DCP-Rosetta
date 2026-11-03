# session2_subset_sum: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

from pychoco.model import Model


def create_model(instance):
    """A bank van had several kinds of coin bags, each kind holding a fixed number
    of coins, with many bags of each kind. Thieves stole some bags, and exactly
    the given total number of coins was lost. Find how many bags of each kind
    were stolen."""
    coin_numbers = instance["coin_numbers"]      # coin_numbers[i]: the number of coins in a bag of kind i
    total_coins_lost = instance["total_coins_lost"]  # the total number of coins that were lost

    model = Model()

    # bags[i]: the number of stolen bags of kind i. Every bag holds at least one
    # coin, so no kind can account for more bags than there are lost coins.
    bags = [model.intvar(0, total_coins_lost, name=f"bags_{i}") for i in range(len(coin_numbers))]

    # The stolen bags hold exactly the coins that were lost.
    model.scalar(bags, coin_numbers, "=", total_coins_lost).post()

    return model, {"bags": bags}, None


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
