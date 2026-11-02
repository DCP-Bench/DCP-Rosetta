# handshaking: a PuLP (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python handshaking.py handshaking.json

import pulp


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples to dinner. Everybody shakes
    hands with some of the others, but nobody shakes hands with themselves or with their
    own spouse. Everyone except Hilary has shaken a different number of hands. How many
    hands has Hilary shaken?"""
    # The number of couples invited, not counting Hilary and Jocelyn.
    num_couples = instance["num_couples"]

    # The number of people. Hilary is person 0, Jocelyn is person 1, and each invited
    # couple is a pair of persons 2k and 2k + 1.
    n_people = 2 + num_couples * 2
    # The numbers of hands a person can have, from 0 up to n_people - 2, since nobody
    # shakes hands with themselves or with their spouse.
    hand_counts = range(n_people - 1)

    problem = pulp.LpProblem("handshaking", pulp.LpMinimize)

    # has[i][r] is 1 when person i has shaken r hands, and 0 when not. Hilary is left out.
    has = pulp.LpVariable.dicts("has", (range(1, n_people), hand_counts), cat="Binary")

    # shake[r, s] is 1 when the person with r hands and the person with s hands shake
    # hands, and 0 when not. A handshake involves two people, so each pair is listed once.
    shake = {(r, s): pulp.LpVariable(f"shake_{r}_{s}", cat="Binary")
             for r in hand_counts for s in hand_counts if r < s}

    # The handshake between the people with r and s hands, in either order.
    def together(r, s):
        return shake[(min(r, s), max(r, s))]

    # shake_hil[r] is 1 when Hilary shakes hands with the person who has r hands, and 0 when not.
    shake_hil = [pulp.LpVariable(f"shake_hil_{r}", cat="Binary") for r in hand_counts]

    # Each person other than Hilary has one number of hands.
    for i in range(1, n_people):
        problem += pulp.lpSum(has[i][r] for r in hand_counts) == 1

    # All of them have different numbers, so each number of hands is held by exactly one of them.
    for r in hand_counts:
        problem += pulp.lpSum(has[i][r] for i in range(1, n_people)) == 1

    # The person with r hands shakes hands with exactly r others, Hilary included.
    for r in hand_counts:
        problem += pulp.lpSum(together(r, s) for s in hand_counts if s != r) + shake_hil[r] == r

    # A couple does not shake hands with itself: if one spouse has r hands and the other
    # has s hands, the people with r and s hands do not shake hands.
    for k in range(1, num_couples + 1):
        for r in hand_counts:
            for s in hand_counts:
                if r != s:
                    problem += together(r, s) + has[2 * k][r] + has[2 * k + 1][s] <= 2

    # Hilary does not shake hands with Jocelyn.
    for r in hand_counts:
        problem += shake_hil[r] + has[1][r] <= 1

    # hil is the number of hands Hilary has shaken.
    hil = pulp.LpVariable("hil", 0, n_people - 2, cat="Integer")
    problem += hil == pulp.lpSum(shake_hil)

    return problem, {"hil": hil}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])
