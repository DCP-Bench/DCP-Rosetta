# session3_people_in_a_room: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install cvc5 numpy`) with:
#   python session3_people_in_a_room.py

import cvc5.pythonic as c5


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an entry order such that
    the ratio of females to males in the room is never above 7/3."""
    n_people = 13                         # the number of people
    n_males = 4                           # the number of males among them
    n_females = n_people - n_males        # the number of females among them

    # sequence[i] is true when the i-th person to enter is female
    sequence = [c5.Bool(f"sequence_{i}") for i in range(n_people)]

    solver = c5.Solver()

    # Exactly n_females of the people are female.
    solver.add(c5.Sum([c5.If(female, 1, 0) for female in sequence]) == n_females)

    # After each entry, the females among the people in the room are at most 7/3 of the males.
    # Written without fractions: 3 times the females is at most 7 times the males.
    for t in range(1, n_people + 1):
        females = c5.Sum([c5.If(female, 1, 0) for female in sequence[:t]])
        males = t - females
        solver.add(3 * females <= 7 * males)

    return solver, {"sequence": sequence}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)
