# coins_grid: a PySAT (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python coins_grid.py coins_grid.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Place coins on an n by n grid, at most one per cell, with exactly c coins in every row
    and every column, so that the sum of the squared horizontal distances of the coins from
    the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in every row and every column

    pool = IDPool()

    # x[i][j] is 1 when a coin lies in row i, column j, and 0 otherwise
    x = [[Integer(f"x_{i}_{j}", 0, 1, vpool=pool) for j in range(n)] for i in range(n)]
    coin = [[x[i][j].equals(1) for j in range(n)] for i in range(n)]

    # dist[i][j] is the squared horizontal distance of cell (i, j) from the main diagonal
    dist = [[(i - j) * (i - j) for j in range(n)] for i in range(n)]

    # The cost of a valid placement bounds z: the coins on the cells where
    # (j - i + c // 2) mod n is below c form one, with c coins in every row and column.
    bound = sum(dist[i][j] for i in range(n) for j in range(n)
                if (j - i + c // 2) % n < c)

    # z is the total cost: the sum of the squared distances of the cells holding a coin
    z = Integer("z", 0, max(bound, 1), vpool=pool)

    engine = IntegerEngine(vars=[v for row in x for v in row] + [z], vpool=pool)
    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Every row holds exactly c coins.
    for i in range(n):
        formula.extend(CardEnc.equals(lits=coin[i], bound=c, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Every column holds exactly c coins.
    for j in range(n):
        formula.extend(CardEnc.equals(lits=[coin[i][j] for i in range(n)], bound=c,
                                      vpool=pool, encoding=EncType.seqcounter).clauses)

    # The cells are scanned one by one. partial[v] is true when the coins among the cells
    # scanned so far have squared distances that sum to v, for each v up to the bound.
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    partial = {0: start}
    cells = [(i, j) for i in range(n) for j in range(n) if dist[i][j] > 0]
    for k, (i, j) in enumerate(cells):
        d = dist[i][j]
        nxt = {}
        for v in partial:
            for w in (v, v + d):
                if w <= bound and w not in nxt:
                    nxt[w] = pool.id(("partial", k + 1, w))
        for v, lit in partial.items():
            # no coin on this cell: the sum stays at v
            formula.append([-lit, coin[i][j], nxt[v]])
            # a coin on this cell: the sum grows by d, and may not pass the bound
            if v + d <= bound:
                formula.append([-lit, -coin[i][j], nxt[v + d]])
            else:
                formula.append([-lit, -coin[i][j]])
        partial = nxt

    # z is the final sum: each value the final sum can take fixes z, and the other values
    # of z are excluded.
    for v, lit in partial.items():
        formula.append([-lit, z.equals(v)])
    for v in range(0, max(bound, 1) + 1):
        if v not in partial:
            formula.append([-z.equals(v)])

    # Minimise z: a coin on cell (i, j) costs its squared distance.
    for (i, j) in cells:
        formula.append([-coin[i][j]], weight=dist[i][j])

    return formula, {"x": x, "z": z}


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
