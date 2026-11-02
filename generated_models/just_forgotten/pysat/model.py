# just_forgotten: a PySAT (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python just_forgotten.py just_forgotten.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Joe's account number uses each digit from 0 to n-1 exactly once. For each set of
    digits he tried, exactly a given number of digits were in their right position.
    Find the account number."""
    sets = instance["sets"]                       # sets[k][i]: the digit at position i in the k-th set Joe tried
    num_correct = instance["num_correct_digits"]  # the number of digits in the right position in each set
    n = len(sets[0])                              # the number of digits

    pool = IDPool()

    # x[i]: the digit at position i of the account number
    x = [Integer(f"x_{i}", 0, n - 1, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # The digits 0 to n-1 each appear exactly once.
    engine.add_alldifferent(x)
    cnf = engine.clausify()

    # Each set has exactly num_correct digits in the position they have in the account number.
    for tried in sets:
        cnf.extend(CardEnc.equals(lits=[x[i].equals(tried[i]) for i in range(n)], bound=num_correct,
                                  vpool=pool, encoding=EncType.seqcounter).clauses)

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
