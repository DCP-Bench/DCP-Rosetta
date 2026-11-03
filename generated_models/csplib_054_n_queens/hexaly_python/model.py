"""n-queens: place n queens on an n x n board so that no two share a row, a column or a diagonal."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n"]  # n = the board is n x n and carries n queens
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # queens[i] = the column (1..n) of the queen on row i; one queen per row by construction,
    # so no two queens can share a row
    queens = [model.int(1, n) for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            # No two queens share a column
            model.constraint(queens[i] != queens[j])
            # No two queens share a diagonal in either direction: queens[i] + i is constant along
            # one diagonal direction, queens[i] - i along the other
            model.constraint(queens[i] + i != queens[j] + j)
            model.constraint(queens[i] - i != queens[j] - j)

    return optimizer, {"queens": queens}
