# session3_people_in_a_room: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python session3_people_in_a_room.py

from pycsp3 import *


def create_model(instance):
    """13 people, 4 of them male, enter a room one at a time. Find an order of entry in which
    the ratio of females to males in the room is never greater than 7/3 at any time."""
    n_people = 13  # the people who enter the room
    n_males = 4  # how many of them are male
    n_females = n_people - n_males  # the rest of the people are female
    max_ratio_numerator = 7  # the ratio of females to males is at most 7 / 3
    max_ratio_denominator = 3

    # sequence[k] is 1 when the (k + 1)-th person to enter is female, 0 when male
    sequence = VarArray(size=n_people, dom={0, 1})

    satisfy(
        # The room ends with n_females females, so n_males males.
        Sum(sequence) == n_females,
        # At any time, after the first n_entered people have entered, the females are at most
        # 7 / 3 of the males, written without a division. With no males in the room there
        # can be no females, so the first person to enter is male.
        [
            max_ratio_denominator * Sum(sequence[:n_entered])
            <= max_ratio_numerator * (n_entered - Sum(sequence[:n_entered]))
            for n_entered in range(1, n_people + 1)
        ],
    )

    return {"sequence": sequence}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())
