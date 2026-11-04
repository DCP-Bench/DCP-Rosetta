# session2_subset_sum: a PySAT (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A bank van lost some bags of coins. Each kind of bag holds a fixed number of
    coins, and there are many bags of each kind. Find how many bags of each kind were
    stolen so that the stolen bags hold exactly the coins that were lost."""
    coin_numbers = instance["coin_numbers"]  # coin_numbers[i]: the number of coins in a bag of kind i
    total_lost = instance["total_coins_lost"]  # the number of coins that were lost

    pool = IDPool()  # hands out the variable numbers

    # bags[i] is the number of stolen bags of kind i. Those bags hold at most the lost
    # coins, so there are at most total_lost // coin_numbers[i] of them.
    bags = [Integer(f"bag{i}", 0, total_lost // value if value else total_lost, vpool=pool)
            for i, value in enumerate(coin_numbers)]

    # Whole-number constraints on the bag counts.
    engine = IntegerEngine(vars=bags, vpool=pool)

    # The stolen bags hold exactly the coins that were lost.
    engine.add_linear(sum(c * b for c, b in zip(coin_numbers, bags)) == total_lost)

    return engine.clausify(), {"bags": bags}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
