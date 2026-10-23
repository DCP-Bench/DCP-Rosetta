from hermax.model import Model


def build(instance):
    """Hidato puzzle solver.

    Fill 12x12 grid with numbers 1-144 where:
    - Consecutive numbers are adjacent (horizontally, vertically, diagonally)
    - Respect given clue numbers
    """
    puzzle = instance["puzzle"]
    size = len(puzzle)
    max_num = size * size

    model = Model()

    # Variables: x[i][j] = number at position (i,j)
    x = model.int_matrix("x", size, size, 1, max_num)

    # Constraint: respect given puzzle clues
    for i in range(size):
        for j in range(size):
            if puzzle[i][j] > 0:
                model &= (x[i][j] == puzzle[i][j])

    # Constraint: all different numbers (1 to 144)
    model &= x.flatten().all_different()

    # Constraint: consecutive numbers must be adjacent
    # For each number k from 1 to 143, find where k and k+1 are placed
    # and ensure they are adjacent (including diagonals)
    for k in range(1, max_num):
        # Create auxiliary variables for positions of k and k+1
        pos_k = []  # Positions where value is k
        pos_k1 = []  # Positions where value is k+1

        for i in range(size):
            for j in range(size):
                # pos_k: (i,j) contains k
                is_k = model.bool(f"is_k_{k}_{i}_{j}")
                model &= (is_k == (x[i][j] == k))
                pos_k.append((i, j, is_k))

                # pos_k1: (i,j) contains k+1
                is_k1 = model.bool(f"is_k1_{k}_{i}_{j}")
                model &= (is_k1 == (x[i][j] == k + 1))
                pos_k1.append((i, j, is_k1))

        # Constraint: k and k+1 must be adjacent
        # At least one pair must be adjacent
        adjacent_pairs = []
        for i_k, j_k, is_k in pos_k:
            for i_k1, j_k1, is_k1 in pos_k1:
                # Check if (i_k, j_k) and (i_k1, j_k1) are adjacent
                if abs(i_k - i_k1) <= 1 and abs(j_k - j_k1) <= 1 and not (i_k == i_k1 and j_k == j_k1):
                    # They're adjacent
                    adjacent = model.bool(f"adj_{k}_{i_k}_{j_k}_{i_k1}_{j_k1}")
                    model &= (adjacent == (is_k & is_k1))
                    adjacent_pairs.append(adjacent)

        # At least one adjacent pair must be true
        if adjacent_pairs:
            model &= (sum(adjacent_pairs) >= 1)

    return model, {"x": x}
