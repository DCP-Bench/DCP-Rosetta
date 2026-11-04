# session1_money_change: a Z3 (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session1_money_change.py session1_money_change.json

import z3


def create_model(instance):
    """Alice has to give Bob some change. She has different types of coins of
    different values and a certain number of coins of each value. Compose the
    change from the available coins, using as few coins as possible."""
    amount = instance["amount"]               # the change to give Bob
    types = instance["types_of_coins"]        # types[i]: the value of coin type i
    available = instance["available_coins"]   # available[i]: how many coins of type i Alice has

    # coin_counts[i] is the number of coins of type i given to Bob
    coin_counts = [z3.Int(f"coin_counts_{i}") for i in range(len(types))]

    solver = z3.Optimize()

    # Alice gives no negative number of coins and no more coins of a type than she has.
    solver.add([c >= 0 for c in coin_counts] + [c <= a for c, a in zip(coin_counts, available)])

    # The coins given add up to the amount.
    solver.add(z3.Sum([c * t for c, t in zip(coin_counts, types)]) == amount)

    # Use as few coins as possible.
    solver.minimize(z3.Sum(coin_counts))

    return solver, {"coin_counts": coin_counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
