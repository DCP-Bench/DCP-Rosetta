from hermax.model import Model


def build(instance):
    n = instance["n"]
    target = n * (n * n + 1) // 2

    m = Model()
    square = m.int_matrix("cell", n, n, 1, n * n)

    # Each cell holds a different integer from 1 to n^2.
    m &= square.flatten().all_different()

    # The sum of every row, column and diagonal equals n(n^2+1)/2.
    for i in range(n):
        m &= (sum(square[i][j] for j in range(n)) == target)
        m &= (sum(square[j][i] for j in range(n)) == target)
    m &= (sum(square[i][i] for i in range(n)) == target)
    m &= (sum(square[i][n - 1 - i] for i in range(n)) == target)

    return m, {"square": square}
