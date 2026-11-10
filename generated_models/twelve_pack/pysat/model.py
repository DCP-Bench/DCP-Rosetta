# twelve_pack: a PySAT (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python twelve_pack.py twelve_pack.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Buy packs of the given sizes, any number of each, so that the number of items
    reaches the target, with as few items as possible."""
    target = instance["target"]  # the number of items needed
    packs = instance["packs"]    # packs[i]: the number of items in a pack of kind i
    n_packs = len(packs)         # the number of pack kinds
    ceiling = target * 2         # no count is above twice the target

    # Buying ceil(target / smallest) packs of the smallest kind reaches the target with fewer
    # than target + smallest items, so the best total never exceeds target + smallest - 1.
    smallest = min(packs)
    high = target + smallest - 1

    pool = IDPool()

    # total is the number of items bought, from the target up to high
    total = Integer("total", target, high, encoding="order", vpool=pool)

    # counts[i] is how many packs of kind i are bought. More packs of one kind than fit in
    # high items would overshoot it, so the count stops at high // packs[i].
    counts = [Integer(f"counts_{i}", 0, min(ceiling, high // packs[i]),
                      encoding="coupled", vpool=pool) for i in range(n_packs)]
    engine = IntegerEngine(vars=counts + [total], vpool=pool)

    # The total is the number of items in all the packs bought.
    engine.add_linear(sum(packs[i] * counts[i] for i in range(n_packs)) - total == 0)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise the total. Each item above the target costs 1, so the cost is the total minus the target.
    for v in range(target + 1, high + 1):
        formula.append([-total.ge(v)], weight=1)

    # The objective in the problem's terms: the number of items bought (RC2's cost is that
    # number minus the target).
    return formula, {"counts": counts}, total


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
