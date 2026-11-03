# who_killed_agatha: a Python-MIP (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

import mip


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents. From the clues about who hates whom and who
    is richer than whom, find out who killed Agatha."""
    names = instance["names"]  # names[i]: the name of resident i
    n = len(names)             # the number of residents

    # the positions of Agatha, the butler and Charles among the residents
    agatha = names.index("Agatha herself")
    butler = names.index("the butler")
    charles = names.index("Charles")

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # hates[i][j] is true when resident i hates resident j
    hates = [[model.add_var(f"hates_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]
    # richer[i][j] is true when resident i is richer than resident j
    richer = [[model.add_var(f"richer_{i}_{j}", var_type=mip.BINARY) for j in range(n)] for i in range(n)]
    # is_killer[i] is true when resident i killed Agatha
    is_killer = [model.add_var(f"is_killer_{i}", var_type=mip.BINARY) for i in range(n)]
    # killer is the position of the resident who killed Agatha
    killer = model.add_var("killer", lb=0, ub=n - 1, var_type=mip.INTEGER)

    # Exactly one resident killed Agatha.
    model += mip.xsum(is_killer) == 1
    # The killer is that resident's position.
    model += killer == mip.xsum(i * is_killer[i] for i in range(n))

    # A killer always hates, and is no richer than his victim.
    for i in range(n):
        model += hates[i][agatha] >= is_killer[i]
        model += richer[i][agatha] + is_killer[i] <= 1

    # Agatha hates everybody except the butler.
    for j in range(n):
        if j == butler:
            model += hates[agatha][j] == 0
        else:
            model += hates[agatha][j] == 1

    # Charles hates no one that Agatha hates.
    for j in range(n):
        model += hates[charles][j] + hates[agatha][j] <= 1

    # The butler hates everyone who is not richer than Agatha.
    for j in range(n):
        model += hates[butler][j] + richer[j][agatha] >= 1

    # The butler hates everyone whom Agatha hates.
    for j in range(n):
        model += hates[butler][j] - hates[agatha][j] >= 0

    # Nobody hates everyone.
    for i in range(n):
        model += mip.xsum(hates[i][j] for j in range(n)) <= n - 1

    return model, {"killer": killer}


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
