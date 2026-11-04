# session5_hardy_1729_square: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install mip numpy`) with:
#   python session5_hardy_1729_square.py

import mip


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the last two: a^2 + b^2 = c^2 + d^2."""
    model = mip.Model(solver_name="CBC")

    # The candidate values for each number, 1 to 100.
    values = list(range(1, 101))
    names = ["a", "b", "c", "d"]

    # x[n] is the number n, between 1 and 100.
    x = {n: model.add_var(n, lb=1, ub=100, var_type=mip.INTEGER) for n in names}
    # p[n][v] is 1 when the number n is v, and 0 when not.
    p = {
        n: {v: model.add_var(f"p_{n}_{v}", var_type=mip.BINARY) for v in values}
        for n in names
    }

    for n in names:
        # Each number takes exactly one value.
        model.add_constr(mip.xsum(p[n][v] for v in values) == 1)
        model.add_constr(x[n] == mip.xsum(v * p[n][v] for v in values))

    # The four numbers are different: each value is taken by at most one of them.
    for v in values:
        model.add_constr(mip.xsum(p[n][v] for n in names) <= 1)

    # The squares of a and b, and the squares of c and d, are summed over the chosen values.
    sq_ab = mip.xsum([v * v * p["a"][v] for v in values] + [v * v * p["b"][v] for v in values])
    sq_cd = mip.xsum([v * v * p["c"][v] for v in values] + [v * v * p["d"][v] for v in values])
    # a^2 + b^2 = c^2 + d^2
    model.add_constr(sq_ab == sq_cd)

    return model, {"a": x["a"], "b": x["b"], "c": x["c"], "d": x["d"]}


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
