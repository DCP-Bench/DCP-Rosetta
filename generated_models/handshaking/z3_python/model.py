# handshaking: a Z3 (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python handshaking.py handshaking.json

import z3


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples for dinner. Everybody
    shakes hands with some of the others, but nobody shakes hands with themselves
    or with their spouse. Jocelyn asks how many hands each person has shaken and
    all the answers are different. How many hands has Hilary shaken?"""
    num_couples = instance["num_couples"]  # the number of couples invited, not counting Hilary and Jocelyn
    n_people = 2 + num_couples * 2         # everybody at the party

    # Hilary is person 0 and Jocelyn is person 1. Persons 2k and 2k + 1 are a married couple.
    def spouses(i, j):
        return i // 2 == j // 2

    # shook[(i, j)] for i < j is true when persons i and j shake hands. A handshake
    # is shared by both people, so each pair has one variable. Nobody shakes hands
    # with themselves or with their spouse, so those pairs have none.
    shook = {}
    for i in range(n_people):
        for j in range(i + 1, n_people):
            if not spouses(i, j):
                shook[(i, j)] = z3.Bool(f"shook_{i}_{j}")

    def hands_of(i):
        # The handshakes person i may take part in.
        return [shook[(min(i, j), max(i, j))]
                for j in range(n_people) if j != i and not spouses(i, j)]

    # has[i][v] is true when person i has shaken exactly v hands. Nobody shakes more
    # than n_people - 2 hands: not their own, and not their spouse's.
    has = [[z3.Bool(f"has_{i}_{v}") for v in range(n_people - 1)] for i in range(n_people)]
    # The number of hands Hilary has shaken, which is the answer.
    hil = z3.Int("hil")

    solver = z3.Solver()

    # Each person has shaken exactly one of the counts from 0 to n_people - 2, and
    # has[i][v] says which one.
    for i in range(n_people):
        shakes = [(h, 1) for h in hands_of(i)]
        for v in range(n_people - 1):
            solver.add(has[i][v] == z3.PbEq(shakes, v))
        solver.add(z3.PbEq([(has[i][v], 1) for v in range(n_people - 1)], 1))

    # Hilary's count is the number of handshakes Hilary takes part in.
    solver.add(hil == z3.Sum([z3.If(h, 1, 0) for h in hands_of(0)]))
    solver.add(hil >= 0, hil <= n_people - 2)

    # Jocelyn and the invited people all gave different answers, so each count from
    # 0 to n_people - 2 is given by exactly one of them.
    for v in range(n_people - 1):
        solver.add(z3.PbEq([(has[i][v], 1) for i in range(1, n_people)], 1))

    # The person who shook n_people - 2 hands shook everybody except their spouse, so
    # that spouse shook no hands. Removing the couple leaves the same party with two
    # people fewer, so each other couple has counts v and n_people - 2 - v. Jocelyn's
    # spouse is Hilary, who is not counted, so Jocelyn has the middle count.
    for i in range(1, n_people):
        s = i + 1 if i % 2 == 0 else i - 1  # the spouse of person i
        for v in range(n_people - 1):
            if v == n_people - 2 - v:
                continue
            if s == 0:
                solver.add(z3.Not(has[i][v]))
            else:
                solver.add(z3.Implies(has[i][v], has[s][n_people - 2 - v]))

    # x[i] is the number of hands person i has shaken.
    x = [z3.Int(f"x_{i}") for i in range(n_people)]
    for i in range(1, n_people):
        for v in range(n_people - 1):
            solver.add(z3.Implies(has[i][v], x[i] == v))

    # The invited couples can be renamed freely, so their order is fixed: within each
    # couple the spouse with the smaller count comes first, and the couples follow in
    # the order of their first spouse's count.
    for k in range(1, num_couples + 1):
        solver.add(x[2 * k] < x[2 * k + 1])
        if k > 1:
            solver.add(x[2 * k - 2] < x[2 * k])

    return solver, {"hil": hil}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
