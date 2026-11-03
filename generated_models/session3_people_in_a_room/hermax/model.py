# session3_people_in_a_room: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run it (after `pip install hermax`) with:
#   python session3_people_in_a_room.py

from hermax.model import Model

# There are 13 people, 4 of them male, entering a room one at a time. Find an
# order of entry (males and females) such that, at every moment, the ratio of
# females to males in the room is no greater than 7/3.
#
# The data is fixed by the problem statement, so the instance is not read.
N_PEOPLE = 13  # the number of people (the statement fixes it)
N_MALES = 4    # the number of males among them (the statement fixes it)


def create_model(instance):
    """Find an entry order for 13 people, 4 of them male, such that the females-to-males
    ratio in the room is at most 7/3 at every moment."""
    m = Model()

    # sequence[k] is true when the k-th person to enter is female, false when male
    sequence = m.bool_vector("sequence", N_PEOPLE)

    # Exactly 4 of the 13 people are male, so 9 are female.
    m &= (sum(sequence[k] for k in range(N_PEOPLE)) == N_PEOPLE - N_MALES)

    # After the first k+1 entries, with F females and M = (k+1) - F males in the room,
    # the ratio F/M must be at most 7/3, i.e. 3F <= 7M, which is 10F <= 7(k+1).
    # When no male is in the room this forces no female to be there either.
    for k in range(N_PEOPLE):
        females_in_room = sum(sequence[i] for i in range(k + 1))
        m &= (10 * females_in_room <= 7 * (k + 1))

    # No objective: any entry order that satisfies the ratio rule is an answer.
    return m, {"sequence": sequence}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
