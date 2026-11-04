# session1_money_change: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session1_money_change.py session1_money_change.json

import mip


def create_model(instance):
    """Alice gives Bob change using the coins she has available: compose the
    amount from the available coins, using as few coins as possible."""
    amount = instance["amount"]               # the change to give Bob
    values = instance["types_of_coins"]       # values[i]: the value of coin type i
    available = instance["available_coins"]   # available[i]: how many coins of type i Alice has

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # counts[i] is the number of coins of type i given to Bob, at most the number Alice has
    counts = [
        model.add_var(f"coins_{i}", lb=0, ub=available[i], var_type=mip.INTEGER)
        for i in range(len(values))
    ]

    # The coins given add up to the amount.
    model.add_constr(
        mip.xsum(values[i] * counts[i] for i in range(len(values))) == amount,
        "amount_given",
    )

    # Use as few coins as possible.
    model.objective = mip.xsum(counts)

    return model, {"coin_counts": counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
