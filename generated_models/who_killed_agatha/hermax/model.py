# who_killed_agatha: a hermax (Python) model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install hermax`):
#   python who_killed_agatha.py who_killed_agatha.json

from hermax.model import Model

# The residents, by their position in the problem statement: Agatha, the butler, Charles.
AGATHA, BUTLER, CHARLES = range(3)


def create_model(instance):
    """Who killed Agatha? Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the
    butler and Charles are the only residents. From what is known about who hates whom and
    who is richer than whom, find the killer, as the 0-based index of the residents."""
    names = instance["names"]  # names[i]: the name of resident i; names are listed in the problem's order
    n = len(names)             # the number of residents living in the mansion
    victim = AGATHA            # the person who was killed

    m = Model()
    # killer is the 0-based index of the resident who killed Agatha
    killer = m.int("killer", 0, n - 1)
    # hates[i][j] is true when resident i hates resident j
    hates = m.bool_matrix("hates", n, n)
    # richer[i][j] is true when resident i is richer than resident j
    richer = m.bool_matrix("richer", n, n)

    # A killer always hates his victim, and is no richer than his victim.
    for k in range(n):
        m &= hates[k][victim].only_if(killer == k)
        m &= (~richer[k][victim]).only_if(killer == k)

    # Assumed, as in the reference: no one is richer than himself, and of two different
    # people exactly one is richer than the other (not needed to identify the killer).
    for i in range(n):
        m &= ~richer[i][i]
        for j in range(i + 1, n):
            m &= (richer[i][j] + richer[j][i] == 1)

    # Charles hates no one that Agatha hates.
    for i in range(n):
        m &= (~hates[AGATHA][i] | ~hates[CHARLES][i])

    # Agatha hates everybody except the butler.
    for i in range(n):
        if i == BUTLER:
            m &= ~hates[AGATHA][i]
        else:
            m &= hates[AGATHA][i]

    # The butler hates everyone not richer than Aunt Agatha.
    for i in range(n):
        m &= (richer[i][AGATHA] | hates[BUTLER][i])

    # The butler hates everyone whom Agatha hates.
    for i in range(n):
        m &= (~hates[AGATHA][i] | hates[BUTLER][i])

    # No one hates everyone: each resident hates at most n - 1 people.
    for i in range(n):
        m &= (sum(hates[i][j] for j in range(n)) <= n - 1)

    # Satisfaction problem: no objective, only the killer is reported.
    return m, {"killer": killer}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
