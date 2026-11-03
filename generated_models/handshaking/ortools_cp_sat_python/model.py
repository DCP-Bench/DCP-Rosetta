# handshaking: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `handshaking.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
# Then run it on the first instance (after `pip install ortools`):
#   python handshaking.py handshaking.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Hilary and Jocelyn are married and invite some couples for dinner. Everybody
    shakes hands with some of the others, but nobody shakes hands with themselves
    or with their spouse. Jocelyn asks how many hands each person has shaken and
    all the answers are different. How many hands has Hilary shaken?"""
    num_couples = instance["num_couples"]  # the number of couples invited

    # The people are Hilary (person 0), Jocelyn (person 1) and then each invited
    # couple in turn: persons 2 and 3, persons 4 and 5, and so on. Person 2k and
    # person 2k+1 are spouses.
    n_people = 2 + num_couples * 2

    model = cp_model.CpModel()

    # hands[i] is the number of hands person i has shaken, from 0 up to n_people - 2,
    # since nobody shakes their own or their spouse's hand
    hands = [model.new_int_var(0, n_people - 2, f"hands_{i}") for i in range(n_people)]
    # hil is the number of hands Hilary has shaken
    hil = hands[0]
    # shaken[i][j] is true when person i and person j shake hands. Pairs inside one
    # couple, including a person with themselves, are fixed at 0.
    shaken = [[model.new_int_var(0, 0, f"shaken_{i}_{j}") if i // 2 == j // 2
               else model.new_bool_var(f"shaken_{i}_{j}")
               for j in range(n_people)] for i in range(n_people)]

    # Shaking hands is mutual.
    for i in range(n_people):
        for j in range(n_people):
            model.add(shaken[i][j] == shaken[j][i])

    # Count the handshakes of each person.
    for i in range(n_people):
        model.add(hands[i] == sum(shaken[i]))

    # Everybody except Hilary gave a different answer.
    model.add_all_different(hands[1:])

    return model, {"hil": hil}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
