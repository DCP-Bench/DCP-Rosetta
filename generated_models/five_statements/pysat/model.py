# five_statements: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python five_statements.py

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """Five statements say that exactly one, exactly two, exactly three,
    exactly four and exactly five of these statements are false. Determine
    which of them is true."""
    n_statements = 5  # the number of statements

    pool = IDPool()
    formula = CNF()

    # statements[i] is true when statement i + 1 is true
    statements = [pool.id(("statement", i)) for i in range(n_statements)]
    # exactly[c] is true when exactly c of the statements are false, for c from 0 to n_statements
    exactly = [pool.id(("exactly", c)) for c in range(n_statements + 1)]

    # One number of false statements holds.
    formula.append(exactly)
    for c in range(n_statements + 1):
        for other in range(c + 1, n_statements + 1):
            formula.append([-exactly[c], -exactly[other]])

    # exactly[c] holds only when exactly c statements are false.
    for c in range(n_statements + 1):
        for clause in CardEnc.equals(lits=[-s for s in statements], bound=c, vpool=pool,
                                     encoding=EncType.seqcounter).clauses:
            formula.append([-exactly[c]] + clause)

    # Statement i + 1 is true exactly when exactly i + 1 statements are false.
    for i in range(n_statements):
        formula.append([-statements[i], exactly[i + 1]])
        formula.append([statements[i], -exactly[i + 1]])

    return formula, {"statements": statements}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

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
