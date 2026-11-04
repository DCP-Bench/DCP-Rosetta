# session1_five_floors: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python session1_five_floors.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def not_next_to(p, q):
    """Clauses that forbid p and q from living on neighbouring floors."""
    clauses = []
    for v in range(1, 5):
        for a, b in ((p, q), (q, p)):
            if a.lb <= v <= a.ub and b.lb <= v + 1 <= b.ub:
                clauses.append([-a.equals(v), -b.equals(v + 1)])
    return clauses


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of a
    five-floor apartment house. Find the floor where each of them lives."""
    pool = IDPool()

    # The floor where Baker lives, not the fifth floor
    B = Integer("B", 1, 4, vpool=pool)
    # The floor where Cooper lives, not the first floor
    C = Integer("C", 2, 5, vpool=pool)
    # The floor where Fletcher lives, neither the first nor the fifth floor
    F = Integer("F", 2, 4, vpool=pool)
    # The floor where Miller lives
    M = Integer("M", 1, 5, vpool=pool)
    # The floor where Smith lives
    S = Integer("S", 1, 5, vpool=pool)
    floor = [B, C, F, M, S]
    engine = IntegerEngine(vars=floor, vpool=pool)

    # The five people live on different floors.
    engine.add_alldifferent(floor)
    cnf = engine.clausify()

    # Miller lives on a higher floor than Cooper.
    for c in range(C.lb, C.ub + 1):
        for m in range(M.lb, c + 1):
            cnf.append([-C.equals(c), -M.equals(m)])

    # Smith does not live on a floor next to Fletcher's.
    cnf.extend(not_next_to(S, F))

    # Fletcher does not live on a floor next to Cooper's.
    cnf.extend(not_next_to(F, C))

    return cnf, {"B": B, "C": C, "F": F, "M": M, "S": S}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
