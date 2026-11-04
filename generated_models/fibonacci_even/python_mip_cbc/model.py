# fibonacci_even: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install mip numpy`) with:
#   python fibonacci_even.py

import mip


def create_model(instance):
    """Each new term in the Fibonacci sequence is the sum of the previous two, starting
    from 1 and 2. Find the sum of the even-valued terms that do not exceed four million."""
    limit = 4000000    # the largest term that is added up
    n_terms = 33       # the number of terms considered; term 32 (5702887) is the first above the limit
    bound = 2 * limit  # upper bound on every term considered

    model = mip.Model(solver_name="CBC")

    # f[i] is term i of the sequence; the first two terms are 1 and 2
    f = []
    for i in range(n_terms):
        if i < 2:
            f.append(model.add_var(f"f_{i}", lb=i + 1, ub=i + 1, var_type=mip.INTEGER))
        else:
            f.append(model.add_var(f"f_{i}", lb=0, ub=bound, var_type=mip.INTEGER))

    # Each term from the third on is the sum of the two terms before it.
    for i in range(2, n_terms):
        model += f[i] == f[i - 1] + f[i - 2]

    # h[i] is half of term i, rounded down
    h = [model.add_var(f"h_{i}", lb=0, ub=bound, var_type=mip.INTEGER) for i in range(n_terms)]
    # r[i] is true when term i is odd
    r = [model.add_var(f"r_{i}", var_type=mip.BINARY) for i in range(n_terms)]
    # Each term is twice its half, plus 1 when it is odd.
    for i in range(n_terms):
        model += f[i] == 2 * h[i] + r[i]

    # within[i] is true when term i does not exceed four million
    within = [model.add_var(f"within_{i}", var_type=mip.BINARY) for i in range(n_terms)]
    # Term i is at most four million exactly when within[i] is true.
    for i in range(n_terms):
        model += f[i] <= limit + bound * (1 - within[i])
        model += f[i] >= (limit + 1) - (limit + 1) * within[i]

    # counted[i] is true when term i is one of the terms added up
    counted = [model.add_var(f"counted_{i}", var_type=mip.BINARY) for i in range(n_terms)]
    # A term is counted exactly when it is even (r is false) and does not exceed four million (within is true).
    for i in range(n_terms):
        model += counted[i] <= 1 - r[i]
        model += counted[i] <= within[i]
        model += counted[i] >= within[i] - r[i]

    # contribution[i] is the amount term i adds to the sum
    contribution = [
        model.add_var(f"contribution_{i}", lb=0, ub=limit, var_type=mip.INTEGER)
        for i in range(n_terms)
    ]
    # It is term i when term i is counted, and 0 otherwise.
    for i in range(n_terms):
        model += contribution[i] <= f[i]
        model += contribution[i] <= limit * counted[i]
        model += contribution[i] >= f[i] - bound * (1 - counted[i])

    # res is the sum of the even-valued terms that do not exceed four million
    res = model.add_var("res", lb=0, ub=n_terms * limit, var_type=mip.INTEGER)
    # The sum is the total of the contributions.
    model += res == mip.xsum(contribution)

    return model, {"res": res}


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
