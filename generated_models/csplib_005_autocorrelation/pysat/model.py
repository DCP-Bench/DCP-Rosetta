# csplib_005_autocorrelation: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Choose a sequence of n bits, each +1 or -1, that minimises the sum of the squared
    periodic autocorrelations C_k = sum_i S_i * S_((i+k) mod n) over k = 1 to n-1."""
    n = instance["n"]  # the length of the sequence

    pool = IDPool()

    # The distances k = 1 to n // 2. A larger distance n - k compares the same pairs of
    # positions as distance k, so it has the same autocorrelation.
    shifts = range(1, n // 2 + 1)

    # sequence[i] is the bit at position i, -1 or +1
    sequence = [Integer(f"sequence_{i}", -1, 1, vpool=pool) for i in range(n)]
    # count[k] is the number of positions whose bit differs from the bit k places on, cyclically
    count = {k: Integer(f"differ_count_{k}", 0, n, encoding="order", vpool=pool)
             for k in shifts}
    # each integer takes exactly one of its values
    engine = IntegerEngine(vars=sequence + list(count.values()), vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # A bit is +1 or -1, never 0.
    for s in sequence:
        formula.append([-s.equals(0)])
    # plus[i] is true when bit i is +1.
    plus = [s.equals(1) for s in sequence]

    for k in shifts:
        # The two bits at positions i and (i + k) mod n multiply to -1 when they differ and
        # to +1 when they agree, so C_k = n - 2 * count[k].
        # differ[i] is true when the bits at i and (i + k) mod n differ.
        differ = []
        for i in range(n):
            j = (i + k) % n
            d = pool.id(("differ", k, i))
            formula.append([-d, plus[i], plus[j]])
            formula.append([-d, -plus[i], -plus[j]])
            formula.append([d, -plus[i], plus[j]])
            formula.append([d, plus[i], -plus[j]])
            differ.append(d)
        # reached[v - 1] is true when count[k] is at least v.
        reached = [count[k].ge(v) for v in range(1, n + 1)]
        # count[k] is the number of differing positions.
        formula.extend(PBEnc.equals(lits=differ + reached,
                                    weights=[1] * n + [-1] * n, bound=0,
                                    vpool=pool).clauses)

        # The energy adds C_k^2 for shift k, and shift n - k adds the same amount. So shift k
        # counts twice, unless k is n / 2 and it is its own mirror.
        times = 1 if 2 * k == n else 2
        # Each step of count[k] from v - 1 to v changes the energy by
        # times * ((n - 2v)^2 - (n - 2(v - 1))^2). A rise is paid when count[k] reaches v, a
        # fall is paid when count[k] stays below v. The payments differ from the energy by a
        # fixed amount, which does not change the best sequence.
        for v in range(1, n + 1):
            delta = times * ((n - 2 * v) ** 2 - (n - 2 * (v - 1)) ** 2)
            if delta > 0:
                formula.append([-count[k].ge(v)], weight=delta)
            elif delta < 0:
                formula.append([count[k].ge(v)], weight=-delta)

    # The objective in the problem's terms: the energy E. Each shift k adds times * C_k^2, which
    # is times * n^2 when no positions differ plus the step changes RC2 pays (or saves) above.
    objective = []
    for k in shifts:
        times = 1 if 2 * k == n else 2
        objective.append((times * n * n, True))
        for v in range(1, n + 1):
            delta = times * ((n - 2 * v) ** 2 - (n - 2 * (v - 1)) ** 2)
            objective.append((delta, count[k].ge(v)))

    return formula, {"sequence": sequence}, objective


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
