# five_brigands: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install mip numpy`) with:
#   python five_brigands.py

import mip


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, have
    200 doubloons altogether. If Alfonso had twelve times as many, Benito three
    times as many, Carlos the same, Diego half as many and Esteban one third as
    many, they would still have 200 doubloons altogether. No brigand has less
    than one doubloon. How many doubloons has each?"""
    total = 200  # the doubloons the brigands have altogether

    model = mip.Model(solver_name="CBC")

    # The doubloons of Alfonso (A), Benito (B), Carlos (C), Diego (D) and Esteban (E).
    # Each has at least one doubloon, and no one has more than the total.
    A, B, C, D, E = [model.add_var(name, lb=1, ub=total, var_type=mip.INTEGER) for name in "ABCDE"]

    # Together they hold the total.
    model += mip.xsum([A, B, C, D, E]) == total

    # With the changed amounts the total is still 200. Multiplied by 6 to keep the
    # coefficients whole: 12A + 3B + C + D/2 + E/3 becomes 72A + 18B + 6C + 3D + 2E.
    model += 72 * A + 18 * B + 6 * C + 3 * D + 2 * E == 6 * total

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E}


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
