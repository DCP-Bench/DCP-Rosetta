# who_killed_agatha: a SCIP (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python who_killed_agatha.py who_killed_agatha.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents of the mansion. A killer always hates the
    victim and is no richer than the victim. The statements about hating and
    wealth fix who the killer is: the output is the 0-based index of the killer
    among the residents."""
    # The residents, in the order the instance lists them: names[0] is Agatha
    # herself, names[1] the butler, names[2] Charles.
    names = instance["names"]  # the residents of the mansion
    n = len(names)             # the number of residents: three, as the statement names
    AGATHA, BUTLER, CHARLES = 0, 1, 2

    model = Model("who_killed_agatha")

    # hates[x, y] is 1 when resident x hates resident y. "Everybody" is read as
    # every resident, the person themself included, so hates[x, x] is a real entry.
    hates = model.addMatrixVar((n, n), vtype="B", name="hates")

    # richer[y] is 1 when resident y is richer than Agatha. The statement only
    # compares wealth with Agatha, so this is the only richness fact modelled:
    # no other ordering between residents is assumed. Agatha is not richer than
    # herself, so her entry is 0.
    richer = model.addMatrixVar(n, vtype="B", name="richer")

    # killer[x] is 1 when resident x killed Agatha. The statement says someone
    # killed her, and it speaks of a single killer, so exactly one entry is 1.
    killer = model.addMatrixVar(n, vtype="B", name="killer")

    # Agatha is not richer than herself.
    model.addCons(richer[AGATHA] == 0)

    # Exactly one resident killed Agatha.
    model.addCons(quicksum(killer) == 1)

    # A killer always hates the victim: killer[x] = 1 forces hates[x, AGATHA]
    # to 1, and killer[x] = 0 leaves it free. Written as the linear form of
    # that implication between two binaries.
    model.addMatrixCons(hates[:, AGATHA] >= killer)

    # A killer is no richer than the victim: killer[x] = 1 forces richer[x] to 0.
    model.addMatrixCons(richer + killer <= 1)

    # Agatha hates everybody except the butler.
    model.addMatrixCons(hates[AGATHA] == [0 if y == BUTLER else 1 for y in range(n)])

    # Charles hates no one that Agatha hates: for no resident y are both
    # hates[AGATHA, y] and hates[CHARLES, y] 1.
    model.addMatrixCons(hates[CHARLES] + hates[AGATHA] <= 1)

    # The butler hates everyone not richer than Agatha: for each resident y,
    # either y is richer than Agatha or the butler hates y.
    model.addMatrixCons(hates[BUTLER] + richer >= 1)

    # The butler hates everyone whom Agatha hates.
    model.addMatrixCons(hates[BUTLER] >= hates[AGATHA])

    # Nobody hates everyone: each resident hates at most n - 1 of the n residents.
    model.addMatrixCons(hates.sum(axis=1) <= n - 1)

    # The killer is the resident whose killer entry is 1: its index is the output.
    return model, {"killer": quicksum(x * killer[x] for x in range(n))}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
