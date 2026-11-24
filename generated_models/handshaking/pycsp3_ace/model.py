# handshaking: a PyCSP3 model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python handshaking.py handshaking.json

from pycsp3 import *


def create_model(instance):
    """Hilary and Jocelyn are married. They invite some couples who are friends for
    dinner, and the guests shake hands with each other, but nobody shakes hands with
    him or herself or with his or her spouse. Jocelyn then asks how many hands each
    person has shaken, and all the answers are different. Find how many hands Hilary
    has shaken."""
    # The number of invited couples, not counting Hilary and Jocelyn.
    num_couples = instance["num_couples"]
    # The invited couples and the host couple.
    n_couples_with_host = num_couples + 1
    # Each couple is two people: person 0 is Hilary, person 1 is Jocelyn, and the
    # couples are (0, 1), (2, 3), and so on.
    n_people = 2 * n_couples_with_host
    hilary = 0
    jocelyn = 1
    # spouse[p] is the husband or wife of person p.
    spouse = [p + 1 if p % 2 == 0 else p - 1 for p in range(n_people)]

    # shakes[p][q] is 1 when person p shakes hands with person q.
    shakes = VarArray(size=[n_people, n_people], dom={0, 1})
    # hands[p] is the number of hands person p has shaken; nobody shakes hands with
    # self or spouse, so at most n_people - 2 hands (domain 0 to n_people - 2).
    hands = VarArray(size=n_people, dom=range(n_people - 1))

    satisfy(
        # Nobody shakes hands with him or herself.
        [shakes[p][p] == 0 for p in range(n_people)],
        # Nobody shakes hands with his or her spouse.
        [shakes[p][spouse[p]] == 0 for p in range(n_people)],
        # A handshake is between two people: shakes[p][q] and shakes[q][p] are the same.
        [shakes[p][q] == shakes[q][p] for p in range(n_people) for q in range(p + 1, n_people)],
        # hands[p] counts the handshakes of person p.
        [hands[p] == Sum(shakes[p]) for p in range(n_people)],
        # Jocelyn asks the question, so the answers of everyone except her are all different.
        AllDifferent([hands[p] for p in range(n_people) if p != jocelyn]),
        # Implied: the two hand counts of each invited couple add up to n_people - 2. The
        # answers are all different and span 0 to n_people - 2, so the person with the most
        # hands shook everyone but self and spouse, and the one with none is that spouse;
        # removing such a pair leaves the same pattern for the other couples.
        [hands[p] + hands[p + 1] == n_people - 2 for p in range(2, n_people, 2)],
    )

    # hil is the number of hands Hilary has shaken.
    hil = hands[hilary]

    return {"hil": hil}


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
