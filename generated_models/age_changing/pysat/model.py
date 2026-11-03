# age_changing: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python age_changing.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Starting from my age and applying the four operations +2, /8, -3 and *7 in some
    order gives my husband's age. Starting from his age and applying the same four
    operations in a different order gives my age. Find both ages."""
    # The four operations, each giving the new age from the old one. "/8" only applies
    # to an age that is a multiple of 8; for any other age it gives no result.
    operations = [
        lambda old: old + 2,
        lambda old: old // 8 if old % 8 == 0 else None,
        lambda old: old - 3,
        lambda old: old * 7,
    ]
    n_ops = len(operations)

    pool = IDPool()

    # My age and my husband's age, both between 16 and 120.
    m = Integer("m", 16, 120, vpool=pool)
    h = Integer("h", 16, 120, vpool=pool)

    # perm1[i] is the operation applied at step i when starting from my age, and perm2[i]
    # is the operation applied at step i when starting from his age.
    perm1 = [Integer(f"perm1_{i}", 0, n_ops - 1, vpool=pool) for i in range(n_ops)]
    perm2 = [Integer(f"perm2_{i}", 0, n_ops - 1, vpool=pool) for i in range(n_ops)]

    # from_mine[i] is the age after i steps starting from my age. It starts at my age and
    # ends at my husband's age. The ages in between lie between 1 and 1000.
    from_mine = [m] + [Integer(f"from_mine{i}", 1, 1000, vpool=pool) for i in range(1, n_ops)] + [h]
    # from_his[i] is the age after i steps starting from his age. It starts at his age and
    # ends at my age.
    from_his = [h] + [Integer(f"from_his{i}", 1, 1000, vpool=pool) for i in range(1, n_ops)] + [m]

    # Each age variable is listed once: my age and his age appear in both sequences.
    ages = list(dict.fromkeys(from_mine + from_his))

    # The step with operation perm turns the age old into the age new. For each operation
    # and each value of old, the clauses force new to the result, or rule the value out
    # when the operation does not apply to it or the result is not an allowed age.
    def apply_step(cnf, perm, old, new):
        for k, operation in enumerate(operations):
            for value in range(old.lb, old.ub + 1):
                result = operation(value)
                if result is not None and new.lb <= result <= new.ub:
                    cnf.append([-perm.equals(k), -old.equals(value), new.equals(result)])
                else:
                    cnf.append([-perm.equals(k), -old.equals(value)])

    engine = IntegerEngine(vars=ages + perm1 + perm2, vpool=pool)

    # Each of the two orders uses every operation exactly once.
    engine.add_alldifferent(perm1)
    engine.add_alldifferent(perm2)

    cnf = engine.clausify()

    # differs[i] is true when the two orders use different operations at step i. The two
    # orders differ at some step.
    differs = [pool.id(("differs", i)) for i in range(n_ops)]
    cnf.append(differs)
    for i in range(n_ops):
        for k in range(n_ops):
            cnf.append([-differs[i], -perm1[i].equals(k), -perm2[i].equals(k)])

    # Each step applies the operation chosen for it to the age before it, giving the age
    # after it. The first sequence runs from my age to his, the second from his to mine.
    for i in range(n_ops):
        apply_step(cnf, perm1[i], from_mine[i], from_mine[i + 1])
        apply_step(cnf, perm2[i], from_his[i], from_his[i + 1])

    return cnf, {"m": m, "h": h}


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
