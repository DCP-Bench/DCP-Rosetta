# handshaking: a Choco-solver (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python handshaking.py handshaking.json

from pychoco.model import Model


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples for dinner. Everybody
    shakes hands with some of the others, but nobody shakes hands with themselves
    or with their spouse. Jocelyn asks how many hands each person has shaken and
    all the answers are different. How many hands has Hilary shaken?"""
    num_couples = instance["num_couples"]  # the number of couples invited, not counting Hilary and Jocelyn

    # The people are Hilary (person 0), Jocelyn (person 1) and then each invited
    # couple in turn: persons 2 and 3, persons 4 and 5, and so on. Person 2k and
    # person 2k+1 are spouses, so the spouse of person i is person i ^ 1.
    n_people = 2 + num_couples * 2

    model = Model()

    # shakes[(i, j)] is true when persons i and j shake hands, for i < j and j not the
    # spouse of i. A handshake is mutual, so one variable covers both directions.
    shakes = {}
    for i in range(n_people):
        for j in range(i + 1, n_people):
            if j != (i ^ 1):
                shakes[(i, j)] = model.boolvar(name=f"shakes_{i}_{j}")

    # hands[i] is the number of hands person i has shaken. Nobody shakes their own
    # hand or their spouse's, so it is at most n_people - 2.
    hands = [model.intvar(0, n_people - 2, name=f"hands_{i}") for i in range(n_people)]

    # Each person's hand count is the number of handshakes they take part in.
    for i in range(n_people):
        model.sum([shakes[(min(i, j), max(i, j))] for j in range(n_people) if j != i and j != (i ^ 1)],
                  "=", hands[i]).post()

    # Everybody except Hilary has a different number of hands.
    model.all_different(hands[1:]).post()

    # Couples can be renamed and spouses swapped without changing Hilary's count, so
    # only one arrangement is kept: in each invited couple the first person has more
    # hands than the second, and each couple's first person has more hands than the
    # first person of the couple after it.
    for couple in range(1, num_couples + 1):
        first, second = 2 * couple, 2 * couple + 1
        model.arithm(hands[first], ">", hands[second]).post()
        if couple < num_couples:
            model.arithm(hands[first], ">", hands[first + 2]).post()

    # Hilary's number of hands is the answer.
    return model, {"hil": hands[0]}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")
