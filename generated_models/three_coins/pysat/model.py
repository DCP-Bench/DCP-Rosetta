# three_coins: a PySAT (Python) model from DCP Rosetta.
# Download the `three_coins.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python three_coins.py three_coins.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """Three coins lie on a table, in the order given. In exactly the given number of
    moves, each move flipping one coin, make them all face heads or all face tails."""
    init = instance["init"]            # init[j]: whether coin j starts tails up
    num_moves = instance["num_moves"]  # the number of moves
    n = len(init)                      # the number of coins

    pool = IDPool()

    # steps[r][j] is true when coin j is tails up after r moves (row 0 is the start)
    steps = [[pool.id(("s", r, j)) for j in range(n)] for r in range(num_moves + 1)]

    cnf = CNF()

    # The coins start as given.
    for j in range(n):
        cnf.append([steps[0][j]] if init[j] else [-steps[0][j]])

    for row in range(1, num_moves + 1):
        # flipped[j] is true when move row flips coin j
        flipped = []
        for j in range(n):
            a, b = steps[row][j], steps[row - 1][j]
            f = pool.id(("f", row, j))
            # A coin is flipped in a move exactly when its side changes.
            cnf.append([-f, a, b])
            cnf.append([-f, -a, -b])
            cnf.append([f, -a, b])
            cnf.append([f, a, -b])
            flipped.append(f)

        # Each move flips exactly one coin.
        cnf.extend(CardEnc.equals(lits=flipped, bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # After the last move all coins face the same way.
    last = steps[num_moves]
    for j in range(1, n):
        cnf.append([-last[0], last[j]])
        cnf.append([last[0], -last[j]])

    return cnf, {"steps": steps}


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
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
