# who_killed_agatha: a Z3 (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

import z3


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and Charles
    are the only residents. From the clues about who hates whom and who is richer than
    whom, find out who killed Agatha."""
    names = instance["names"]  # names[i]: the name of resident i
    n = len(names)             # the number of residents

    # Agatha, the butler and Charles are residents 0, 1 and 2.
    agatha, butler, charles = 0, 1, 2
    victim = agatha  # the one who was killed

    # killer is the number of the resident who killed Agatha
    killer = z3.Int("killer")
    # hates[i][j] is true when resident i hates resident j
    hates = [[z3.Bool(f"hates_{i}_{j}") for j in range(n)] for i in range(n)]
    # richer[i][j] is true when resident i is richer than resident j
    richer = [[z3.Bool(f"richer_{i}_{j}") for j in range(n)] for i in range(n)]

    solver = z3.Solver()

    # The killer is one of the residents.
    solver.add(killer >= 0, killer <= n - 1)

    # A killer always hates, and is no richer than, his victim.
    for i in range(n):
        solver.add(z3.Implies(killer == i, hates[i][victim]))
        solver.add(z3.Implies(killer == i, z3.Not(richer[i][victim])))

    # Nobody is richer than himself, and of two residents exactly one is richer than the other.
    for i in range(n):
        solver.add(z3.Not(richer[i][i]))
        for j in range(i + 1, n):
            solver.add(richer[i][j] == z3.Not(richer[j][i]))

    # Agatha hates herself and Charles, and does not hate the butler.
    solver.add(hates[agatha][agatha], hates[agatha][charles], z3.Not(hates[agatha][butler]))

    # Charles hates nobody that Agatha hates.
    solver.add([z3.Implies(hates[agatha][i], z3.Not(hates[charles][i])) for i in range(n)])

    # The butler hates everyone not richer than Agatha.
    solver.add([z3.Implies(z3.Not(richer[i][agatha]), hates[butler][i]) for i in range(n)])

    # The butler hates everyone whom Agatha hates.
    solver.add([z3.Implies(hates[agatha][i], hates[butler][i]) for i in range(n)])

    # Nobody hates everyone.
    solver.add([z3.Sum([z3.If(hates[i][j], 1, 0) for j in range(n)]) <= n - 1 for i in range(n)])

    return solver, {"killer": killer}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
