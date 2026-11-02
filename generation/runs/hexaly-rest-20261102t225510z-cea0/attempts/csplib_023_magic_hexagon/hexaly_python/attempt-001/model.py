"""Magic hexagon: the numbers 1..19 in a hexagon so that all 15 lines of cells add up to the magic sum."""
import hexaly.optimizer as hx

# The cells A..S, in rows of 3, 4, 5, 4 and 3, are numbered 0..18 reading left to right, top to bottom
ROWS = [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18]]
# The diagonals running down to the left and down to the right (each with a row of the hexagon's shape)
DOWN_LEFT = [[0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18]]
DOWN_RIGHT = [[2, 6, 11], [1, 5, 10, 15], [0, 4, 9, 14, 18], [3, 8, 13, 17], [7, 12, 16]]


def build(instance):
    cells, magic = instance["NUM_CELLS"], instance["MAGIC_SUM"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The cells hold 1..19, each once: a full list decision
    perm = model.list(cells)
    model.constraint(model.count(perm) == cells)
    LD = [perm[i] + 1 for i in range(cells)]

    # Every one of the 15 lines adds up to the magic sum
    for line in ROWS + DOWN_LEFT + DOWN_RIGHT:
        model.constraint(model.sum(LD[i] for i in line) == magic)

    return optimizer, {"LD": LD}
