from hermax.model import Model


def build(instance):
    # Quasigroup completion: complete a partially filled Latin square.
    # A Latin square is an NxN matrix where each row and column contains
    # each number from 1 to N exactly once.

    N = instance["N"]  # Size of the quasigroup
    start = instance["start"]  # Partially filled grid (0 means empty)

    m = Model()

    # puzzle[i][j] is the value (1 to N) at position (i, j)
    puzzle = m.int_matrix("puzzle", N, N, 1, N)

    # Constraint 1: Each row is a permutation of 1 to N
    for i in range(N):
        m &= puzzle.row(i).all_different()

    # Constraint 2: Each column is a permutation of 1 to N
    for j in range(N):
        m &= puzzle.col(j).all_different()

    # Constraint 3: Respect the pre-filled values
    for i in range(N):
        for j in range(N):
            if start[i][j] != 0:
                m &= (puzzle[i][j] == start[i][j])

    return m, {"puzzle": puzzle}
