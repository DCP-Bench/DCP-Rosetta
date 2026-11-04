# handshaking: a CPMpy model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python handshaking.py handshaking.json

import cpmpy as cp


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples for dinner. Everybody
    shakes hands with some of the others, but nobody shakes hands with themselves
    or with their spouse. Jocelyn asks how many hands each person has shaken and
    all the answers are different. How many hands has Hilary shaken?"""
    num_couples = instance["num_couples"]  # the number of couples invited

    # The people are Hilary (person 0), Jocelyn (person 1) and then each invited
    # couple in turn: persons 2 and 3, persons 4 and 5, and so on. Person 2k and
    # person 2k+1 are spouses.
    n = 2 + num_couples * 2

    # shaken[i][j] is true when person i and person j shake hands
    shaken = cp.boolvar(shape=(n, n), name="shaken")
    # count[i] is the number of hands person i has shaken: from 0 up to n - 2,
    # since nobody shakes their own or their spouse's hand
    count = cp.intvar(0, n - 2, shape=n, name="count")
    # the number of hands Hilary has shaken
    hil = count[0]

    model = cp.Model()
    # Shaking hands is mutual.
    model.add(shaken == shaken.T)
    # Nobody shakes their own hand.
    for i in range(n):
        model.add(~shaken[i, i])
    # Nobody shakes the hand of their spouse.
    for i in range(0, n, 2):
        model.add(~shaken[i, i + 1])
    # Each person's count is the number of hands they have shaken.
    model.add(count == shaken.sum(axis=1))
    # Everybody except Hilary gave a different answer.
    model.add(cp.AllDifferent(count[1:]))

    return model, {"hil": hil}


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
