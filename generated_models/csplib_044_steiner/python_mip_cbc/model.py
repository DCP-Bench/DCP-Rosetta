# csplib_044_steiner: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

import mip


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n = instance["n"]              # the number of elements
    n_triples = n * (n - 1) // 6   # the number of triples in the system

    model = mip.Model(solver_name="CBC")

    # sets[i][j] is 1 when element j is in triple i, and 0 otherwise
    sets = [[model.add_var(f"sets_{i}_{j}", var_type=mip.BINARY) for j in range(n)]
            for i in range(n_triples)]

    # Each triple has exactly three elements.
    for i in range(n_triples):
        model.add_constr(mip.xsum(sets[i]) == 3)

    # Every pair of elements lies in exactly one triple.
    for a in range(n):
        for b in range(a + 1, n):
            # both[i] is 1 for the triple that contains a and b.
            both = [model.add_var(f"both_{i}_{a}_{b}", lb=0, ub=1) for i in range(n_triples)]
            for i in range(n_triples):
                model.add_constr(both[i] >= sets[i][a] + sets[i][b] - 1)
            model.add_constr(mip.xsum(both) == 1)

    # Each element meets the other n - 1 elements, two in each triple it lies in,
    # so it lies in (n - 1) / 2 triples.
    for j in range(n):
        model.add_constr(mip.xsum(sets[i][j] for i in range(n_triples)) == (n - 1) // 2)

    return model, {"sets": sets}


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
