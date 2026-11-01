# session3_people_in_a_room: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install cpmpy`) with:
#   python session3_people_in_a_room.py

import cpmpy as cp


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an entry order
    such that the ratio of females to males in the room is never above 7/3."""
    # The problem fixes its own data, so the instance is not read.
    num_people = 13
    num_males = 4

    # sequence[i] is true when the i-th person to enter is female (false: male)
    sequence = cp.boolvar(shape=num_people, name="sequence")

    model = cp.Model()
    # Exactly num_males of the people are male.
    model.add(cp.sum(sequence) == num_people - num_males)

    # After each entry, females / males <= 7/3, written as 3 * females <= 7 * males
    # to avoid the fraction. Prefix 0 is skipped: with no one in the room there is no ratio.
    for i in range(1, num_people):
        females = cp.sum(sequence[:i])  # females among the first i people to enter
        males = i - females             # males among the first i people to enter
        model.add(3 * females <= 7 * males)

    return model, {"sequence": sequence}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())
