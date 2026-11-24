# session3_people_in_a_room: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python session3_people_in_a_room.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an order in
    which the males and females enter so that the ratio of females to males in
    the room is at most 7/3 at any one time. The output gives the sex of the
    person at each position of the order, 0 for male and 1 for female.

    The instance file is empty ([]): the statement fixes every number used here,
    so the instance argument is not read."""
    n = 13  # the number of people, from the statement
    males = 4  # the number of male people, from the statement
    females = n - males  # the number of female people: 9

    model = Model("session3_people_in_a_room")

    # sequence[t] is 1 when the person at position t of the order is female,
    # and 0 when that person is male
    sequence = [model.addVar(name=f"female_{t}", vtype="B") for t in range(n)]

    # Everyone enters, so exactly 9 females and 4 males appear in the order.
    model.addCons(quicksum(sequence) == females)

    # After the first t people have entered, the room holds in_room females and
    # t - in_room males. The ratio in_room / (t - in_room) is at most 7/3, which
    # is written without a division as 3 * in_room <= 7 * males_in_room. With no
    # males in the room this allows no females either, so the first person is male.
    # After all 13 have entered the room holds 9 females and 4 males, a ratio of
    # 9/4 < 7/3, so the last entrance needs no constraint and the loop stops at 12.
    for t in range(1, n):
        in_room = quicksum(sequence[:t])
        model.addCons(3 * in_room <= 7 * (t - in_room))

    # Satisfaction problem: any order that meets the ratio rule is a solution,
    # so no objective is set.

    return model, {"sequence": sequence}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())
