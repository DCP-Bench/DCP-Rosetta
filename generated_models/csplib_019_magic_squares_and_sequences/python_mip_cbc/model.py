# csplib_019_magic_squares_and_sequences: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_019_magic_squares_and_sequences.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_019_magic_squares_and_sequences.py csplib_019_magic_squares_and_sequences.json

import mip


def create_model(instance):
    """A magic sequence of length n is a sequence of integers x_0, ..., x_{n-1}
    between 0 and n-1 such that, for every i, the number i occurs exactly x_i times
    in the sequence."""
    n = instance["n"]  # the length of the sequence

    model = mip.Model(solver_name="CBC")

    # x[i] is the number at position i, so it is also how often the number i occurs
    x = [model.add_var(f"x_{i}", lb=0, ub=n - 1, var_type=mip.INTEGER) for i in range(n)]

    # holds[i][v] is 1 when position i holds the number v
    holds = [[model.add_var(f"holds_{i}_{v}", var_type=mip.BINARY) for v in range(n)]
             for i in range(n)]

    # Each position holds exactly one number.
    for i in range(n):
        model.add_constr(mip.xsum(holds[i]) == 1)
        # x[i] is the number that position i holds.
        model.add_constr(x[i] == mip.xsum(v * holds[i][v] for v in range(n)))

    # The number i occurs exactly x[i] times: x[i] counts the positions that hold i.
    for i in range(n):
        model.add_constr(x[i] == mip.xsum(holds[j][i] for j in range(n)))

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
