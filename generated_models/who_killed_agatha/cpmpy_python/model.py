# who_killed_agatha: a CPMpy model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python who_killed_agatha.py who_killed_agatha.json

import cpmpy as cp


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and
    Charles are the only residents. From the clues about who hates whom and who
    is richer than whom, find out who killed Agatha."""
    n = len(instance["names"])  # names[i]: resident i; the residents are the only people in the story
    agatha, butler, charles = 0, 1, 2  # residents are numbered in the order Agatha, the butler, Charles
    victim = agatha

    # killer is the resident who killed Agatha
    killer = cp.intvar(0, n - 1, name="killer")
    # hates[i, j] is true when resident i hates resident j
    hates = cp.boolvar(shape=(n, n), name="hates")
    # richer[i, j] is true when resident i is richer than resident j
    richer = cp.boolvar(shape=(n, n), name="richer")

    model = cp.Model()

    # A killer always hates, and is no richer than, his victim.
    model.add(hates[killer, victim] == 1)
    model.add(richer[killer, victim] == 0)

    # Nobody is richer than himself, and of two different residents exactly one is richer.
    model.add(~richer.diagonal())
    for i in range(n):
        for j in range(i + 1, n):
            model.add(richer[i, j] != richer[j, i])

    # Charles hates nobody that Agatha hates.
    model.add(hates[agatha].implies(~hates[charles]))

    # Agatha hates everybody except the butler.
    model.add(hates[agatha, agatha])
    model.add(hates[agatha, charles])
    model.add(~hates[agatha, butler])

    # The butler hates everyone not richer than Agatha.
    model.add((~richer[:, agatha]).implies(hates[butler]))
    # The butler hates everyone whom Agatha hates.
    model.add(hates[agatha].implies(hates[butler]))

    # Nobody hates everyone.
    model.add([cp.sum(hates[i]) <= n - 1 for i in range(n)])

    return model, {"killer": killer}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
