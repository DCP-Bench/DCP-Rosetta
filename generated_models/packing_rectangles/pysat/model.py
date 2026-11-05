# packing_rectangles: a PySAT (Python) model from DCP Rosetta.
# Download the `packing_rectangles.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/packing_rectangles.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python packing_rectangles.py packing_rectangles.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Rectangle packing: place rectangles of given widths and heights, without rotating them,
    inside a bounding rectangle so that no two overlap and the bounding rectangle has the
    smallest possible area."""
    widths = instance["widths"]    # widths[i]: the width of item i
    heights = instance["heights"]  # heights[i]: the height of item i
    n = len(widths)                # the number of items

    # The bounding rectangle is at least as wide as the widest item and at most as wide as all
    # items side by side. Its height is bounded the same way.
    area_min_x, area_max_x = max(widths), sum(widths)
    area_min_y, area_max_y = max(heights), sum(heights)
    # Upper bounds for the sides of the bounding rectangle, kept above their lower bounds.
    tx_ub = max(area_max_x, area_min_x + 1)
    ty_ub = max(area_max_y, area_min_y + 1)

    pool = IDPool()

    # pos_x[i] and pos_y[i]: the left and bottom edges of item i, counted from 0
    pos_x = [Integer(f"pos_x{i}", 0, area_max_x, encoding="coupled", vpool=pool)
             for i in range(n)]
    pos_y = [Integer(f"pos_y{i}", 0, area_max_y, encoding="coupled", vpool=pool)
             for i in range(n)]
    # total_x and total_y: the width and the height of the bounding rectangle
    total_x = Integer("total_x", area_min_x, tx_ub, encoding="coupled", vpool=pool)
    total_y = Integer("total_y", area_min_y, ty_ub, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=pos_x + pos_y + [total_x, total_y], vpool=pool)

    # The constraints of the problem.
    formula = WCNF()

    def ge(x, v, lb, ub):
        """Whether x is at least v. Known to be True when v <= lb, and False when v > ub."""
        if v <= lb:
            return True
        if v > ub:
            return False
        return x.ge(v)

    def precedes(cond, a, a_lb, a_ub, size, b, b_lb, b_ub):
        """Clauses making a + size <= b hold whenever cond holds. cond None means always."""
        head = [] if cond is None else [-cond]
        # If a is at least v, then b is at least v + size.
        for v in range(a_lb, a_ub + 1):
            lhs = ge(a, v, a_lb, a_ub)
            if lhs is False:
                continue
            rhs = ge(b, v + size, b_lb, b_ub)
            if rhs is True:
                continue
            clause = list(head)
            if lhs is not True:
                clause.append(-lhs)
            if rhs is not False:
                clause.append(rhs)
            formula.append(clause)

    # The bounding rectangle is no wider and no taller than all items side by side.
    engine.add_linear(total_x <= area_max_x)
    engine.add_linear(total_y <= area_max_y)
    formula.extend(engine.clausify().clauses)

    # Every item lies inside the bounding rectangle.
    for i in range(n):
        precedes(None, pos_x[i], 0, area_max_x, widths[i], total_x, area_min_x, tx_ub)
        precedes(None, pos_y[i], 0, area_max_y, heights[i], total_y, area_min_y, ty_ub)

    # No two items overlap. Each pair has four ways to be apart, each with a flag that
    # implies it; one of the four flags must hold.
    for i in range(n):
        for j in range(i + 1, n):
            left = pool.id(("left", i, j))     # item i lies left of item j
            right = pool.id(("left", j, i))    # item j lies left of item i
            below = pool.id(("below", i, j))   # item i lies below item j
            above = pool.id(("below", j, i))   # item j lies below item i
            formula.append([left, right, below, above])
            precedes(left, pos_x[i], 0, area_max_x, widths[i], pos_x[j], 0, area_max_x)
            precedes(right, pos_x[j], 0, area_max_x, widths[j], pos_x[i], 0, area_max_x)
            precedes(below, pos_y[i], 0, area_max_y, heights[i], pos_y[j], 0, area_max_y)
            precedes(above, pos_y[j], 0, area_max_y, heights[j], pos_y[i], 0, area_max_y)

    # Total area of the items. A bounding rectangle with less area than this cannot hold them.
    item_area = sum(w * h for w, h in zip(widths, heights))
    # Choosing sides W and H costs W * H, the area of the bounding rectangle. Pairs with less
    # area than the items are ruled out.
    for W in range(area_min_x, area_max_x + 1):
        for H in range(area_min_y, area_max_y + 1):
            if W * H < item_area:
                formula.append([-total_x.equals(W), -total_y.equals(H)])
            elif W * H > 0:
                formula.append([-total_x.equals(W), -total_y.equals(H)], weight=W * H)

    # The objective in the problem's terms: the area total_x * total_y (as RC2's cost).
    # sides(W, H) names the choice of sides W and H, and adds W * H when it is made.
    objective = []
    for W in range(area_min_x, area_max_x + 1):
        for H in range(area_min_y, area_max_y + 1):
            if W * H >= item_area and W * H > 0:
                sides = pool.id(("sides", W, H))
                formula.extend([[-sides, total_x.equals(W)], [-sides, total_y.equals(H)],
                                [sides, -total_x.equals(W), -total_y.equals(H)]])
                objective.append((W * H, sides))

    return formula, {"pos_x": pos_x, "pos_y": pos_y,
                     "total_x": total_x, "total_y": total_y}, objective


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
