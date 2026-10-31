from hermax.model import Model


def all_different_pairs(model, variables):
    # Pairwise inequality over a plain list of IntVars.
    for a in range(len(variables)):
        for b in range(a + 1, len(variables)):
            model &= (variables[a] != variables[b])


def build(instance):
    # Grid side and cages come from the instance.
    n = instance["n"]
    cages = instance["problem"]

    # Nonets are square blocks; the side of a block is the square root of n.
    block = int(round(n ** 0.5))
    assert block * block == n

    model = Model()
    x = model.int_matrix("x", n, n, 1, n)

    # Each row, column and nonet contains each number 1 to n exactly once.
    for i in range(n):
        model &= x.row(i).all_different()
        model &= x.col(i).all_different()
    for br in range(block):
        for bc in range(block):
            nonet = [x[br * block + r][bc * block + c] for r in range(block) for c in range(block)]
            all_different_pairs(model, nonet)

    # Each cage: its cells hold distinct numbers, and they sum to the printed total.
    for total, cells in cages:
        cell_vars = [x[r - 1][c - 1] for r, c in cells]
        all_different_pairs(model, cell_vars)
        model &= (sum(cell_vars) == total)

    return model, {"x": x}
