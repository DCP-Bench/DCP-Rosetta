# broken_weights: a PySAT (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python broken_weights.py broken_weights.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number of
    pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]  # the weight of the whole measure, in pounds
    n = instance["n"]  # the number of pieces it broke into

    pool = IDPool()

    # The other n - 1 pieces weigh at least a pound each, so no piece weighs more than this.
    heaviest = m - (n - 1)
    # weights[j] is the weight of piece j, in pounds
    weights = [Integer(f"weight{j}", 1, heaviest, vpool=pool) for j in range(n)]
    engine = IntegerEngine(vars=weights, vpool=pool)
    cnf = engine.clausify()

    # Each piece's weight is also kept in binary digits, so that the pieces can be added up.
    n_bits = heaviest.bit_length()
    # bit[j][b] is digit b of the weight of piece j, worth 2**b pounds
    bit = [[pool.id(("bit", j, b)) for b in range(n_bits)] for j in range(n)]
    for j in range(n):
        for v in range(1, heaviest + 1):
            for b in range(n_bits):
                cnf.append([-weights[j].equals(v), bit[j][b] if (v >> b) & 1 else -bit[j][b]])

    # The pieces add up to the weight of the whole measure.
    cnf.extend(PBEnc.equals(lits=[bit[j][b] for j in range(n) for b in range(n_bits)],
                            weights=[1 << b for j in range(n) for b in range(n_bits)],
                            bound=m, vpool=pool).clauses)

    # Every load from 1 to m balances on the scale. Each piece is on the pan with the load,
    # on the other pan, or off the scale. The pieces on the other pan, minus the pieces
    # beside the load, weigh the load.
    for target in range(1, m + 1):
        # lits[k] is a digit of a piece on a pan, and coefficients[k] is its pounds on the
        # scale: plus for the other pan, minus for the pan with the load
        lits, coefficients = [], []
        for j in range(n):
            on_other = pool.id(("other", target, j))
            on_load = pool.id(("load", target, j))
            # A piece is on at most one pan.
            cnf.append([-on_other, -on_load])
            for b in range(n_bits):
                # digit_on_pan is true when piece j is on this pan and digit b of its weight is set
                for pan, sign in ((on_other, 1), (on_load, -1)):
                    digit_on_pan = pool.id(("digit", target, j, b, sign))
                    cnf.append([-digit_on_pan, pan])
                    cnf.append([-digit_on_pan, bit[j][b]])
                    cnf.append([digit_on_pan, -pan, -bit[j][b]])
                    lits.append(digit_on_pan)
                    coefficients.append(sign * (1 << b))
        cnf.extend(PBEnc.equals(lits=lits, weights=coefficients, bound=target,
                                vpool=pool).clauses)

    return cnf, {"weights": weights}


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
