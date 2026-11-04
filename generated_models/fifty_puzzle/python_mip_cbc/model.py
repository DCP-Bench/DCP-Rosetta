# fifty_puzzle: a Python-MIP (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

import mip


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs: choose
    the dummies to knock down so that their numbers add up to exactly the target sum,
    neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the exact total the knocked-over numbers must reach
    n_dummies = len(values)              # the number of dummies

    model = mip.Model(solver_name="CBC")

    # dummies[i] is true when dummy i is knocked over
    dummies = [model.add_var(f"dummies_{i}", var_type=mip.BINARY) for i in range(n_dummies)]

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    model += mip.xsum(values[i] * dummies[i] for i in range(n_dummies)) == target_sum

    return model, {"dummies": dummies}


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
