# csplib_024_langford: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

import mip


def create_model(instance):
    """Arrange two copies of each number from 1 to k into one sequence of 2k places, so that the
    two 1's appear one number apart, the two 2's two numbers apart, ..., and the two k's k numbers
    apart."""
    k = instance["k"]  # the largest number; the sequence holds two copies of each of 1 to k
    n_places = 2 * k   # the sequence has one place for each copy

    model = mip.Model(solver_name="CBC")

    # x[(i, p)] is 1 when the first copy of number i is at place p and the second copy is i + 1
    # places further on, and 0 otherwise
    x = {}
    for i in range(1, k + 1):
        for p in range(0, n_places - i - 1):
            x[(i, p)] = model.add_var(f"x_{i}_{p}", var_type=mip.BINARY)

    # Each number i has exactly one placement.
    for i in range(1, k + 1):
        model += mip.xsum(x[(i, p)] for p in range(0, n_places - i - 1)) == 1

    # sol[q] is the number at place q.
    sol = []
    for q in range(n_places):
        # the placements that put a copy of some number at place q
        covers = []
        for i in range(1, k + 1):
            if (i, q) in x:
                covers.append((i, x[(i, q)]))
            if (i, q - i - 1) in x:
                covers.append((i, x[(i, q - i - 1)]))
        # Place q holds exactly one copy.
        model += mip.xsum(b for _, b in covers) == 1
        s = model.add_var(f"sol_{q}", lb=1, ub=k, var_type=mip.INTEGER)
        model += s == mip.xsum(i * b for i, b in covers)
        sol.append(s)

    # There is no objective: any sequence that meets the rules is an answer.
    return model, {"sol": sol}


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
