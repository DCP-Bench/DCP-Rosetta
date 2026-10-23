from hermax.model import Model


def build(instance):
    """
    Initials queue problem: assign alphabetically ordered pairs of distinct letters
    from A-E (0-4) to 10 people in a queue.

    Constraints:
    1. Each person has initials (first < second)
    2. All initials are distinct
    3. No two adjacent people share a letter
    4. BE (1,4) is at position 0 (front)
    5. CD (2,3) is at position 1
    6. BD (1,3) is at position 9 (end)
    """
    m = Model()

    # queue[i][0] and queue[i][1] are the two initials for person i
    # Both must be from 0-4, with queue[i][0] < queue[i][1]
    queue = m.int_matrix("queue", 10, 2, 0, 4)

    # Constraint: each person's initials are alphabetically ordered
    for i in range(10):
        m &= (queue[i, 0] < queue[i, 1])

    # Constraint: all initials are distinct (as pairs)
    # We need to ensure that the 10 pairs are all different
    # We encode each pair as a single number: first * 5 + second
    pair_values = m.int_vector("pair_values", 10, 0, 24)
    for i in range(10):
        m &= (pair_values[i] == queue[i, 0] * 5 + queue[i, 1])

    # All pair values must be distinct
    m &= pair_values.all_different()

    # Constraint: no two adjacent people share a letter
    for i in range(9):
        # queue[i] and queue[i+1] must not share a letter
        # This means: not (queue[i][0] == queue[i+1][0] or queue[i][0] == queue[i+1][1] or
        #                   queue[i][1] == queue[i+1][0] or queue[i][1] == queue[i+1][1])
        m &= (queue[i, 0] != queue[i+1, 0])
        m &= (queue[i, 0] != queue[i+1, 1])
        m &= (queue[i, 1] != queue[i+1, 0])
        m &= (queue[i, 1] != queue[i+1, 1])

    # Constraint: BE (1,4) is at position 0
    m &= (queue[0, 0] == 1)
    m &= (queue[0, 1] == 4)

    # Constraint: CD (2,3) is at position 1
    m &= (queue[1, 0] == 2)
    m &= (queue[1, 1] == 3)

    # Constraint: BD (1,3) is at position 9
    m &= (queue[9, 0] == 1)
    m &= (queue[9, 1] == 3)

    return m, {"queue": queue}
