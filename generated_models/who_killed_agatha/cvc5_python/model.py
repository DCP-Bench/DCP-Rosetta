# who_killed_agatha: a cvc5 (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

import cvc5.pythonic as c5


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents. From the clues about who hates whom and who
    is richer than whom, find out who killed Agatha."""
    names = instance["names"]  # names[i]: the name of resident i
    n_residents = len(names)   # the number of residents

    agatha = names.index("Agatha herself")  # Aunt Agatha, the victim
    butler = names.index("the butler")
    charles = names.index("Charles")

    # killer is the resident who killed Agatha
    killer = c5.Int("killer")
    # hates[i][j] is true when resident i hates resident j
    hates = [[c5.Bool(f"hates_{i}_{j}") for j in range(n_residents)] for i in range(n_residents)]
    # richer[i][j] is true when resident i is richer than resident j
    richer = [[c5.Bool(f"richer_{i}_{j}") for j in range(n_residents)] for i in range(n_residents)]

    solver = c5.Solver()

    # The killer is one of the residents.
    solver.add(killer >= 0, killer < n_residents)

    # Nobody is richer than himself, and of two residents at most one is richer than the other.
    solver.add([c5.Not(richer[i][i]) for i in range(n_residents)])
    solver.add([
        c5.Implies(richer[i][j], c5.Not(richer[j][i]))
        for i in range(n_residents)
        for j in range(n_residents)
        if i != j
    ])

    # A killer always hates his victim, and is no richer than his victim.
    for p in (agatha, butler, charles):
        solver.add(c5.Implies(killer == p, c5.And(hates[p][agatha], c5.Not(richer[p][agatha]))))

    # Agatha hates everybody except the butler.
    solver.add(hates[agatha][agatha], c5.Not(hates[agatha][butler]), hates[agatha][charles])

    # The butler hates everyone not richer than Agatha.
    solver.add([c5.Implies(c5.Not(richer[j][agatha]), hates[butler][j]) for j in range(n_residents)])

    # The butler hates everyone whom Agatha hates.
    solver.add([c5.Implies(hates[agatha][j], hates[butler][j]) for j in range(n_residents)])

    # Charles hates no one that Agatha hates.
    solver.add([c5.Implies(hates[agatha][j], c5.Not(hates[charles][j])) for j in range(n_residents)])

    # Nobody hates everyone.
    solver.add([c5.Or([c5.Not(hates[i][j]) for j in range(n_residents)]) for i in range(n_residents)])

    return solver, {"killer": killer}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
