# csplib_006_golomb_rulers: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Place size marks on a ruler, the first at position 0, so that the distances between
    all pairs of marks are different. Find the shortest such Golomb ruler."""
    size = instance["size"]  # the number of marks on the ruler

    # the largest position a mark can take; the shortest ruler is far shorter than this
    top = size * size

    pool = IDPool()

    # on[p] is true when a mark lies at position p
    on = [pool.id(("on", p)) for p in range(top + 1)]
    # marks[k] is the position of mark k, counting from the left
    marks = [Integer(f"marks{k}", 0, top, vpool=pool) for k in range(size)]

    formula = WCNF()
    # each mark takes one position
    formula.extend(IntegerEngine(vars=marks, vpool=pool).clausify().clauses)

    # at_least(p, k) is true when at least k marks lie at positions 0 to p. It is defined
    # from the value at p - 1 and whether position p holds a mark.
    def at_least(p, k):
        return pool.id(("at_least", p, k))

    for p in range(top + 1):
        formula.append([at_least(p, 0)])
        for k in range(1, size + 2):
            here = at_least(p, k)
            if p == 0:
                # only position 0 counts: at least 1 mark there iff it holds a mark
                if k == 1:
                    formula.append([-here, on[0]])
                    formula.append([here, -on[0]])
                else:
                    formula.append([-here])
                continue
            before, before_less = at_least(p - 1, k), at_least(p - 1, k - 1)
            # at least k marks up to p iff at least k marks up to p - 1, or k - 1 marks up to
            # p - 1 and a mark at p
            formula.append([-before, here])
            formula.append([-before_less, -on[p], here])
            formula.append([-here, before, before_less])
            formula.append([-here, before, on[p]])

    # The ruler has exactly size marks.
    formula.append([at_least(top, size)])
    formula.append([-at_least(top, size + 1)])

    # The first mark is at position 0.
    formula.append([on[0]])

    # Marks are in increasing order: marks[k] is the position that holds a mark with exactly
    # k marks before it.
    for k in range(size):
        for p in range(top + 1):
            eq = marks[k].equals(p)
            if p == 0:
                cond = [on[0]] if k == 0 else None
            else:
                cond = [on[p], at_least(p - 1, k), -at_least(p - 1, k + 1)]
            if cond is None:
                formula.append([-eq])
                continue
            for lit in cond:
                formula.append([-eq, lit])
            formula.append([-lit for lit in cond] + [eq])

    # No two pairs of marks lie the same distance apart. pair(p, d) is true when there are
    # marks at p and p + d, and at most one pair is at each distance d.
    for d in range(1, top + 1):
        pairs = []
        for p in range(0, top + 1 - d):
            pair = pool.id(("pair", p, d))
            formula.append([-on[p], -on[p + d], pair])
            pairs.append(pair)
        if len(pairs) > 1:
            formula.extend(CardEnc.atmost(lits=pairs, bound=1, vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # The length is the position of the last mark. Each position p from 1 on that the last
    # mark reaches, that is each p with not all marks below p, costs 1, so the total cost is
    # the length.
    for p in range(1, top + 1):
        formula.append([at_least(p - 1, size)], weight=1)

    return formula, {"marks": marks, "length": marks[-1]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
