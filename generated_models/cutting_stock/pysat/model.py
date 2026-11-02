# cutting_stock: a PySAT (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python cutting_stock.py cutting_stock.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths, following
    cutting patterns that each yield a given number of rolls of each width. Each
    width has a number of orders that must be met. Decide how many times each
    pattern is used so that the total number of raw rolls cut is as small as
    possible."""
    widths = instance["widths"]                    # widths[w]: the width of the rolls of kind w
    orders = instance["orders"]                    # orders[w]: the number of rolls of width w that must be cut
    n_patterns = instance["num_patterns"]          # the number of cutting patterns
    num_rolls_width = instance["num_rolls_width"]  # num_rolls_width[p][w]: rolls of width w that one raw roll gives with pattern p
    n_widths = len(orders)                         # the number of widths

    # ub[p]: the most raw rolls cut with pattern p in an optimal plan, capped at 100.
    # Dropping one raw roll cut with p must leave some ordered width short, so p is used no
    # more often than that width needs. A pattern that makes no roll of any width is never used.
    ub = []
    for p in range(n_patterns):
        reach = [-(-max(orders[w], 0) // num_rolls_width[p][w])
                 for w in range(n_widths) if num_rolls_width[p][w] > 0]
        ub.append(min(100, max(reach)) if reach else 0)

    pool = IDPool()
    # patterns_used[p]: the number of raw rolls cut with pattern p
    patterns_used = [Integer(f"patterns_used{p}", 0, max(ub[p], 1), encoding="coupled", vpool=pool)
                     for p in range(n_patterns)]
    # min_rolls_cut: the total number of raw rolls cut
    total_ub = sum(ub)
    min_rolls_cut = Integer("min_rolls_cut", 0, max(total_ub, 1), encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=patterns_used + [min_rolls_cut], vpool=pool)
    # A pattern that is never used is fixed to zero rolls.
    for p in range(n_patterns):
        if ub[p] == 0:
            engine.add_linear(patterns_used[p] <= 0)

    # For each width, the rolls cut with all patterns are at least its order.
    unmet = False
    for w in range(n_widths):
        terms = [num_rolls_width[p][w] * patterns_used[p]
                 for p in range(n_patterns) if num_rolls_width[p][w] != 0]
        if terms:
            engine.add_linear(sum(terms) >= orders[w])
        elif orders[w] > 0:
            # no pattern produces this width, so the order cannot be met
            unmet = True

    # The total number of raw rolls cut is the sum over the patterns.
    engine.add_linear(min_rolls_cut - sum(patterns_used) == 0)

    # Lower bounds on the rolls cut, stated up front. A width alone needs at least its order
    # divided by the most rolls of that width one raw roll gives, rounded up. Together the
    # orders need at least their total length divided by the most length one raw roll gives.
    lower = 0  # the fewest raw rolls the bounds so far allow
    for w in range(n_widths):
        most_pieces = max(num_rolls_width[p][w] for p in range(n_patterns))
        if orders[w] > 0 and most_pieces > 0:
            lower = max(lower, -(-orders[w] // most_pieces))
    most_length = max(sum(num_rolls_width[p][w] * widths[w] for w in range(n_widths))
                      for p in range(n_patterns))
    if most_length > 0 and min(widths) > 0:
        ordered_length = sum(max(orders[w], 0) * widths[w] for w in range(n_widths))
        lower = max(lower, -(-ordered_length // most_length))
    lower = min(lower, total_ub)
    engine.add_linear(min_rolls_cut >= lower)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    if unmet:
        # An unmet order leaves no plan: this forces a contradiction.
        contradiction = pool.id("unmet order")
        formula.append([contradiction])
        formula.append([-contradiction])

    # Each raw roll cut above the lower bound costs 1, so the cost is the number of raw
    # rolls cut.
    for v in range(lower + 1, total_ub + 1):
        formula.append([-min_rolls_cut.ge(v)], weight=1)

    return formula, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}


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
