# who_killed_agatha: an Exact (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

from exact import Exact


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents. From the clues about who hates whom and who
    is richer than whom, find out who killed Agatha."""
    names = instance["names"]  # names[i]: the name of resident i
    n = len(names)             # the number of residents

    # The positions of Agatha, the butler and Charles among the residents.
    agatha = names.index("Agatha herself")
    butler = names.index("the butler")
    charles = names.index("Charles")
    victim = agatha  # Agatha is the one who was killed

    solver = Exact()

    # Exact identifies its variables by name.
    # hates[i][j] is 1 when resident i hates resident j. Agatha hates everybody except the butler.
    hates = [[f"hates_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            if i == agatha:
                fixed = int(j != butler)
                solver.addVariable(hates[i][j], fixed, fixed)
            else:
                solver.addVariable(hates[i][j], 0, 1)

    # richer[i][j] is 1 when resident i is richer than resident j. Nobody is richer than himself.
    richer = [[f"richer_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(richer[i][j], 0, 0 if i == j else 1)

    # killer is the number of the resident who killed Agatha. is_killer[i] is 1 when
    # resident i is the killer, and 0 when not.
    solver.addVariable("killer", 0, n - 1)
    is_killer = [f"is_killer_{i}" for i in range(n)]
    for name in is_killer:
        solver.addVariable(name, 0, 1)

    # Exactly one resident is the killer.
    solver.addConstraint([(1, name) for name in is_killer], True, 1, True, 1)
    # The killer's number is the number of the resident who is the killer.
    solver.addConstraint([(i, is_killer[i]) for i in range(1, n)] + [(-1, "killer")], True, 0, True, 0)

    # A killer always hates his victim.
    for i in range(n):
        solver.addConstraint([(1, hates[i][victim]), (-1, is_killer[i])], True, 0)

    # A killer is no richer than his victim.
    for i in range(n):
        solver.addConstraint([(1, richer[i][victim]), (1, is_killer[i])], False, 0, True, 1)

    # Of two different residents, exactly one is richer than the other.
    for i in range(n):
        for j in range(i + 1, n):
            solver.addConstraint([(1, richer[i][j]), (1, richer[j][i])], True, 1, True, 1)

    # Charles hates no one that Agatha hates.
    for i in range(n):
        solver.addConstraint([(1, hates[agatha][i]), (1, hates[charles][i])], False, 0, True, 1)

    # The butler hates everyone who is not richer than Agatha.
    for i in range(n):
        solver.addConstraint([(1, richer[i][agatha]), (1, hates[butler][i])], True, 1)

    # The butler hates everyone whom Agatha hates.
    for i in range(n):
        solver.addConstraint([(1, hates[butler][i]), (-1, hates[agatha][i])], True, 0)

    # Nobody hates everyone, so each resident hates at most n - 1 of the others.
    for i in range(n):
        solver.addConstraint([(1, hates[i][j]) for j in range(n)], False, 0, True, n - 1)

    return solver, {"killer": "killer"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
