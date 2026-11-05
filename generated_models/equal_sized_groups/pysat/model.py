# equal_sized_groups: a PySAT (Python) model from DCP Rosetta.
# Download the `equal_sized_groups.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/equal_sized_groups.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python equal_sized_groups.py equal_sized_groups.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Divide a sorted list of n elements into k groups by choosing k - 1 split points,
    keeping elements with the same value in the same group, with the groups as close in
    size to round(n / k) as possible in total."""
    a = instance["a"]  # the sorted list of elements
    n_groups = instance["k"]  # the number of groups
    n_elements = len(a)  # the number of elements
    group_size = round(n_elements / n_groups)  # the ideal size of a group
    breaks = range(n_groups - 1)  # the k - 1 split points

    # The largest deviation of a group from the ideal size: a group holds between 1 and n - k + 1 elements.
    max_dev = max(group_size - 1, n_elements - n_groups + 1 - group_size, 0)

    pool = IDPool()

    # x[p] is the 1-based position of the last element before split point p. A split point
    # after the last element would leave a group empty.
    x = [Integer(f"x_{p}", 1, n_elements - 1, vpool=pool) for p in breaks]
    # err[i] is at least how far group i is from the ideal size; the objective pushes it down to that.
    err = [Integer(f"err_{i}", 0, max_dev, encoding="order", vpool=pool) for i in range(n_groups)]
    engine = IntegerEngine(vars=x + err, vpool=pool)

    formula = WCNF()

    # Group i has the size given by the split points. `avoid` lists the ways the split points can
    # move off the positions that give group i this size. If none of them happens, the error of
    # group i is at least its deviation from the ideal size. A group of more than n - k + 1
    # elements would leave another group empty, so that size is ruled out.
    def charge(i, size, avoid):
        dev = abs(size - group_size)
        if size > n_elements - n_groups + 1:
            formula.append(avoid)
        elif dev > 0:
            formula.append(avoid + [err[i].ge(dev)])

    formula.extend(engine.clausify().clauses)

    # Equal elements stay together, so a split point may only fall between two different elements.
    allowed = [j for j in range(1, n_elements) if a[j - 1] != a[j]]
    for p in breaks:
        for j in range(1, n_elements):
            if a[j - 1] == a[j]:
                formula.append([-x[p].equals(j)])

    if n_groups == 1:
        # The only group holds every element.
        charge(0, n_elements, [])
    else:
        # The first group ends at the first split point, so its size is that split point's position.
        for u in allowed:
            charge(0, u, [-x[0].equals(u)])
        # Group i lies between split points i - 1 and i, so its size is the gap between their
        # positions. The split points increase, so every group holds at least one element.
        for i in range(1, n_groups - 1):
            for u in allowed:
                for v in allowed:
                    avoid = [-x[i - 1].equals(u), -x[i].equals(v)]
                    if v <= u:
                        formula.append(avoid)
                    else:
                        charge(i, v - u, avoid)
        # The last group holds the elements after the last split point.
        for u in allowed:
            charge(n_groups - 1, n_elements - u, [-x[n_groups - 2].equals(u)])

    # The error of each group is written in binary. bits lists the binary digits of all groups,
    # and weights the value of each. The digit worth 2**b of group i is on whenever the error of
    # group i has that digit set. The weighted digits add up to at most n, so the total error is
    # at most n.
    bits, weights = [], []
    for i in range(n_groups):
        b = 0
        while (1 << b) <= max_dev:
            bit = pool.id(("err_bit", i, b))
            lo = 1 << b
            while lo <= max_dev:
                hi = min(lo + (1 << b) - 1, max_dev)
                clause = [-err[i].ge(lo), bit]
                if hi < max_dev:
                    clause.insert(1, err[i].ge(hi + 1))
                formula.append(clause)
                lo += 1 << (b + 1)
            bits.append(bit)
            weights.append(1 << b)
            b += 1
    if bits:
        formula.extend(PBEnc.leq(lits=bits, weights=weights, bound=n_elements, vpool=pool).clauses)

    # The objective is the total error: each unit of error in each group costs 1.
    for i in range(n_groups):
        for v in range(1, max_dev + 1):
            formula.append([-err[i].ge(v)], weight=1)

    # The objective in the problem's terms: the total error, the sum of the group errors (as
    # RC2's cost; each error equals its group's deviation in an optimal split).
    objective = [(1, e) for e in err]

    return formula, {"x": x}, objective


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
