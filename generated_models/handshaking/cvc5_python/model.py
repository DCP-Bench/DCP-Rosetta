# handshaking: a cvc5 (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python handshaking.py handshaking.json

import cvc5.pythonic as c5


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples who are friends. At dinner,
    everyone shakes hands with some of the others, but nobody shakes hands with themselves
    or with their spouse. Jocelyn asks each person except herself how many hands they have
    shaken, and all the answers are different. How many hands has Hilary shaken?"""
    n = instance["num_couples"]  # the number of couples Hilary and Jocelyn invite

    # The most hands one person can shake: everyone except themselves and their spouse.
    top = 2 * n
    # The answers are 0 to top. Jocelyn asks the 2n + 1 people other than herself, and
    # their answers are all different, so each answer is given by exactly one person.
    # ranks[r] is the person who answers r.
    ranks = list(range(top + 1))

    # shake[(r, t)] is true when the person answering r and the person answering t shake
    # hands, for each pair with r < t. Nobody shakes their own hand.
    shake = {(r, t): c5.Bool(f"shake_{r}_{t}") for r in ranks for t in ranks if r < t}

    def shakes(r, t):
        return shake[(min(r, t), max(r, t))]

    # shakes_jocelyn[r] is true when the person answering r shakes hands with Jocelyn.
    shakes_jocelyn = [c5.Bool(f"shakes_jocelyn_{r}") for r in ranks]

    # spouse[(r, t)] is true when the people answering r and t are married to each other,
    # for each pair with r < t.
    spouse = {(r, t): c5.Bool(f"spouse_{r}_{t}") for r in ranks for t in ranks if r < t}

    def married(r, t):
        return spouse[(min(r, t), max(r, t))]

    # is_hilary[r] is true when the person answering r is Hilary, who is married to Jocelyn.
    is_hilary = [c5.Bool(f"is_hilary_{r}") for r in ranks]

    # Exactly one of the conditions in lits holds.
    def exactly_one(lits):
        return [c5.Or(lits)] + [c5.Not(c5.And(a, b))
                                for x, a in enumerate(lits) for b in lits[x + 1:]]

    solver = c5.Solver()

    # Nobody shakes hands with his or her spouse.
    solver.add([c5.Implies(sp, c5.Not(shake[pair])) for pair, sp in spouse.items()])
    # Hilary does not shake hands with Jocelyn, her spouse.
    solver.add([c5.Implies(h, c5.Not(j)) for h, j in zip(is_hilary, shakes_jocelyn)])

    # Exactly one person is Hilary.
    solver.add(exactly_one(is_hilary))
    # Everyone is married to exactly one other person, and Hilary is married to Jocelyn.
    for r in ranks:
        solver.add(exactly_one([married(r, t) for t in ranks if t != r] + [is_hilary[r]]))

    # The person answering r has shaken exactly r hands, with the others or with Jocelyn.
    for r in ranks:
        # one entry for each handshake of this person
        handshakes = [c5.If(shakes(r, t), 1, 0) for t in ranks if t != r]
        handshakes.append(c5.If(shakes_jocelyn[r], 1, 0))
        solver.add(c5.Sum(handshakes) == r)

    # The answer: the number of hands of whoever is Hilary.
    hil = c5.Sum([c5.If(is_hilary[r], r, 0) for r in ranks])

    # The conditions use only sums and comparisons of whole numbers.
    return solver, {"hil": hil}


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
