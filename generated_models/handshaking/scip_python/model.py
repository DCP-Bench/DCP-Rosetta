# handshaking: a SCIP (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python handshaking.py handshaking.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Halmos's handshaking puzzle. Hilary and Jocelyn are married and invite some
    couples, who are friends, to dinner. Everyone shakes hands with everyone except
    themselves and their own spouse. Jocelyn then asks every person but herself how
    many hands they have shaken, and all the answers are different. Find how many
    hands Hilary has shaken.

    The output hil is the number of hands Hilary has shaken.
    """
    # num_couples: the number of couples that Hilary and Jocelyn invite. Hilary and
    # Jocelyn are a married couple too, so the party has num_couples + 1 couples.
    couples = instance["num_couples"] + 1
    # Persons 2c and 2c+1 are the two spouses of couple c. Couple 0 is Hilary and
    # Jocelyn, so Hilary is person 0 and Jocelyn is person 1.
    people = 2 * couples
    HILARY, JOCELYN = 0, 1
    # Nobody shakes hands with self or with spouse, so each person shakes at most
    # people - 2 hands. The hand counts, and so the answers, lie in 0..max_hands.
    max_hands = people - 2

    model = Model("handshaking")

    # shake[i, j] is 1 when persons i and j shake hands, and 0 when they do not.
    # A handshake involves two people, so shake is symmetric.
    shake = model.addMatrixVar((people, people), vtype="B", name="shake")
    model.addMatrixCons(shake == shake.T)  # a handshake is between two people
    # Nobody shakes hands with themselves (the diagonal is 0)...
    for i in range(people):
        model.addCons(shake[i, i] == 0)
    # ...or with their spouse, who is the other person of the same couple.
    for c in range(couples):
        model.addCons(shake[2 * c, 2 * c + 1] == 0)

    # hands[p] is the number of hands person p has shaken.
    hands = shake.sum(axis=1)

    # Jocelyn asks everyone but herself, so the people asked are all persons except
    # Jocelyn. asked[r] is the person who gives the r-th answer.
    asked = [p for p in range(people) if p != JOCELYN]
    # answer[r, v] is 1 when the r-th person asked answers v hands, and 0 when not.
    # SCIP has no all-different constraint, so distinct answers are encoded with
    # one-hot binaries: each person gives exactly one answer, and each value 0..max_hands
    # is given by exactly one person. There are as many values as people asked.
    answer = model.addMatrixVar((len(asked), max_hands + 1), vtype="B", name="answer")
    model.addMatrixCons(answer.sum(axis=1) == 1)  # each person asked gives one answer
    model.addMatrixCons(answer.sum(axis=0) == 1)  # all the answers are different
    # Each person Jocelyn asks answers their true number of hands. The answer of row r
    # is the value v with answer[r, v] = 1, so it is the sum of v * answer[r, v].
    model.addMatrixCons(hands[asked] == answer @ np.arange(max_hands + 1))

    # Known consequence of the distinct answers in Halmos's handshake puzzle: the two
    # spouses of each couple together shook max_hands hands. It is implied by the
    # answers, so it does not change the solutions; it is kept because without it the
    # search for a further solution is too slow.
    for c in range(couples):
        model.addCons(hands[2 * c] + hands[2 * c + 1] == max_hands)

    # hil: Hilary's number of hands, as its own integer variable equal to hands[HILARY].
    # A solver that looks for a second solution must exclude the values of the variables an
    # output is built from. A sum over a whole row of binaries has many assignments with
    # the same value, so the search is slow; one integer variable excludes one value.
    hil = model.addVar(vtype="I", lb=0, ub=max_hands, name="hil")
    model.addCons(hil == hands[HILARY])

    return model, {"hil": hil}


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
