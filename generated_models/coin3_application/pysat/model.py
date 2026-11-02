# coin3_application: a PySAT (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python coin3_application.py coin3_application.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find the fewest coins that let one pay exactly any amount below a given maximum,
    using coins of the given denominations."""
    denominations = instance["denominations"]    # denominations[i]: the value of coin type i
    max_amount = instance["max_amount_to_pay"]   # every amount from 1 up to this value, excluded, must be payable
    n_denominations = len(denominations)

    pool = IDPool()

    # The most coins of each type that any answer needs. A payment below max_amount
    # uses at most (max_amount - 1) // d coins of value d, so no more are carried.
    ub = [max_amount if d <= 0 else min(max_amount, (max_amount - 1) // d)
          for d in denominations]

    # x[i] is the number of coins of type i carried
    x = [Integer(f"x_{i}", 0, ub[i], encoding="coupled", vpool=pool)
         for i in range(n_denominations)]
    engine = IntegerEngine(vars=list(x), vpool=pool)

    # The payment of each amount j from 1 up to max_amount, excluded, uses tmp coins of
    # each type. A payment of j uses at most j // d coins of value d.
    impossible = False
    pay = []  # (type i, coins used tmp, most coins of type i that can be used) for every payment
    for j in range(1, max_amount):
        terms = []  # (i, d, coins used, most coins used) for the types that fit under j
        for i, d in enumerate(denominations):
            top = ub[i] if d <= 0 else min(ub[i], j // d)
            if top <= 0:
                continue
            tmp = Integer(f"tmp_{j}_{i}", 0, top, encoding="order", vpool=pool)
            engine.add_var(tmp)
            terms.append((i, d, tmp, top))
        if not terms:
            impossible = True
            continue
        # the coins used add up to exactly j
        engine.add_linear(sum(d * tmp for _, d, tmp, _ in terms) == j)
        pay.extend((i, tmp, top) for i, _, tmp, top in terms)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    if impossible:
        # an amount that no coin type is small enough to pay cannot be paid, so no answer exists
        formula.append([])

    # The coins used in a payment are among the coins carried: for each type, the number
    # used never exceeds the number carried.
    for i, tmp, top in pay:
        for v in range(1, top + 1):
            formula.append([-tmp.ge(v), x[i].ge(v)])

    # At most max_amount coins are carried in all.
    if sum(ub) > max_amount:
        steps = [x[i].ge(v) for i in range(n_denominations) for v in range(1, ub[i] + 1)]
        formula.extend(CardEnc.atmost(lits=steps, bound=max_amount, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Minimise the number of coins: each coin carried costs 1.
    for i in range(n_denominations):
        for v in range(1, ub[i] + 1):
            formula.append([-x[i].ge(v)], weight=1)

    return formula, {"x": x}


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
