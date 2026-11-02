# who_killed_agatha: a PuLP (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

import pulp


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents. From the clues about who hates whom and who
    is richer than whom, find out who killed Agatha."""
    names = instance["names"]  # names[i]: the name of resident i
    n_residents = len(names)   # the number of residents
    residents = range(n_residents)

    # The residents the clues talk about.
    agatha = names.index("Agatha herself")  # the victim
    butler = names.index("the butler")
    charles = names.index("Charles")

    problem = pulp.LpProblem("who_killed_agatha", pulp.LpMinimize)

    # is_killer[k] is 1 when resident k killed Agatha.
    is_killer = [pulp.LpVariable(f"is_killer_{k}", cat="Binary") for k in residents]

    # Exactly one resident killed Agatha.
    problem += pulp.lpSum(is_killer) == 1

    # The number of the resident who killed Agatha.
    killer = pulp.lpSum(k * flag for k, flag in zip(residents, is_killer))

    # hates[i][j] is 1 when resident i hates resident j.
    hates = [[pulp.LpVariable(f"hates_{i}_{j}", cat="Binary") for j in residents]
             for i in residents]
    # Agatha hates herself and Charles, and does not hate the butler.
    hates[agatha][agatha].bounds(1, 1)
    hates[agatha][charles].bounds(1, 1)
    hates[agatha][butler].bounds(0, 0)

    # richer[i][j] is 1 when resident i is richer than resident j.
    richer = [[pulp.LpVariable(f"richer_{i}_{j}", cat="Binary") for j in residents]
              for i in residents]
    # Nobody is richer than himself.
    for i in residents:
        richer[i][i].bounds(0, 0)

    # A killer always hates, and is no richer than, his victim.
    for k in residents:
        problem += hates[k][agatha] >= is_killer[k]
        problem += richer[k][agatha] <= 1 - is_killer[k]

    # Of two different residents, exactly one is richer than the other.
    for i in residents:
        for j in residents:
            if i < j:
                problem += richer[i][j] == 1 - richer[j][i]

    # Charles hates no one that Agatha hates.
    for i in residents:
        problem += hates[charles][i] <= 1 - hates[agatha][i]

    # The butler hates everyone who is not richer than Agatha.
    for i in residents:
        problem += hates[butler][i] >= 1 - richer[i][agatha]

    # The butler hates everyone whom Agatha hates.
    for i in residents:
        problem += hates[butler][i] >= hates[agatha][i]

    # Nobody hates everyone.
    for i in residents:
        problem += pulp.lpSum(hates[i]) <= n_residents - 1

    return problem, {"killer": killer}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
