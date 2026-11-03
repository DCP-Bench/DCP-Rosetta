# session1_money_change: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install ortools`):
#   python session1_money_change.py session1_money_change.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Alice has to give Bob some change. She has different types of coins of
    different values and a certain number of coins of each value. Compose the
    change from the available coins, using as few coins as possible."""
    amount = instance["amount"]               # the change to give Bob
    types = instance["types_of_coins"]        # types[i]: the value of coin type i
    available = instance["available_coins"]   # available[i]: how many coins of type i Alice has

    model = cp_model.CpModel()

    # coin_counts[i] is the number of coins of type i given to Bob. Alice cannot
    # give more coins of a type than she has.
    coin_counts = [model.new_int_var(0, available[i], f"coin_counts_{i}") for i in range(len(types))]

    # The coins given add up to the amount.
    model.add(sum(c * t for c, t in zip(coin_counts, types)) == amount)

    # Use as few coins as possible.
    model.minimize(sum(coin_counts))

    return model, {"coin_counts": coin_counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
