# among: a PySAT (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python among.py among.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Exactly m of the values in x take one of the values in v. Every value in x
    is at least 0 and at most 7."""
    n_values = instance["n"]  # the number of values in x
    n_wanted = instance["m"]  # how many values in x must take a value from v
    v = instance["v"]         # the values that are counted

    pool = IDPool()

    # x[i] is the value at position i, between 0 and 7.
    x = [Integer(f"x{i}", 0, 7, vpool=pool) for i in range(n_values)]

    # Rules on the values of x.
    engine = IntegerEngine(vars=x, vpool=pool)
    cnf = engine.clausify()

    # One statement per position and each value in v that x can take: position i takes that value.
    hits = [x[i].equals(value) for i in range(n_values) for value in v if 0 <= value <= 7]

    # Each position takes one value, so exactly n_wanted of these statements hold.
    cnf.extend(CardEnc.equals(lits=hits, bound=n_wanted, vpool=pool,
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
