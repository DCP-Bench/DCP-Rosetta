"""Magic hexagon: the numbers 1..19 in a hexagon so that all 15 lines of cells add up to the magic sum."""
import hexaly.optimizer as hx

# The cells A..S, in rows of 3, 4, 5, 4 and 3, are numbered 0..18 reading left to right, top to bottom
ROWS = [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18]]
# The diagonals running down to the left and down to the right
DOWN_LEFT = [[0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18]]
DOWN_RIGHT = [[2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16]]


def build(instance):
    cells, magic = instance["NUM_CELLS"], instance["MAGIC_SUM"]  # the number of cells, and the sum of every line
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[c][v] = 1 if cell c holds the number v + 1. Booleans with linear sums give Hexaly bounds that a
    # permutation of numbers compared through sums does not.
    has = [[model.bool() for _ in range(cells)] for _ in range(cells)]
    # Every cell holds one number, and every number from 1 to 19 is used once
    for c in range(cells):
        model.constraint(model.sum(has[c]) == 1)
        model.constraint(model.sum(has[k][c] for k in range(cells)) == 1)

    LD = [model.sum((v + 1) * has[c][v] for v in range(cells)) for c in range(cells)]  # the number in each cell
    # Every one of the 15 lines adds up to the magic sum
    for line in ROWS + DOWN_LEFT + DOWN_RIGHT:
        model.constraint(model.sum(LD[i] for i in line) == magic)

    return optimizer, {"LD": LD}
