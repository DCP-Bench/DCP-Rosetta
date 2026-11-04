# birthday_coins: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python birthday_coins.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Tommy was given 15 coins (half-crowns, shillings and sixpences) that add up to
    one pound, five shillings and six pence. How many half-crowns was he given?"""
    # Money is counted in pence: a shilling is 12 pence, a pound is 20 shillings and a
    # sixpence is 6 pence. A half-crown is 2 shillings and a sixpence.
    values = [2 * 12 + 6, 12, 6]        # values[c]: the worth of one coin of kind c, in pence
    total_value = 20 * 12 + 5 * 12 + 6  # one pound, five shillings and six pence
    n_coins = 15                        # the number of coins Tommy was given

    pool = IDPool()

    # coins[c] is the number of coins of kind c that Tommy was given, kinds in the order of values
    coins = [Integer(f"coins_{c}", 0, n_coins, vpool=pool) for c in range(len(values))]
    engine = IntegerEngine(vars=coins, vpool=pool)

    # The coins are worth one pound, five shillings and six pence together.
    engine.add_linear(sum(v * n for v, n in zip(values, coins)) == total_value)
    # Tommy was given 15 coins.
    engine.add_linear(sum(coins) == n_coins)

    return engine.clausify(), {"half_crowns": coins[0]}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
