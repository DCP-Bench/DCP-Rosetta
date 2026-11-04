# candies: a PySAT (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python candies.py candies.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Alice, a kindergarten teacher, gives candies to the children sitting in a line, each with a
    rating. Every child gets at least 1 candy, and of two neighbours the one with the higher
    rating gets more candies. Minimise the total number of candies."""
    ratings = instance["ratings"]  # ratings[i]: the rating of the child at position i
    n = len(ratings)               # the number of children

    pool = IDPool()

    # x[i] is the number of candies the child at position i gets, from 1 to n. An optimal solution
    # never gives a child more than n candies. For n = 1 the range is widened to two values, and the
    # bound below cuts it back to n.
    x = [Integer(f"x{i}", 1, max(n, 2), encoding="coupled", vpool=pool) for i in range(n)]
    # z is the total number of candies. Every child gets one, so z is at least n.
    z = Integer("z", n, n * n + 1, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=x + [z], vpool=pool)

    # Each child gets at most n candies, and the total is at most n * n.
    for xi in x:
        engine.add_linear(xi <= n)
    engine.add_linear(z <= n * n)

    # The total is the sum of the candies given to the children.
    engine.add_linear(z - sum(x) == 0)

    # Of two neighbours, the child with the higher rating gets more candies.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            engine.add_linear(x[i - 1] - x[i] >= 1)
        elif ratings[i - 1] < ratings[i]:
            engine.add_linear(x[i] - x[i - 1] >= 1)

    # The constraints above are hard.
    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise the total. The total costs 1 for each value above n that it reaches, so the cost is
    # the total minus n.
    for v in range(n + 1, n * n + 1):
        formula.append([-z.ge(v)], weight=1)

    return formula, {"z": z, "x": x}


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
