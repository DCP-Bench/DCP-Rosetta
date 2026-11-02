# frog_circle: a PySAT (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python frog_circle.py frog_circle.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Cards numbered 1 to n lie in a circle. A frog starts on card 1 and, from card k, jumps k
    places clockwise. Find an arrangement of the cards that lets the frog land on every card."""
    n = instance["n"]  # the number of cards

    pool = IDPool()

    # x[p] is the number of the card at place p around the circle, counting places from 0
    x = [Integer(f"x{p}", 1, n, vpool=pool) for p in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # Every card appears once.
    engine.add_alldifferent(x)
    # The frog starts on card 1, which lies at place 0.
    engine.add_linear(x[0] == 1)
    cnf = engine.clausify()

    # at_step[i][p] is true when the frog stands at place p after i jumps
    at_step = [[pool.id(("at", i, p)) for p in range(n)] for i in range(n)]

    # The frog starts at place 0, before its first jump.
    cnf.append([at_step[0][0]])
    # At each stop the frog stands at exactly one place.
    for i in range(n):
        cnf.extend(CardEnc.equals(lits=at_step[i], bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)

    # A jump from place p, where card v lies, takes the frog v places clockwise to place (p + v) mod n.
    for i in range(1, n):
        for p in range(n):
            for v in range(1, n + 1):
                cnf.append([-at_step[i - 1][p], -x[p].equals(v), at_step[i][(p + v) % n]])

    # Over its n stops, the start included, the frog stands on each place exactly once.
    for p in range(n):
        cnf.extend(CardEnc.equals(lits=[at_step[i][p] for i in range(n)], bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"x": x}


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
