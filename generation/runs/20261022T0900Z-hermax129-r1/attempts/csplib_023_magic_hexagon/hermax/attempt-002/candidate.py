from hermax.model import Model


def build(instance):
    # Magic Hexagon: Arrange numbers 1-19 in a hexagonal grid such that
    # each of the 15 lines (rows and diagonals) sums to the magic constant.

    # The hexagon structure:
    #       A,  B,  C       (indices 0, 1, 2)
    #      D,  E,  F,  G    (indices 3, 4, 5, 6)
    #     H,  I,  J,  K,  L (indices 7, 8, 9, 10, 11)
    #      M,  N,  O,  P    (indices 12, 13, 14, 15)
    #       Q,  R,  S       (indices 16, 17, 18)

    magic_sum = instance["MAGIC_SUM"]  # Should be 38
    num_cells = instance["NUM_CELLS"]  # Should be 19

    m = Model()

    # Create 19 variables with values 1 to 19
    hexagon = m.int_vector("LD", num_cells, 1, num_cells)

    # Constraint: all values must be distinct (1 to 19 each used once)
    m &= hexagon.all_different()

    # Define the 15 line constraints
    # Lines are defined by the indices of cells that should sum to magic_sum

    lines = [
        # Horizontal lines (5 lines)
        [0, 1, 2],                    # A, B, C
        [3, 4, 5, 6],                 # D, E, F, G
        [7, 8, 9, 10, 11],            # H, I, J, K, L
        [12, 13, 14, 15],             # M, N, O, P
        [16, 17, 18],                 # Q, R, S

        # Diagonal lines (one direction) - going down-left
        [0, 3, 7],                    # A, D, H
        [1, 4, 8, 12],                # B, E, I, M
        [2, 5, 9, 13, 16],            # C, F, J, N, Q
        [6, 10, 14, 17],              # G, K, O, R
        [11, 15, 18],                 # L, P, S

        # Diagonal lines (other direction) - going down-right
        [2, 6, 11],                   # C, G, L
        [1, 5, 10, 15],               # B, F, K, P
        [0, 4, 9, 14, 18],            # A, E, J, O, S
        [3, 8, 13, 17],               # D, I, N, R
        [7, 12, 16],                  # H, M, Q
    ]

    # Add constraints: each line sums to magic_sum
    for line_indices in lines:
        line_sum = sum(hexagon[i] for i in line_indices)
        m &= (line_sum == magic_sum)

    return m, {"LD": hexagon}
