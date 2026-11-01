# heterosquare: a CPMpy model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python heterosquare.py heterosquare.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square

    # x[i, j] is the number in row i, column j
    x = cp.intvar(1, n * n, shape=(n, n), name="x")

    # The sums of the rows, the columns and the two diagonals. Each sum is at most
    # n * n^2 = n^3, since it adds n numbers of at most n^2.
    row_sums = cp.intvar(1, n ** 3, shape=n, name="row_sums")
    col_sums = cp.intvar(1, n ** 3, shape=n, name="col_sums")
    diag_sum = cp.intvar(1, n ** 3, name="diag_sum")        # top left to bottom right
    anti_diag_sum = cp.intvar(1, n ** 3, name="anti_diag_sum")  # top right to bottom left

    model = cp.Model()
    # The numbers in the square are distinct.
    model.add(cp.AllDifferent(x))
    # Define the sums.
    model.add(row_sums == x.sum(axis=1))
    model.add(col_sums == x.sum(axis=0))
    model.add(diag_sum == cp.sum(np.diag(x)))
    model.add(anti_diag_sum == cp.sum(np.diag(x[:, ::-1])))
    # All the row, column and diagonal sums are different.
    model.add(cp.AllDifferent(list(row_sums) + list(col_sums) + [diag_sum, anti_diag_sum]))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
