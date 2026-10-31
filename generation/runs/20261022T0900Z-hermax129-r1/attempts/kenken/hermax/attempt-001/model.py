from itertools import product

from hermax.model import Model


def cage_allowed(target, size, n):
    """Digit tuples (1..n) that satisfy the cage clue under some operation.

    The operation is not in the instance, so the cage admits the union of the
    tuples for addition, multiplication, subtraction and division.
    Subtraction and division apply to two-cell cages.
    """
    allowed = set()
    if size == 1:
        if 1 <= target <= n:
            allowed.add((target,))
        return allowed
    for tup in product(range(1, n + 1), repeat=size):
        total = sum(tup)
        prod = 1
        for v in tup:
            prod *= v
        if total == target or prod == target:
            allowed.add(tup)
        if size == 2:
            a, b = tup
            hi, lo = max(a, b), min(a, b)
            if hi - lo == target:
                allowed.add(tup)
            if hi % lo == 0 and hi // lo == target:
                allowed.add(tup)
    return allowed


def build(instance):
    n = instance["n"]
    cages = instance["problem"]  # each cage: [target, [[r, c], ...]], 1-indexed

    m = Model()

    # Each cell holds a digit 1..n.
    x = m.int_matrix("x", n, n, 1, n)

    # Each row contains exactly one of each digit.
    for i in range(n):
        m &= x.row(i).all_different()

    # Each column contains exactly one of each digit.
    for j in range(n):
        m &= x.col(j).all_different()

    # Each cage's digits achieve its clue under the (unknown) operation.
    for target, cells in cages:
        cell_vars = [x[r - 1][c - 1] for r, c in cells]
        m &= m.table(cell_vars, allowed=sorted(cage_allowed(target, len(cells), n)))

    return m, {"x": x}
