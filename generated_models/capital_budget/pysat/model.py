# capital_budget: a PySAT (Python) model from DCP Rosetta.
# Download the `capital_budget.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python capital_budget.py capital_budget.json

from math import gcd

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType, PBEnc


def create_model(instance):
    """A company considers a number of investments, each with a net present value (NPV) and a cash
    outflow now. Choose the investments that maximise the total NPV, with the cash outflow of the
    chosen investments within the budget."""
    budget = instance["budget"]        # the total budget available for investment
    npv = instance["npv"]              # npv[i]: the net present value of investment i
    cash_flow = instance["cash_flow"]  # cash_flow[i]: the cash outflow investment i needs now
    n = len(npv)                       # the number of investments

    pool = IDPool()
    formula = WCNF()

    # x[i] is true when investment i is chosen
    x = [pool.id(("x", i)) for i in range(n)]

    # The cash outflow of the chosen investments stays within the budget.
    formula.extend(PBEnc.leq(lits=x, weights=cash_flow, bound=budget, vpool=pool).clauses)

    # The common divisor of the NPVs (1 when they are all zero). Every total NPV is a multiple of it,
    # so the total is counted in units of it.
    unit = 0
    for v in npv:
        unit = gcd(unit, v)
    unit = unit or 1
    # steps[i]: the NPV of investment i in units
    steps = [v // unit for v in npv]
    top = sum(steps)  # the largest total NPV in units

    # units is the total NPV of the chosen investments, in units.
    units = Integer("npv_units", 0, max(top, 1), encoding="coupled", vpool=pool)
    formula.extend(units.domain_clauses())
    # order[k - 1] is true when units is at least k. Counting these thresholds gives units.
    order = [units.ge(k) for k in range(1, max(top, 1) + 1)]
    # units is the sum of the steps of the chosen investments.
    formula.extend(PBEnc.equals(lits=x + order,
                                weights=steps + [-1] * len(order), bound=0,
                                vpool=pool, encoding=EncType.bdd).clauses)

    # z is the total NPV, which is unit times units. Its values that are not a multiple of unit are
    # ruled out, and the others agree with units.
    z = Integer("z", 0, unit * max(top, 1), vpool=pool)
    for v in range(0, unit * max(top, 1) + 1):
        if v % unit == 0:
            formula.append([-z.equals(v), units.equals(v // unit)])
            formula.append([z.equals(v), -units.equals(v // unit)])
        else:
            formula.append([-z.equals(v)])

    # Leaving an investment out costs its NPV, so the chosen investments have the largest total NPV.
    for i in range(n):
        if npv[i] > 0:
            formula.append([x[i]], weight=npv[i])

    # The objective in the problem's terms: the total NPV of the chosen investments (RC2's
    # cost is the NPV left out).
    return formula, {"x": x, "z": z}, z


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
        # an Integer decodes its value from the model, a literal is true when it is in the model
        value = np.vectorize(lambda v: v.decode(model) if isinstance(v, Integer) else v in model)
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")
