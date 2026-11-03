"""Maximum density still life: the most live cells in an n x m Life pattern that does not change."""
import hexaly.optimizer as hx


def build(instance):
    n, m = instance["n"], instance["m"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # grid[i][j] = 1 if the cell is alive; cells outside the active grid are dead
    grid = [[model.bool() for _ in range(m)] for _ in range(n)]

    def neighbours(i, j):
        """The live neighbours of cell (i, j), which may lie one step outside the grid."""
        return [grid[a][b] for a in range(i - 1, i + 2) for b in range(j - 1, j + 2)
                if (a, b) != (i, j) and 0 <= a < n and 0 <= b < m]

    for i in range(-1, n + 1):
        for j in range(-1, m + 1):
            around = neighbours(i, j)
            if len(around) < 3:
                continue  # fewer than three possible neighbours: no dead cell here can come alive
            count = model.sum(around)
            if 0 <= i < n and 0 <= j < m:
                alive = grid[i][j]
                # A live cell keeps living with exactly 2 or 3 live neighbours
                model.constraint(count >= 2 * alive)
                model.constraint(count + 5 * alive <= 8)
                # A dead cell must not have exactly 3 live neighbours
                model.constraint(model.or_(alive == 1, count != 3))
            else:
                # A dead cell just outside the grid must not come alive either
                model.constraint(count != 3)

    # Maximise the number of live cells
    model.maximize(model.sum(grid[i][j] for i in range(n) for j in range(m)))
    return optimizer, {"grid": grid}
