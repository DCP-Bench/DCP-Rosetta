# heterosquare: a PySAT (Python) model from DCP Rosetta.
# Download the `heterosquare.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python heterosquare.py heterosquare.json

from itertools import combinations

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """A heterosquare of order n is an n by n square of distinct integers from 1 to n^2
    whose row, column and diagonal sums are all different."""
    n = instance["n"]  # the order of the square
    top = n * n        # the largest entry

    pool = IDPool()

    # x[r][c] is the number in row r, column c
    x = [[Integer(f"x_{r}_{c}", 1, top, vpool=pool) for c in range(n)] for r in range(n)]
    cells = [cell for row in x for cell in row]
    engine = IntegerEngine(vars=cells, vpool=pool)

    # The numbers in the square are distinct.
    engine.add_alldifferent(cells)
    formula = engine.clausify()

    # The sums are compared through their binary digits, which keeps the model small for
    # sums up to n^3. Every line has n cells, so two lines have different sums exactly when
    # their sums of (entry - 1) differ.
    entry_bits = (top - 1).bit_length()
    line_bits = (n * (top - 1)).bit_length()

    # bit[r][c][k] is digit k of x[r][c] - 1; it is forced to the digits of the value of x[r][c]
    bit = [[[pool.id(("bit", r, c, k)) for k in range(entry_bits)] for c in range(n)] for r in range(n)]
    for r in range(n):
        for c in range(n):
            for value in range(1, top + 1):
                for k in range(entry_bits):
                    is_set = ((value - 1) >> k) & 1
                    formula.append([-x[r][c].equals(value), bit[r][c][k] if is_set else -bit[r][c][k]])

    # The lines whose sums must differ, each as the list of its cells: the rows, the columns and the two diagonals.
    lines = [[(r, c) for c in range(n)] for r in range(n)]
    lines += [[(r, c) for r in range(n)] for c in range(n)]
    lines.append([(i, i) for i in range(n)])
    lines.append([(i, n - 1 - i) for i in range(n)])

    # line_sum[j] holds the digits of the sum of (entry - 1) over line j. The digits of the
    # cells on the line add up to the digits of this sum.
    line_sum = []
    for j, line in enumerate(lines):
        sum_bits = [pool.id(("sum", j, k)) for k in range(line_bits)]
        lits = [bit[r][c][k] for r, c in line for k in range(entry_bits)] + sum_bits
        weights = [1 << k for _ in line for k in range(entry_bits)] + [-(1 << k) for k in range(line_bits)]
        formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=0, vpool=pool).clauses)
        line_sum.append(sum_bits)

    # Every two lines have different sums. For each pair, differs[k] is true only when
    # digit k of the two sums is different, and one of the digits must differ.
    for a, b in combinations(range(len(lines)), 2):
        differs = [pool.id(("differs", a, b, k)) for k in range(line_bits)]
        for k in range(line_bits):
            formula.append([-differs[k], line_sum[a][k], line_sum[b][k]])
            formula.append([-differs[k], -line_sum[a][k], -line_sum[b][k]])
        formula.append(differs)

    return formula, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
