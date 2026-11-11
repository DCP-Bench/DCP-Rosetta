# who_killed_agatha: a PyCSP3 model from DCP Rosetta.
# Download the `who_killed_agatha.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python who_killed_agatha.py who_killed_agatha.json

from pycsp3 import *


def create_model(instance):
    """Someone in Dreadsbury Mansion killed Aunt Agatha.
    Agatha, the butler, and Charles live in Dreadsbury Mansion, and
    are the only ones to live there. A killer always hates, and is
    no richer than his victim. Charles hates noone that Agatha hates.
    Agatha hates everybody except the butler. The butler hates everyone
    not richer than Aunt Agatha. The butler hates everyone whom Agatha hates.
    Noone hates everyone. Who killed Agatha?"""
    names = instance["names"]  # the names of the three people, in the order Agatha, the butler, Charles
    n_people = len(names)
    agatha, butler, charles = range(n_people)  # the indices of Agatha, the butler and Charles in names; the problem has exactly these three people

    # killer is the index of the person who killed Agatha, one of the people in the mansion.
    killer = Var(dom=range(n_people))

    # hates[i][j] is 1 when person i hates person j, and 0 otherwise.
    hates = VarArray(size=[n_people, n_people], dom={0, 1})

    # wealth[i] is the rank of person i's wealth; person i is richer than person j when wealth[i] > wealth[j].
    # Only the comparisons of wealth matter, and n_people people have at most n_people levels of wealth,
    # so ranks 0 .. n_people - 1 lose no solution.
    wealth = VarArray(size=n_people, dom=range(n_people))

    satisfy(
        # The killer hates Agatha, his victim.
        hates[killer][agatha] == 1,

        # The killer is no richer than Agatha.
        wealth[killer] <= wealth[agatha],

        # Agatha hates everybody except the butler.
        [hates[agatha][j] == 1 for j in range(n_people) if j != butler],
        hates[agatha][butler] == 0,

        # Charles hates no one that Agatha hates (read as: for each person j, if Agatha hates j then Charles does not).
        [imply(hates[agatha][j] == 1, hates[charles][j] == 0) for j in range(n_people)],

        # The butler hates everyone not richer than Agatha (read as: for each person j, if j is no richer than Agatha then the butler hates j).
        [imply(wealth[j] <= wealth[agatha], hates[butler][j] == 1) for j in range(n_people)],

        # The butler hates everyone whom Agatha hates (read as: for each person j, if Agatha hates j then the butler does too).
        [imply(hates[agatha][j] == 1, hates[butler][j] == 1) for j in range(n_people)],

        # Noone hates everyone.
        [Sum(hates[i][j] for j in range(n_people)) < n_people for i in range(n_people)],
    )

    return {"killer": killer}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())
