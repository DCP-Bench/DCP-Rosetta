# flip_rows_cols: a PySAT (Python) model from DCP Rosetta.
# Download the `flip_rows_cols.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python flip_rows_cols.py flip_rows_cols.json

from math import isqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import EncType, PBEnc

TOTAL_MAX = 1000  # the overall sum is at most 1000
LINE_MAX = 300    # every row sum and column sum is at most 300


def create_model(instance):
    """Flip the sign of whole rows and columns of a matrix of numbers, as many as you like,
    so that every row and every column sums to zero or more. Among these flips, make the
    overall sum of the flipped matrix as small as possible."""
    matrix = instance["input_matrix"]  # matrix[i][j]: the number in row i and column j
    n_rows = len(matrix)
    n_cols = len(matrix[0])

    pool = IDPool()

    # row_signs[i] is -1 when row i is flipped and 1 when it is not.
    row_signs = [Integer(f"row_signs_{i}", -1, 1, vpool=pool) for i in range(n_rows)]
    # col_signs[j] is -1 when column j is flipped and 1 when it is not.
    col_signs = [Integer(f"col_signs_{j}", -1, 1, vpool=pool) for j in range(n_cols)]
    # The overall sum of the flipped matrix.
    total_sum = Integer("total_sum", 0, TOTAL_MAX, encoding="order", vpool=pool)
    engine = IntegerEngine(vars=row_signs + col_signs + [total_sum], vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # A sign is -1 or 1, never 0.
    for s in row_signs + col_signs:
        formula.append([-s.equals(0)])
    row_positive = [s.equals(1) for s in row_signs]
    col_positive = [s.equals(1) for s in col_signs]

    # keep[i][j] is true when entry (i, j) keeps its sign, that is when its row and its
    # column have the same sign. The entry then stays as it is, and otherwise it is negated.
    keep = [[pool.id(("keep", i, j)) for j in range(n_cols)] for i in range(n_rows)]
    for i in range(n_rows):
        for j in range(n_cols):
            k, r, c = keep[i][j], row_positive[i], col_positive[j]
            formula.append([-k, -r, c])
            formula.append([-k, r, -c])
            formula.append([k, r, c])
            formula.append([k, -r, -c])

    # Over the given cells, the flipped entries sum to 2|a| summed over the cells whose
    # flipped entry is positive, minus mass, where mass is the sum of |a| over the cells.
    def signed_sum(cells):
        lits, weights = [], []
        for i, j in cells:
            a = matrix[i][j]
            if a != 0:
                lits.append(keep[i][j] if a > 0 else -keep[i][j])
                weights.append(2 * abs(a))
        return lits, weights, sum(weights) // 2

    # low <= sum of the flipped entries in cells <= high.
    def within(cells, low, high):
        lits, weights, mass = signed_sum(cells)
        if low + mass > 0:
            formula.extend(PBEnc.geq(lits=lits, weights=weights,
                                     bound=low + mass, vpool=pool).clauses)
        if high + mass < sum(weights):
            formula.extend(PBEnc.leq(lits=lits, weights=weights,
                                     bound=high + mass, vpool=pool).clauses)

    # Each entry lies between -100 and 100, so a larger entry leaves no flip to find.
    if any(abs(v) > 100 for row in matrix for v in row):
        formula.append([])

    # Every row of the flipped matrix sums to zero or more, and at most LINE_MAX.
    for i in range(n_rows):
        within([(i, j) for j in range(n_cols)], 0, LINE_MAX)
    # Every column of the flipped matrix sums to zero or more, and at most LINE_MAX.
    for j in range(n_cols):
        within([(i, j) for i in range(n_rows)], 0, LINE_MAX)

    # The overall sum is at least 0.
    cells = [(i, j) for i in range(n_rows) for j in range(n_cols)]
    lits, weights, mass = signed_sum(cells)
    if mass > 0:
        formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=mass, vpool=pool).clauses)

    # steps[v - 1] is true when total_sum is less than v.
    steps = [-total_sum.ge(v) for v in range(1, TOTAL_MAX + 1)]
    # total_sum is at least the overall sum: the overall sum plus the true steps stays at
    # most mass + TOTAL_MAX.
    formula.extend(PBEnc.leq(lits=lits + steps, weights=weights + [1] * len(steps),
                             bound=mass + TOTAL_MAX, vpool=pool,
                             encoding=EncType.adder).clauses)

    # Minimise total_sum. Falsifying the soft clause for v in 1..TOTAL_MAX, which happens
    # when total_sum reaches v, costs 1 + (v - 1) // block_size. The total cost rises
    # strictly with total_sum, so minimising the cost minimises total_sum.
    block_size = isqrt(TOTAL_MAX) + 1
    for v in range(1, TOTAL_MAX + 1):
        formula.append([-total_sum.ge(v)], weight=1 + (v - 1) // block_size)

    return formula, {"row_signs": row_signs, "col_signs": col_signs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
