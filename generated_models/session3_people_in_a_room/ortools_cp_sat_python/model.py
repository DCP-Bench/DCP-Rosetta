# session3_people_in_a_room: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install ortools`) with:
#   python session3_people_in_a_room.py

from ortools.sat.python import cp_model


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an entry order
    such that the ratio of females to males in the room is never above 7/3."""
    n_people = 13  # the number of people
    n_males = 4    # the number of males among them

    model = cp_model.CpModel()

    # sequence[i] is true when the i-th person to enter is female
    sequence = [model.new_bool_var(f"sequence_{i}") for i in range(n_people)]

    # n_males of the people are male, so the others are female.
    model.add(sum(sequence) == n_people - n_males)

    # After each entry, the females are at most 7 / 3 of the males.
    for i in range(1, n_people):
        # females and males among the first i people to enter
        females = sum(sequence[:i])
        males = i - females
        model.add(3 * females <= 7 * males)

    return model, {"sequence": sequence}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))
