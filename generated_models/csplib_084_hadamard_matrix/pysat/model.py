# csplib_084_hadamard_matrix: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find two sequences a and b of odd length l, with entries -1 or +1, that each
    sum to 1 and whose periodic autocorrelations add up to -2 at every shift
    s = 1, ..., (l-1)/2 (a Legendre pair, which gives a Hadamard matrix)."""
    l = instance["l"]        # length of each sequence, an odd number
    n_shifts = (l - 1) // 2  # the shifts s = 1 to n_shifts are constrained

    pool = IDPool()  # gives a number to each variable of the model
    cnf = CNF()      # all constraints of the model

    def sequence(name):
        # plus[i] is true when entry i of the sequence is +1
        plus = [pool.id((name, "plus", i)) for i in range(l)]
        # values[i] is entry i of the sequence, -1 or +1
        values = [Integer(f"{name}_{i}", -1, 1, vpool=pool) for i in range(l)]
        engine = IntegerEngine(vars=values, vpool=pool)
        cnf.extend(engine.clausify().clauses)
        # An entry is +1 exactly when its flag is true, and -1 otherwise, so 0 is excluded.
        for i in range(l):
            cnf.append([-plus[i], values[i].equals(1)])
            cnf.append([plus[i], values[i].equals(-1)])
        # The entries sum to 1, so (l + 1) / 2 of them are +1.
        cnf.extend(CardEnc.equals(lits=plus, bound=(l + 1) // 2, vpool=pool, encoding=EncType.seqcounter).clauses)
        return plus, values

    def agreements(name, plus, s):
        # agree[i] is the flag for position i, collected for the count below
        agree = []
        # same is true exactly when entries i and i + s (mod l) are equal
        for i in range(l):
            p, q = plus[i], plus[(i + s) % l]
            same = pool.id((name, "same", s, i))
            cnf.append([-same, -p, q])
            cnf.append([-same, p, -q])
            cnf.append([same, p, q])
            cnf.append([same, -p, -q])
            agree.append(same)
        return agree

    # a and b are the two sequences.
    plus_a, a = sequence("a")
    plus_b, b = sequence("b")

    # PAF(a, s) + PAF(b, s) = -2. Each PAF is 2 * (equal pairs) - l, so the
    # condition says that the equal pairs of a and b together number l - 1.
    for s in range(1, n_shifts + 1):
        same = agreements("a", plus_a, s) + agreements("b", plus_b, s)
        cnf.extend(CardEnc.equals(lits=same, bound=l - 1, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"a": a, "b": b}


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
