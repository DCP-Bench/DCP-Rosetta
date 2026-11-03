# session3_people_in_a_room: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install exact numpy`) with:
#   python session3_people_in_a_room.py

from exact import Exact


def create_model(instance):
    """Thirteen people, four of them male, enter a room one at a time. Find an order
    of entry in which the ratio of females to males in the room is never more than
    7 to 3."""
    total_people = 13                # the people who enter the room
    num_males = 4                    # the males among them; the others are female
    ratio_females, ratio_males = 7, 3  # at any time, females : males is at most 7 : 3

    solver = Exact()

    # Exact identifies its variables by name.
    # sequence[i] is 1 when the i-th person to enter is female, and 0 when male
    sequence = [f"sequence_{i}" for i in range(total_people)]
    for name in sequence:
        solver.addVariable(name, 0, 1)

    # Nine of the thirteen people are female.
    females = total_people - num_males
    solver.addConstraint([(1, name) for name in sequence], True, females, True, females)

    # After the first i people have entered, with F of them female and i - F male, the ratio
    # F : (i - F) is at most 7 : 3. Written without a fraction, that is 10 F <= 7 i.
    for i in range(1, total_people):
        solver.addConstraint([(ratio_males + ratio_females, name) for name in sequence[:i]],
                             False, 0, True, ratio_females * i)

    return solver, {"sequence": sequence}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")
