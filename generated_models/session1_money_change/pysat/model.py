# session1_money_change: a PySAT (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session1_money_change.py session1_money_change.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import PBEnc


def create_model(instance):
    """Alice has to give Bob some change. She has coins of several types, each with a
    value and a limited number, and must pay the exact amount with as few coins as
    possible."""
    amount = instance["amount"]                    # the change Alice must give Bob
    types_of_coins = instance["types_of_coins"]    # types_of_coins[i]: the value of coin type i
    available_coins = instance["available_coins"]  # available_coins[i]: how many coins of type i Alice has
    n_types = len(types_of_coins)                  # the number of coin types

    pool = IDPool()  # hands out the variable numbers

    formula = WCNF()

    # coin_counts[i] is the number of coins of type i that Alice gives Bob, from 0 up to
    # the number she has.
    coin_counts = [Integer(f"coin_counts_{i}", 0, available_coins[i], encoding="coupled", vpool=pool)
                   for i in range(n_types)]

    # Each count is exactly one of its values.
    for count in coin_counts:
        formula.extend(count.domain_clauses())

    # One fact for each coin that can be given: "Bob gets at least v coins of type i". Each
    # such fact stands for one coin of type i, so fact_values gives the value of that coin.
    facts = [coin_counts[i].ge(v) for i in range(n_types) for v in range(1, available_coins[i] + 1)]
    fact_values = [types_of_coins[i] for i in range(n_types) for v in range(1, available_coins[i] + 1)]

    # The coins given add up to the amount.
    formula.extend(PBEnc.equals(lits=facts, weights=fact_values, bound=amount, vpool=pool).clauses)

    # Minimise the number of coins given: each fact that holds costs 1.
    for fact in facts:
        formula.append([-fact], weight=1)

    return formula, {"coin_counts": coin_counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
