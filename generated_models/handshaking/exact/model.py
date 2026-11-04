# handshaking: an Exact (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python handshaking.py handshaking.json

from exact import Exact


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples for dinner. Everybody shakes hands
    with some of the others, but nobody shakes hands with themselves or with their spouse.
    Jocelyn asks how many hands each person has shaken, and all the answers are different.
    How many hands has Hilary shaken?"""
    num_couples = instance["num_couples"]  # the number of couples invited, not counting Hilary and Jocelyn
    n_people = 2 + 2 * num_couples         # Hilary, Jocelyn and the two members of each invited couple

    solver = Exact()

    # Exact identifies its variables by name.
    # shakes[i, j] is 1 when persons i and j shake hands, for each pair with i < j. Spouses
    # never shake hands, so they get no variable.
    shakes = {}
    for i in range(n_people):
        for j in range(i + 1, n_people):
            if not (i % 2 == 0 and j == i + 1):
                shakes[i, j] = f"shakes_{i}_{j}"
                solver.addVariable(shakes[i, j], 0, 1)

    # hands[i] is the number of hands person i has shaken. Nobody shakes their own hand or
    # their spouse's, so at most n_people - 2.
    hands = [f"hands_{i}" for i in range(n_people)]
    for i in range(n_people):
        solver.addVariable(hands[i], 0, n_people - 2)
        # The handshakes that person i takes part in.
        handshakes = [(1, name) for (a, b), name in shakes.items() if i in (a, b)]
        # hands[i] counts them.
        solver.addConstraint(handshakes + [(-1, hands[i])], True, 0, True, 0)

    # answer_is[i, v] is 1 when person i answers v to Jocelyn's question, for everybody but Hilary.
    answer_is = {(i, v): f"answer_{i}_is_{v}" for i in range(1, n_people) for v in range(n_people - 1)}
    for i in range(1, n_people):
        for v in range(n_people - 1):
            solver.addVariable(answer_is[i, v], 0, 1)
        # Each person gives exactly one answer.
        solver.addConstraint([(1, answer_is[i, v]) for v in range(n_people - 1)], True, 1, True, 1)
        # The answer is the number of hands the person has shaken.
        solver.addConstraint([(v, answer_is[i, v]) for v in range(1, n_people - 1)] + [(-1, hands[i])],
                             True, 0, True, 0)
    # Everybody except Hilary gives a different answer.
    for v in range(n_people - 1):
        solver.addConstraint([(1, answer_is[i, v]) for i in range(1, n_people)], False, 0, True, 1)

    for couple in range(1, num_couples + 1):
        # The two spouses of a couple have different answers, so the first one has shaken more hands.
        solver.addConstraint([(1, hands[2 * couple]), (-1, hands[2 * couple + 1])], True, 1, False, 0)
        if couple > 1:
            # The couples are listed by the hands of their first member, largest first.
            solver.addConstraint([(1, hands[2 * couple - 2]), (-1, hands[2 * couple])], True, 1, False, 0)

    # Hilary's hands.
    return solver, {"hil": hands[0]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
