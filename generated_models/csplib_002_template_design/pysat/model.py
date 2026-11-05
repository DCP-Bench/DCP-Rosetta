# csplib_002_template_design: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_002_template_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_002_template_design.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_002_template_design.py csplib_002_template_design.json

from math import isqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import EncType, PBEnc


def create_model(instance):
    """Template design: choose which variations each template holds and how many sheets
    to print from it, so that every variation reaches its demand with as few printed
    sheets as possible."""
    n_slots = instance["n_slots"]          # the number of slots on each template
    n_templates = instance["n_templates"]  # the number of templates
    n_var = instance["n_var"]              # the number of variations
    demand = instance["demand"]            # demand[v]: the number of copies of variation v wanted

    templates = range(n_templates)  # template numbers, from 0
    variations = range(n_var)       # variation numbers, from 0

    # lower: each sheet carries n_slots copies, so the demand needs at least
    # sum(demand) / n_slots sheets, and each template is printed at least once.
    lower = max(-(-sum(demand) // n_slots), n_templates)
    # upper: n_templates * max(demand) sheets at most.
    upper = n_templates * max(demand)
    # A plan that gives one slot to each variation, then gives each further slot to the
    # variation needing the most sheets per copy, with no variation above n_var slots.
    # Printing that template sheets times and each other template once takes
    # sheets + n_templates - 1 sheets.
    if n_var <= n_slots <= n_var * n_var:
        copies = [1] * n_var  # copies[v]: the slots the plan gives variation v
        for _ in range(n_slots - n_var):
            v = max(variations, key=lambda v: (-(-demand[v] // copies[v])
                                               if copies[v] < n_var else -1))
            copies[v] += 1
        sheets = max([1] + [-(-demand[v] // copies[v]) for v in variations])
        if sheets <= max(demand):
            upper = min(upper, sheets + n_templates - 1)
    lower = min(lower, upper)
    # p_max: the most sheets printed from one template, leaving every other template
    # at least one sheet, and never more than the largest demand.
    p_max = max(min(max(demand), upper - (n_templates - 1)), 1)

    pool = IDPool()
    # production[t]: the number of sheets printed from template t
    production = [Integer(f"production{t}", 1, p_max, vpool=pool) for t in templates]
    # layout[t][v]: the number of slots of template t that hold variation v
    layout = [[Integer(f"layout_{t}_{v}", 0, n_var, vpool=pool) for v in variations]
              for t in templates]
    engine = IntegerEngine(vars=production + [x for row in layout for x in row], vpool=pool)

    # Every slot of every template holds a variation.
    for t in templates:
        engine.add_linear(sum(layout[t]) == n_slots)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # bits[k] is true exactly when bit k of x is 1, for every value x takes from lo to hi.
    def digits(x, lo, hi, name):
        n = max(hi, 1).bit_length()
        bits = [pool.id((name, k)) for k in range(n)]
        for val in range(lo, hi + 1):
            for k in range(n):
                formula.append([-x.equals(val), bits[k] if (val >> k) & 1 else -bits[k]])
        return bits

    prod_bits = [digits(production[t], 1, p_max, ("production bit", t)) for t in templates]
    layout_bits = [[digits(layout[t][v], 0, n_var, ("layout bit", t, v))
                    for v in variations] for t in templates]

    # pair[t][v][b][c] is true exactly when bit b of the sheets printed from template t and
    # bit c of the copies of variation v on that template are both 1. Such a pair is worth
    # 2^(b+c) copies, so the sheets times the copies is the sum of the pairs.
    # coverage[v]: the pairs for variation v and their worth
    coverage = []
    for v in variations:
        lits, weights = [], []
        for t in templates:
            for b, pb in enumerate(prod_bits[t]):
                for c, lb in enumerate(layout_bits[t][v]):
                    pair = pool.id(("pair", t, v, b, c))
                    formula.append([-pair, pb])
                    formula.append([-pair, lb])
                    formula.append([pair, -pb, -lb])
                    lits.append(pair)
                    weights.append(1 << (b + c))
        # The copies of variation v, over all templates, reach its demand.
        formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=demand[v], vpool=pool,
                                 encoding=EncType.bdd).clauses)
        coverage.append((lits, weights))

    # Implied: every template fills all its slots, so the sheets together carry at least
    # the total demand.
    formula.extend(PBEnc.geq(lits=[pb for t in templates for pb in prod_bits[t]],
                             weights=[n_slots << b for t in templates
                                      for b in range(len(prod_bits[t]))],
                             bound=sum(demand), vpool=pool, encoding=EncType.adder).clauses)

    # total: the number of sheets printed, between lower and upper. It is at least the
    # sheets printed from all the templates together.
    total = Integer("total", lower, upper, encoding="order", vpool=pool)
    formula.extend(IntegerEngine(vars=[total], vpool=pool).clausify().clauses)
    thresholds = [total.ge(v) for v in range(lower + 1, upper + 1)]
    formula.extend(PBEnc.leq(lits=[pb for t in templates for pb in prod_bits[t]] + thresholds,
                             weights=[1 << b for t in templates
                                      for b in range(len(prod_bits[t]))]
                             + [-1] * len(thresholds),
                             bound=lower, vpool=pool, encoding=EncType.adder).clauses)

    # Copies of variation v are at most n_slots * total less the demand of the other
    # variations, since every sheet carries n_slots copies. Only when that bound is not
    # negative.
    for v in variations:
        lits, weights = coverage[v]
        rest = n_slots * lower - (sum(demand) - demand[v])
        if rest >= 0:
            formula.extend(PBEnc.leq(lits=lits + thresholds,
                                     weights=weights + [-n_slots] * len(thresholds),
                                     bound=rest, vpool=pool, encoding=EncType.adder).clauses)

    # group: the number of sheet counts that share one weight, about the square root of
    # the range of sheet counts.
    group = isqrt(max(upper - lower, 1)) + 1
    # Reaching total >= v costs a weight that rises by one every group sheets, so the cost
    # of a plan rises with the sheets it prints and the cheapest plan prints the fewest.
    for v in range(lower + 1, upper + 1):
        formula.append([-total.ge(v)], weight=1 + (v - lower - 1) // group)

    # The objective in the problem's terms: the number of sheets printed, over all templates
    # (RC2's cost is a grouped weight on total, which bounds it from above).
    objective = [(1, production[t]) for t in templates]

    return formula, {"production": production, "layout": layout}, objective


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
