# session2_subset_sum: an Exact (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

from exact import Exact


def create_model(instance):
    """A bank van lost some bags of coins, each bag holding one of the given
    numbers of coins, with several bags of each kind. Find how many bags of each
    kind were stolen so that exactly the given total number of coins was lost."""
    total_coins_lost = instance["total_coins_lost"]  # the total number of coins that were lost
    coin_numbers = instance["coin_numbers"]  # the number of coins in a bag of each kind
    n_kinds = len(coin_numbers)  # the number of kinds of bag

    solver = Exact()

    # Exact identifies its variables by name.
    # bags[i] is the number of stolen bags of kind i, at most the number of coins lost
    bags = [f"bags_{i}" for i in range(n_kinds)]
    for name in bags:
        solver.addVariable(name, 0, total_coins_lost)

    # The stolen bags hold exactly the coins that were lost.
    solver.addConstraint([(coin_numbers[i], bags[i]) for i in range(n_kinds) if coin_numbers[i]],
                         True, total_coins_lost, True, total_coins_lost)

    return solver, {"bags": bags}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
