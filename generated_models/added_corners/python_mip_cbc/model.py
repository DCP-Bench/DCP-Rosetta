# added_corners: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install mip numpy`) with:
#   python added_corners.py

import mip


def create_model(instance):
    """Enter the digits 1 through 8 in the eight cells of a ring around an empty
    middle: four corner circles and four edge squares. Each square holds the sum
    of the two circles next to it."""
    model = mip.Model(solver_name="CBC")

    # The digit in each cell. The corner circles are cells 0, 2, 5 and 7; the edge squares are cells 1, 3, 4 and 6.
    x = [model.add_var(f"p{i}", lb=1, ub=8, var_type=mip.INTEGER) for i in range(8)]

    # choice[i][v - 1] is 1 when cell i holds the digit v.
    choice = [[model.add_var(f"b_{i}_{v}", var_type=mip.BINARY) for v in range(1, 9)] for i in range(8)]

    # Each cell holds exactly one digit, and that digit is the one chosen for it.
    for i in range(8):
        model.add_constr(mip.xsum(choice[i]) == 1)
        model.add_constr(x[i] == mip.xsum(v * choice[i][v - 1] for v in range(1, 9)))

    # Each digit goes in exactly one cell.
    for v in range(1, 9):
        model.add_constr(mip.xsum(choice[i][v - 1] for i in range(8)) == 1)

    # Each square is the sum of the two circles beside it: the top square sits between the top corners, and so on round the ring.
    model.add_constr(x[1] == x[0] + x[2])
    model.add_constr(x[3] == x[0] + x[5])
    model.add_constr(x[4] == x[2] + x[7])
    model.add_constr(x[6] == x[5] + x[7])

    return model, {"positions": x}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)
