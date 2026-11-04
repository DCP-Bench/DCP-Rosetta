# among: a Python-MIP (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python among.py among.json

import mip


def create_model(instance):
    """An array of n values, each from 0 to 7, in which exactly m values are
    among the listed values v."""
    n_values = instance["n"]    # the number of values in the array
    n_matches = instance["m"]   # how many values in the array must be among v
    v = instance["v"]           # the listed values that are counted

    model = mip.Model(solver_name="CBC")

    # The values an entry of the array can take.
    values = range(8)
    # The listed values that an entry can take.
    listed = sorted({val for val in v if val in values})

    # x[i] is the value at position i of the array.
    x = [model.add_var(f"x_{i}", lb=0, ub=max(values), var_type=mip.INTEGER) for i in range(n_values)]
    # pick[i][k] is 1 when x[i] takes the value k, and 0 when not.
    pick = [
        [model.add_var(f"pick_{i}_{k}", var_type=mip.BINARY) for k in values]
        for i in range(n_values)
    ]

    for i in range(n_values):
        # Each entry takes exactly one value.
        model += mip.xsum(pick[i][k] for k in values) == 1
        # The entry x[i] is the value it picks.
        model += x[i] == mip.xsum(k * pick[i][k] for k in values)

    # Exactly n_matches entries take one of the listed values.
    model += mip.xsum(pick[i][k] for i in range(n_values) for k in listed) == n_matches

    return model, {"x": x}


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
