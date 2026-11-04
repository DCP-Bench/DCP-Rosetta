# session3_people_in_a_room: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install z3-solver numpy`) with:
#   python session3_people_in_a_room.py

import z3


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an order of entry
    such that the ratio of females to males in the room is never more than 7/3."""
    total_people = 13  # the number of people
    num_males = 4      # the number of males among them

    # sequence[i] is true when the i-th person to enter is female, and false when male.
    sequence = z3.BoolVector("sequence", total_people)

    solver = z3.Solver()

    # Exactly num_males of the people are male, so the rest are female.
    solver.add(z3.PbEq([(s, 1) for s in sequence], total_people - num_males))

    # After each entry the females are at most 7/3 of the males. The inequality is
    # written as 3 * females <= 7 * males to avoid the fraction. With nobody in the
    # room there is no ratio, so the check starts after the first entry.
    for i in range(1, total_people):
        females = z3.Sum([z3.If(s, 1, 0) for s in sequence[:i]])  # females among the first i to enter
        males = i - females                                       # males among the first i to enter
        solver.add(3 * females <= 7 * males)

    return solver, {"sequence": sequence}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)
