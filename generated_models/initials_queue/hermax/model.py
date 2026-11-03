# initials_queue: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install hermax`) with:
#   python initials_queue.py

from hermax.model import Model


def create_model(instance):
    """Find the initials of ten people in a queue for a Maths lecture. Each person's
    initials are an alphabetically ordered pair of distinct letters from A to E (0 to 4),
    and no two people share the same initials. No one shares a letter with the person
    in front of them. BE is at the front, CD is second and BD is last."""
    # The instance has no fields: the queue size, the letters and the clues are all
    # fixed by the statement.
    n = 10          # the number of people in the queue
    letters = 5     # the letters A..E, coded 0..4

    m = Model()

    # queue[i][0] and queue[i][1] are the two letters of the i-th person from the front,
    # with the first letter before the second in the alphabet
    queue = m.int_matrix("queue", n, 2, 0, letters - 1)

    # initials_code[i] = 5 * first letter + second letter. Since the second letter is
    # below 5, the code identifies the pair, so distinct codes mean distinct initials.
    initials_code = m.int_vector("initials_code", n, 0, 24)

    # Each person's letters are in alphabetical order and distinct: first < second.
    for i in range(n):
        m &= (queue[i][0] + 1 <= queue[i][1])

    # Each person's initials code is that pair's code.
    for i in range(n):
        m &= (initials_code[i] == 5 * queue[i][0] + queue[i][1])

    # Nobody has the same initials as anybody else.
    m &= initials_code.all_different()

    # No one shares a letter with the person in front: the four letters of two
    # consecutive people are all different.
    for i in range(n - 1):
        m &= m.vector([queue[i][0], queue[i][1], queue[i + 1][0], queue[i + 1][1]]).all_different()

    # BE is at the front: letters B (1) and E (4).
    m &= (queue[0][0] == 1)
    m &= (queue[0][1] == 4)
    # CD is right behind: letters C (2) and D (3).
    m &= (queue[1][0] == 2)
    m &= (queue[1][1] == 3)
    # BD is right at the end: letters B (1) and D (3).
    m &= (queue[n - 1][0] == 1)
    m &= (queue[n - 1][1] == 3)

    return m, {"queue": queue}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)
