# bales_of_hay: a PySAT (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python bales_of_hay.py bales_of_hay.json

from collections import Counter
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Bales of hay were weighed in every combination of two, and the weights of the
    pairs were written down in numerical order without saying which pair gave which
    weight. Find the weight of each bale."""
    n_bales = instance["n"]        # the number of bales
    weights = instance["weights"]  # the pair weights that were written down, in numerical order
    heaviest = max(weights)        # no pair weighs more than the heaviest written weight
    pairs = list(combinations(range(n_bales), 2))  # every pair of different bales

    pool = IDPool()

    # bales[i] is the weight of bale i; no bale weighs more than 50.
    bales = [Integer(f"bales_{i}", 0, 50, vpool=pool) for i in range(n_bales)]
    # pair_weight[p] is the total weight of pair number p.
    pair_weight = [Integer(f"pair_{i}_{j}", 0, heaviest, vpool=pool) for i, j in pairs]
    engine = IntegerEngine(vars=bales + pair_weight, vpool=pool)

    # The weight of each pair is the sum of the weights of its two bales.
    for p, (i, j) in enumerate(pairs):
        engine.add_linear(pair_weight[p] == bales[i] + bales[j])
    cnf = engine.clausify()

    # The pair weights are exactly the written weights. Each written value is the weight of
    # as many pairs as the number of times it was written down. There are as many pairs as
    # written weights, so no pair is left over.
    for value, times in Counter(weights).items():
        cnf.extend(CardEnc.equals(lits=[pair_weight[p].equals(value) for p in range(len(pairs))],
                                  bound=times, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"bales": bales}


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
