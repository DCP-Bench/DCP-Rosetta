from hermax.model import Model


def build(instance):
    n = instance["n"]
    N = n * n

    m = Model()

    # The n*n cells hold distinct integers 1 .. n^2.
    v = m.int_vector("v", N, 1, N)
    m &= v.all_different()
    grid = [[v[i * n + j] for j in range(n)] for i in range(n)]

    # Line sums: n rows, n columns, and the two diagonals.
    lines = []
    for i in range(n):
        lines.append(sum(grid[i][j] for j in range(n)))
    for j in range(n):
        lines.append(sum(grid[i][j] for i in range(n)))
    lines.append(sum(grid[i][i] for i in range(n)))
    lines.append(sum(grid[i][n - 1 - i] for i in range(n)))

    # The line sums are pairwise different. Each pair is split into two strict
    # comparisons, one of which must hold; the sums are not tied to integers.
    for a in range(len(lines)):
        for b in range(a + 1, len(lines)):
            above = m.bool()
            below = m.bool()
            m &= (lines[a] - lines[b] >= 1).iff(above)
            m &= (lines[a] - lines[b] <= -1).iff(below)
            m &= (above | below)

    return m, {"x": grid}
